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
