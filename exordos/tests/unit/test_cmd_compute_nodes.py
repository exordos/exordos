#    Copyright 2026 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from types import SimpleNamespace
from unittest import mock

from click.testing import CliRunner
import pytest

from exordos.cmd.compute.nodes import commands

NODE = {"uuid": "a370f746-6f28-4a55-8844-a027b77f09e6", "name": "ecosystem-cp"}
HYPERVISOR_UUID = "0c1d2e3f-0000-4000-8000-000000000001"
PROJECT_ID = "6a1d2e3f-0000-4000-8000-000000000002"


def _invoke_add(command, extra_args: list[str]):
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client, "add_entity", return_value=NODE
        ) as add_entity,
    ):
        result = CliRunner().invoke(
            command,
            ["--project-id", PROJECT_ID, "--image", "ubuntu", *extra_args],
            obj=SimpleNamespace(auth_data={}),
        )
    return result, add_entity


def _invoke_info(details: dict):
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "get_entity", return_value=NODE),
        mock.patch.object(commands.base_client, "action_entity", return_value=details),
    ):
        return CliRunner().invoke(
            commands.info_cmd,
            [NODE["name"]],
            obj=SimpleNamespace(auth_data={}),
        )


def test_info_cmd_shows_hypervisor_uuid() -> None:
    result = _invoke_info({"hypervisor": HYPERVISOR_UUID})

    assert result.exit_code == 0, result.output
    assert "Hypervisor" in result.output
    assert HYPERVISOR_UUID in result.output


@pytest.mark.parametrize("details", [{"hypervisor": None}, {}])
def test_info_cmd_node_not_placed(details: dict) -> None:
    result = _invoke_info(details)

    assert result.exit_code == 0, result.output
    assert NODE["name"] in result.output
    assert "Hypervisor" not in result.output


def test_add_cmd_sets_hostname() -> None:
    result, add_entity = _invoke_add(commands.add_cmd, ["--hostname", "node-1"])

    assert result.exit_code == 0, result.output
    data = add_entity.call_args.args[2]
    assert data["hostname"] == "node-1"


def test_add_cmd_omits_hostname_when_not_provided() -> None:
    result, add_entity = _invoke_add(commands.add_cmd, [])

    assert result.exit_code == 0, result.output
    data = add_entity.call_args.args[2]
    assert "hostname" not in data


def test_add_or_update_cmd_sets_hostname() -> None:
    result, add_entity = _invoke_add(
        commands.add_or_update_node_cmd, ["--hostname", "node-1"]
    )

    assert result.exit_code == 0, result.output
    data = add_entity.call_args.args[2]
    assert data["hostname"] == "node-1"


@pytest.mark.parametrize("hostname", ["bad_host", "node-", "bad host", "a" * 64])
def test_add_cmd_rejects_invalid_hostname(hostname: str) -> None:
    result, add_entity = _invoke_add(commands.add_cmd, ["--hostname", hostname])

    assert result.exit_code != 0
    assert "Invalid hostname" in result.output
    add_entity.assert_not_called()


def test_add_or_update_cmd_rejects_invalid_hostname_on_update() -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "get_entity", return_value=NODE),
        mock.patch.object(commands.base_client, "update_entity") as update_entity,
    ):
        result = CliRunner().invoke(
            commands.add_or_update_node_cmd,
            [
                "--uuid",
                NODE["uuid"],
                "--project-id",
                PROJECT_ID,
                "--image",
                "ubuntu",
                "--hostname",
                "bad_host",
            ],
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code != 0
    assert "Invalid hostname" in result.output
    update_entity.assert_not_called()
