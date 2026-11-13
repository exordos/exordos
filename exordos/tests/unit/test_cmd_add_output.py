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
from contextlib import ExitStack
import json
from types import SimpleNamespace
from unittest import mock

import click
from click.testing import CliRunner
import pytest

from exordos.clients import base_client
from exordos.cmd.cli import exordos

UUID = "11111111-1111-1111-1111-111111111111"
ENTITY = {
    "uuid": UUID,
    "name": "resource",
    "project_id": UUID,
    "count": 2,
    "enabled": False,
    "parent": None,
    "spec": {"values": [1, True, None]},
}


def _commands(names):
    seen = set()

    def visit(command):
        if id(command) in seen:
            return
        seen.add(id(command))
        if (
            command.name in names
            and command.callback.__module__ != "exordos.cmd.em.elements.commands"
        ):
            yield command
        for child in getattr(command, "commands", {}).values():
            yield from visit(child)

    return list(visit(exordos))


def _arguments(command):
    overrides = {
        "callback": "{}",
        "content": "{}",
        "condition": "{}",
        "password": "password",
        "admin_password": "password",
        "driver_spec": "kind=libvirt",
        "node": UUID,
    }
    if command.name in ("update", "add-or-update"):
        overrides.update(
            name="updated", description="updated", resource_name="compute.nodes"
        )
    if command.callback.__module__ == "exordos.cmd.security.commands":
        overrides["condition"] = "kind=uri_regex"
    if command.callback.__module__ == "exordos.cmd.dbaas.instances.commands":
        overrides["version"] = UUID
    if command.callback.__module__ in (
        "exordos.cmd.metapaas.mail.instances.commands",
        "exordos.cmd.metapaas.s3.instances.commands",
    ):
        overrides["version"] = UUID
    args = []
    for param in command.params:
        if param.name == "output" or param.name == "help":
            continue
        if not param.required and param.name not in overrides:
            continue
        if getattr(param, "is_flag", False):
            if param.required:
                args.append(param.opts[0])
            continue
        value = overrides.get(param.name)
        if value is None:
            if isinstance(param.type, click.Choice):
                value = param.type.choices[0]
            elif isinstance(param.type, click.IntRange):
                value = str(max(1, param.type.min or 1))
            elif isinstance(param.type, click.types.IntParamType):
                value = "1"
            elif isinstance(param.type, click.types.FloatParamType):
                value = "1.0"
            else:
                value = UUID
        if isinstance(param, click.Option):
            args.extend([param.opts[0], str(value)])
        else:
            args.append(str(value))
    return args


@pytest.mark.parametrize(
    "command", _commands({"add"}), ids=lambda cmd: cmd.callback.__module__
)
def test_add_cmd_json_returns_native_resource(command):
    module = command.callback.__module__
    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(base_client, "get_user_api_client"))
        stack.enter_context(
            mock.patch.object(base_client, "get_entity", return_value=ENTITY)
        )
        stack.enter_context(
            mock.patch.object(base_client, "add_entity", return_value=ENTITY)
        )
        if module == "exordos.cmd.realms.commands":
            stack.enter_context(mock.patch(f"{module}.get_ecosystem_client"))
        if module == "exordos.cmd.settings.commands":
            stack.enter_context(mock.patch(f"{module}.save_config"))
        result = CliRunner().invoke(
            command,
            [*_arguments(command), "--output", "json"],
            obj=SimpleNamespace(auth_data={}, cfg={}, cfg_path=None),
        )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    if module == "exordos.cmd.secret.ssh_keys.commands":
        assert payload == [ENTITY]
    elif module == "exordos.cmd.settings.commands":
        assert payload == {"driver": UUID, "url": UUID}
    else:
        assert payload == ENTITY


@pytest.mark.parametrize(
    "command",
    _commands({"update", "add-or-update"}),
    ids=lambda cmd: cmd.callback.__module__ + "." + cmd.name,
)
def test_update_cmd_json_returns_native_resource(command):
    with (
        mock.patch.object(base_client, "get_user_api_client"),
        mock.patch.object(base_client, "get_entity", return_value=ENTITY),
        mock.patch.object(base_client, "update_entity", return_value=ENTITY),
        mock.patch.object(base_client, "add_entity", return_value=ENTITY),
    ):
        result = CliRunner().invoke(
            command,
            [*_arguments(command), "--output", "json"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == ENTITY
