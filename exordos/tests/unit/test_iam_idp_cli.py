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
from __future__ import annotations

import json
from unittest import mock

from click.testing import CliRunner
import pytest

from exordos.cmd.iam import iam_group
from exordos.cmd.iam.idp import commands
from exordos.common.cmd_context import ContextObject


def _ctx() -> ContextObject:
    return ContextObject(
        auth_data={},
        cfg_path=None,
        developer_key_path=None,
        cfg={},
        need_update=None,
    )


def test_well_known_cmd_prints_openid_configuration() -> None:
    idp = "00000000-0000-0000-0000-000000000001"
    config = {"issuer": "https://example.com", "scopes_supported": ["openid"]}

    with mock.patch.object(commands, "base_client") as base_client:
        client = base_client.get_user_api_client.return_value
        base_client._get_entity_uuid.return_value = idp
        client.get.return_value = config

        result = CliRunner().invoke(iam_group, ["i", "well-known", idp], obj=_ctx())

    assert result.exit_code == 0, result.exception
    base_client._get_entity_uuid.assert_called_once_with(
        client, commands.ENTITY_COLLECTION, idp
    )
    client.get.assert_called_once_with(
        f"/v1/iam/idp/{idp}/.well-known/", "openid-configuration"
    )
    assert json.loads(result.output) == config


@pytest.mark.parametrize(
    ("flag", "expected"),
    [
        (None, True),
        ("--nonce-required", True),
        ("--nonce_required", True),
        ("--no-nonce-required", False),
    ],
)
def test_add_cmd_nonce_required(flag: str | None, expected: bool) -> None:
    args = [
        "i",
        "add",
        "-p",
        "00000000-0000-0000-0000-0000000000aa",
        "-i",
        "00000000-0000-0000-0000-0000000000bb",
        "--callback",
        "{}",
    ]
    if flag is not None:
        args.append(flag)

    with mock.patch.object(commands, "base_client") as base_client:
        base_client.add_entity.return_value = {}
        result = CliRunner().invoke(iam_group, args, obj=_ctx())

    assert result.exit_code == 0, result.output
    data = base_client.add_entity.call_args.args[2]
    assert data["nonce_required"] is expected


def test_list_cmd_shows_project_and_client_uuid() -> None:
    project = "00000000-0000-0000-0000-0000000000aa"
    iam_client = "00000000-0000-0000-0000-0000000000bb"
    idp = {
        "uuid": "00000000-0000-0000-0000-000000000001",
        "name": "my-idp",
        "project_id": project,
        "scope": "openid",
        "iam_client": f"/v1/iam/clients/{iam_client}",
        "status": "ACTIVE",
    }

    with (
        mock.patch("exordos.cmd.base.base_client.list_entities", return_value=[idp]),
        mock.patch("exordos.cmd.base.base_client.get_user_api_client"),
    ):
        result = CliRunner().invoke(iam_group, ["i", "list", "-o", "json"], obj=_ctx())

    assert result.exit_code == 0, result.exception
    assert project in result.output
    assert iam_client in result.output
    assert "/v1/iam/clients/" not in result.output


def test_update_cmd_sends_only_given_fields() -> None:
    idp = "00000000-0000-0000-0000-000000000001"
    iam_client = "00000000-0000-0000-0000-0000000000bb"
    args = [
        "i",
        "update",
        idp,
        "-n",
        "new-name",
        "-i",
        iam_client,
        "--no-nonce-required",
        "--callback",
        '{"kind": "uri", "uri": "https://example.com/cb"}',
    ]

    with mock.patch.object(commands, "base_client") as base_client:
        base_client.update_entity.return_value = {"uuid": idp}
        result = CliRunner().invoke(iam_group, args, obj=_ctx())

    assert result.exit_code == 0, result.exception
    base_client.update_entity.assert_called_once_with(
        base_client.get_user_api_client.return_value,
        commands.ENTITY_COLLECTION,
        idp,
        {
            "name": "new-name",
            "iam_client": f"/v1/iam/clients/{iam_client}",
            "nonce_required": False,
            "callback": {"kind": "uri", "uri": "https://example.com/cb"},
        },
    )


def test_update_cmd_invalid_callback() -> None:
    with mock.patch.object(commands, "base_client") as base_client:
        result = CliRunner().invoke(
            iam_group, ["i", "u", "my-idp", "--callback", "{bad"], obj=_ctx()
        )

    assert result.exit_code != 0
    assert "Invalid JSON string" in result.output
    base_client.update_entity.assert_not_called()


def test_well_known_cmd_alias() -> None:
    with mock.patch.object(commands, "base_client") as base_client:
        base_client._get_entity_uuid.return_value = "idp-uuid"
        base_client.get_user_api_client.return_value.get.return_value = {}

        result = CliRunner().invoke(iam_group, ["i", "wk", "my-idp"], obj=_ctx())

    assert result.exit_code == 0, result.exception
