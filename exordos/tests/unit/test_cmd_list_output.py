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
import uuid as sys_uuid

from click.testing import CliRunner
import pytest

from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.cli import exordos
from exordos.cmd.iam.permission import commands as permission_commands
from exordos.cmd.repo.store import commands as store_commands
from exordos.common import table

UUID = "11111111-1111-1111-1111-111111111111"
ENTITY = {
    "uuid": UUID,
    "name": "узел",
    "version": "1.2.3",
    "status": "ACTIVE",
    "cores": 2,
    "enabled": False,
    "parent": None,
    "default_network": {"ipv4": "192.0.2.1"},
    "values": [1, True, None],
    "iam_client": "/v1/iam/clients/" + UUID,
}


def _list_commands():
    seen = set()

    def visit(command):
        if id(command) in seen:
            return
        seen.add(id(command))
        if command.name == "list" and command.callback.__module__ == "exordos.cmd.base":
            yield command
        for child in getattr(command, "commands", {}).values():
            yield from visit(child)

    return list(visit(exordos))


@pytest.mark.parametrize("command", _list_commands(), ids=lambda cmd: cmd.help)
@pytest.mark.parametrize("entities", [[], [ENTITY]])
def test_list_cmd_json_preserves_resources(command, entities):
    args = ["-o", "json"]
    for param in command.params:
        if param.required:
            args.extend([param.opts[0], UUID])
    with (
        mock.patch.object(base_client, "get_user_api_client"),
        mock.patch.object(base_client, "list_entities", return_value=entities),
    ):
        result = CliRunner().invoke(command, args, obj=SimpleNamespace(auth_data={}))
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == entities


@pytest.mark.parametrize("output", ["json", "JSON"])
def test_list_cmd_json_preserves_filters_fields_and_post_fetch(output):
    post_fetch = mock.Mock(
        side_effect=lambda entities, kwargs: list(reversed(entities))
    )
    group = create_entity_group(
        "node",
        "/parents/{parent_uuid}/nodes/",
        {"UUID": "uuid", "IP": lambda row: "computed"},
        parents=["parent"],
        post_fetch_handler=post_fetch,
    )
    entities = [ENTITY, {**ENTITY, "name": "second"}]
    with (
        mock.patch.object(base_client, "get_user_api_client"),
        mock.patch.object(
            base_client, "list_entities", return_value=entities
        ) as listing,
    ):
        result = CliRunner().invoke(
            group,
            [
                "list",
                "--parent-uuid",
                UUID,
                "-f",
                "status=ACTIVE",
                "--fields",
                "uuid",
                "--fields",
                "default_network",
                "-o",
                output,
            ],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == list(reversed(entities))
    assert (
        listing.call_args.args[1]
        == f"/parents/{UUID}/nodes/?fields=uuid&fields=default_network"
    )
    assert listing.call_args.kwargs == {"status": "ACTIVE"}
    post_fetch.assert_called_once_with(entities, {"parent_uuid": sys_uuid.UUID(UUID)})


def test_list_cmd_json_rejects_watch_before_api_call():
    group = create_entity_group("node", "/nodes/", {})
    with mock.patch.object(base_client, "get_user_api_client") as client:
        result = CliRunner().invoke(
            group, ["list", "--watch", "-o", "json"], obj=SimpleNamespace(auth_data={})
        )
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "--watch cannot be combined" in result.stderr
    client.assert_not_called()


@pytest.mark.parametrize("entities", [[], [ENTITY]])
def test_latest_stable_elements_cmd_json_preserves_resources(entities):
    with (
        mock.patch.object(base_client, "get_user_api_client"),
        mock.patch.object(base_client, "list_entities", return_value=entities),
    ):
        result = CliRunner().invoke(
            store_commands.latest_stable_elements_cmd,
            ["-o", "json"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == entities


def test_by_role_cmd_json_preserves_permissions():
    with (
        mock.patch.object(base_client, "get_user_api_client"),
        mock.patch.object(base_client, "get_entity", return_value=ENTITY),
        mock.patch.object(
            base_client,
            "list_entities",
            return_value=[{"permission": "/permissions/" + UUID}],
        ),
    ):
        result = CliRunner().invoke(
            permission_commands.by_role_cmd,
            [UUID, "-o", "json"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [ENTITY]


@pytest.mark.parametrize("output", ["table", "yaml", "html"])
def test_show_resources_keeps_existing_formats(output, capsys):
    table.show_resources([{"name": "node", "cores": 2}], {"Name": "name"}, output)
    actual = capsys.readouterr().out
    table.print_table(
        table.fill_table([{"name": "node", "cores": 2}], {"Name": "name"}), output
    )
    assert capsys.readouterr().out == actual
