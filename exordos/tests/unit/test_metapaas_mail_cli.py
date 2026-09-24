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

import typing as tp
from unittest import mock

from click.testing import CliRunner

from exordos.cmd import metapaas
from exordos.common.cmd_context import ContextObject

INSTANCE_UUID = "11111111-1111-1111-1111-111111111111"
PROJECT_ID = "44444444-4444-4444-4444-444444444444"
VERSION_UUID = "55555555-5555-5555-5555-555555555555"


def _run(*args: str, lookup: dict | None = None) -> tuple[tp.Any, mock.MagicMock]:
    """Invoke a mail command with the API client calls mocked out."""
    with (
        mock.patch("exordos.clients.base_client.get_user_api_client"),
        mock.patch("exordos.clients.base_client.get_entity", return_value=lookup or {}),
        mock.patch(
            "exordos.clients.base_client.add_entity", return_value={}
        ) as add_entity,
    ):
        result = CliRunner().invoke(
            metapaas.metapaas_group,
            ["mail", *args],
            obj=ContextObject(
                auth_data={"endpoint": "http://10.20.0.2/api/core"},
                cfg_path=None,
                developer_key_path=None,
                cfg={},
                need_update=None,
            ),
        )
    return result, add_entity


class TestMailInstances:
    def test_add_cmd_resolves_version_and_builds_payload(self) -> None:
        result, add_entity = _run(
            "instances",
            "add",
            "-p",
            PROJECT_ID,
            "-n",
            "corp",
            "-d",
            "example.org",
            "-v",
            "exim-2025",
            "--cpu",
            "2",
            "--ram",
            "2048",
            "--disk-size",
            "20",
            lookup={"uuid": VERSION_UUID},
        )
        assert result.exit_code == 0, result.output
        _, collection, data = add_entity.call_args[0]
        assert collection == "/v1/types/mail/instances/"
        assert data["name"] == "corp"
        assert data["domain"] == "example.org"
        assert data["version"] == f"/v1/types/mail/versions/{VERSION_UUID}"
        assert "description" not in data


class TestMailAccounts:
    def test_add_cmd_builds_nested_collection_and_payload(self) -> None:
        result, add_entity = _run(
            "accounts",
            "add",
            "-p",
            PROJECT_ID,
            "-i",
            INSTANCE_UUID,
            "--username",
            "postmaster",
            "--password",
            "s3cret",
        )
        assert result.exit_code == 0, result.output
        _, collection, data = add_entity.call_args[0]
        assert collection == f"/v1/types/mail/instances/{INSTANCE_UUID}/accounts/"
        assert "instance" not in data
        assert data["username"] == "postmaster"
        # password_hash is HIDDEN for every method; the API derives it from the
        # plaintext `password`, which is writable on create and update.
        assert data["password"] == "s3cret"
        assert "password_hash" not in data
        assert "active" not in data
