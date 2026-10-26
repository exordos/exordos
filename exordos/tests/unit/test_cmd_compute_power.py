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

from exordos import constants as c
from exordos.cmd.compute import common
from exordos.cmd.compute.nodes import commands as node_commands
from exordos.cmd.compute.sets import commands as set_commands

ENTITY = {
    "uuid": "a370f746-6f28-4a55-8844-a027b77f09e6",
    "name": "ecosystem-cp",
    "status": "IN_PROGRESS",
}


@pytest.mark.parametrize(
    "group,collection",
    [
        (node_commands.cn_group, c.NODE_COLLECTION),
        (set_commands.sets_group, c.SET_COLLECTION),
    ],
)
@pytest.mark.parametrize(
    "command,action",
    [("power-on", "power_on"), ("power-off", "power_off"), ("reboot", "reboot")],
)
def test_power_cmd_invokes_action(group, collection, command, action) -> None:
    with (
        mock.patch.object(common.base_client, "get_user_api_client") as get_client,
        mock.patch.object(
            common.base_client, "get_entity", return_value=ENTITY
        ) as get_entity,
        mock.patch.object(
            common.base_client, "action_entity", return_value=ENTITY
        ) as action_entity,
    ):
        result = CliRunner().invoke(
            group,
            [command, ENTITY["name"]],
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code == 0, result.output
    client = get_client.return_value
    get_entity.assert_called_once_with(client, collection, ENTITY["name"])
    action_entity.assert_called_once_with(client, collection, action, ENTITY["uuid"])
    assert ENTITY["uuid"] in result.output
