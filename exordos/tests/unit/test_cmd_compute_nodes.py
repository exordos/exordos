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
import json
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


def _invoke_info(details: dict, extra_args=()):
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "get_entity", return_value=NODE),
        mock.patch.object(commands.base_client, "action_entity", return_value=details),
    ):
        return CliRunner().invoke(
            commands.info_cmd,
            [NODE["name"], *extra_args],
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


def _invoke_update(command, extra_args: list[str]):
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "get_entity", return_value=NODE),
        mock.patch.object(
            commands.base_client, "update_entity", return_value=NODE
        ) as update_entity,
    ):
        result = CliRunner().invoke(
            command,
            ["-u", NODE["uuid"], *extra_args],
            obj=SimpleNamespace(auth_data={}),
        )
    return result, update_entity


def test_update_cmd_sets_hostname() -> None:
    result, update_entity = _invoke_update(
        commands.update_cmd, ["--hostname", "node-1"]
    )

    assert result.exit_code == 0, result.output
    data = update_entity.call_args.args[3]
    assert data["hostname"] == "node-1"


def test_update_cmd_omits_hostname_when_not_provided() -> None:
    result, update_entity = _invoke_update(commands.update_cmd, ["--cores", "2"])

    assert result.exit_code == 0, result.output
    data = update_entity.call_args.args[3]
    assert "hostname" not in data


@pytest.mark.parametrize("hostname", ["bad_host", "node-", "bad host", "a" * 64])
def test_update_cmd_rejects_invalid_hostname(hostname: str) -> None:
    result, update_entity = _invoke_update(
        commands.update_cmd, ["--hostname", hostname]
    )

    assert result.exit_code != 0
    assert "Invalid hostname" in result.output
    update_entity.assert_not_called()


def test_update_cmd_rejects_invalid_hostname_before_api_lookup() -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client") as get_client,
        mock.patch.object(commands.base_client, "get_entity") as get_entity,
    ):
        result = CliRunner().invoke(
            commands.update_cmd,
            ["-u", NODE["uuid"], "--hostname", "bad_host"],
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code != 0
    assert "Invalid hostname" in result.output
    get_client.assert_not_called()
    get_entity.assert_not_called()


def test_add_or_update_cmd_rejects_invalid_hostname_on_update() -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client, "get_entity", return_value=NODE
        ) as get_entity,
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
    get_entity.assert_not_called()


@pytest.mark.parametrize("output", ["json", "JSON"])
def test_add_cmd_json_preserves_resource(output):
    result, _ = _invoke_add(commands.add_cmd, ["--output", output])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == NODE


def test_add_cmd_json_wait_prints_only_final_resource():
    pending = {**NODE, "status": "BUILD", "cores": 2, "default_network": None}
    active = {**pending, "status": "ACTIVE", "default_network": {"ipv4": "192.0.2.1"}}
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "add_entity", return_value=pending),
        mock.patch.object(
            commands.base_client, "get_entity", side_effect=[pending, active]
        ),
        mock.patch.object(commands.time, "sleep"),
    ):
        result = CliRunner().invoke(
            commands.add_cmd,
            ["--project-id", PROJECT_ID, "--image", "ubuntu", "--wait", "-o", "json"],
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == active
    assert result.stderr.count("Waiting for node") == 2


@pytest.mark.parametrize("command", ["show", "get", "g"])
@pytest.mark.parametrize("identifier", [NODE["uuid"], NODE["name"]])
def test_show_cmd_json_gets_only_node(command, identifier):
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "get_entity", return_value=NODE) as get,
        mock.patch.object(commands.base_client, "action_entity") as action,
    ):
        result = CliRunner().invoke(
            commands.cn_group,
            [command, identifier, "-o", "json"],
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == NODE
    assert get.call_args.args[2] == identifier
    action.assert_not_called()


@pytest.mark.parametrize(
    "args",
    [
        ["compute", "cn", "get", NODE["name"]],
        ["compute", "cn", "add", "--project-id", PROJECT_ID, "--image", "ubuntu"],
        [
            "dns",
            "records",
            "add",
            "--project-id",
            PROJECT_ID,
            "--domain-uuid",
            PROJECT_ID,
            "--record-type",
            "A",
            "--record",
            "address=192.0.2.1",
        ],
    ],
)
def test_json_output_root_diagnostics_use_stderr(tmp_path, args):
    from exordos.cmd.cli import exordos
    from exordos.cmd.version import commands as version_commands

    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "get_entity", return_value=NODE),
        mock.patch.object(commands.base_client, "add_entity", return_value=NODE),
        mock.patch.object(version_commands, "should_check_version", return_value=True),
        mock.patch.object(version_commands, "save_last_check_time"),
        mock.patch.object(
            version_commands.requests, "get", side_effect=ValueError("offline")
        ),
    ):
        result = CliRunner().invoke(
            exordos,
            [
                "--config",
                str(tmp_path / "missing.yaml"),
                "--check-updates",
                *args,
                "-o",
                "json",
            ],
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == NODE
    assert "configuration file" in result.stderr
    assert "Failed to check" in result.stderr


@pytest.mark.parametrize("module", ["elements", "manifests"])
def test_show_cmd_em_json_prints_only_resource(module):
    from importlib import import_module

    cmd = import_module(f"exordos.cmd.em.{module}.commands")
    entity = {**NODE, "resources": {"nested": [True, None, 3]}}
    with (
        mock.patch.object(cmd.base_client, "get_user_api_client"),
        mock.patch.object(cmd.base_client, "get_entity", return_value=entity),
        mock.patch.object(cmd.base_client, "list_entities") as listing,
    ):
        result = CliRunner().invoke(
            cmd.show_cmd,
            [NODE["uuid"], "-o", "json"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == entity
    listing.assert_not_called()


def test_show_cmd_json_rejects_ambiguous_lookup():
    from exordos.cmd.base import create_entity_group

    group = create_entity_group("resource", "/resources/", {}, lookup_field="uuid")
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client, "list_entities", return_value=[NODE, NODE]
        ),
    ):
        result = CliRunner().invoke(
            group,
            ["show", NODE["uuid"], "-o", "json"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code != 0
    assert result.stdout == ""
    assert "Multiple resources" in result.stderr


def test_info_cmd_json_keeps_legacy_field_value_rows():
    result = _invoke_info({}, ["--output", "json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [
        {"field": key, "value": str(value)} for key, value in NODE.items()
    ]
