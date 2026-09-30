#    Copyright 2026 Genesis Corporation.
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
from unittest.mock import MagicMock
from unittest.mock import patch
import uuid as sys_uuid

from click.testing import CliRunner

from exordos.cmd.secret.certificate import commands
from exordos.common.cmd_context import ContextObject

PROJECT_ID = "12345678-c625-4fee-81d5-f691897b8142"


def _invoke(cmd: tp.Any, *args: str) -> tuple[tp.Any, MagicMock, MagicMock]:
    ctx_obj = ContextObject(
        auth_data={"endpoint": "http://localhost"},
        cfg_path=None,
        developer_key_path=None,
        cfg={},
        need_update=None,
    )
    with (
        patch.object(commands.base_client, "get_user_api_client"),
        patch.object(commands.base_client, "add_entity") as add_mock,
        patch.object(commands.base_client, "update_entity") as update_mock,
        patch.object(commands, "show_data"),
    ):
        result = CliRunner().invoke(cmd, list(args), obj=ctx_obj)
    return result, add_mock, update_mock


class TestCertificateAdd:
    def test_add_cmd_sends_core_payload(self) -> None:
        result, add_mock, _ = _invoke(
            commands.add_cmd,
            "-p",
            PROJECT_ID,
            "-n",
            "my-cert",
            "-e",
            "user@exordos.com",
            "-d",
            "*.test.exordos.com",
            "-d",
            "test.exordos.com",
        )

        assert result.exit_code == 0, result.output
        data = add_mock.call_args.args[2]
        assert data["name"] == "my-cert"
        assert data["project_id"] == PROJECT_ID
        assert data["email"] == "user@exordos.com"
        assert data["domains"] == ["*.test.exordos.com", "test.exordos.com"]
        assert data["method"] == {"kind": "dns_core"}
        assert sys_uuid.UUID(data["uuid"])

    def test_add_cmd_omits_thresholds_by_default(self) -> None:
        result, add_mock, _ = _invoke(
            commands.add_cmd, "-p", PROJECT_ID, "-e", "a@b.com", "-d", "a.com"
        )

        assert result.exit_code == 0, result.output
        data = add_mock.call_args.args[2]
        assert "expiration_threshold" not in data
        assert "overcome_threshold" not in data

    def test_add_cmd_sends_thresholds(self) -> None:
        result, add_mock, _ = _invoke(
            commands.add_cmd,
            "-p",
            PROJECT_ID,
            "-e",
            "a@b.com",
            "-d",
            "a.com",
            "--expiration-threshold",
            "30",
            "--overcome-threshold",
        )

        assert result.exit_code == 0, result.output
        data = add_mock.call_args.args[2]
        assert data["expiration_threshold"] == 30
        assert data["overcome_threshold"] is True

    def test_add_cmd_requires_domain(self) -> None:
        result, add_mock, _ = _invoke(
            commands.add_cmd, "-p", PROJECT_ID, "-e", "a@b.com"
        )

        assert result.exit_code != 0
        add_mock.assert_not_called()

    def test_add_cmd_requires_email(self) -> None:
        result, add_mock, _ = _invoke(commands.add_cmd, "-p", PROJECT_ID, "-d", "a.com")

        assert result.exit_code != 0
        add_mock.assert_not_called()

    def test_add_cmd_rejects_unknown_method(self) -> None:
        result, add_mock, _ = _invoke(
            commands.add_cmd,
            "-p",
            PROJECT_ID,
            "-e",
            "a@b.com",
            "-d",
            "a.com",
            "-m",
            "http_01",
        )

        assert result.exit_code != 0
        add_mock.assert_not_called()


class TestCertificateUpdate:
    def test_update_cmd_sends_only_given_fields(self) -> None:
        uuid = str(sys_uuid.uuid4())

        result, _, update_mock = _invoke(commands.update_cmd, uuid, "-n", "new")

        assert result.exit_code == 0, result.output
        assert update_mock.call_args.args[3] == {"name": "new"}

    def test_update_cmd_sends_email_domains_and_thresholds(self) -> None:
        uuid = str(sys_uuid.uuid4())

        result, _, update_mock = _invoke(
            commands.update_cmd,
            uuid,
            "-e",
            "x@y.com",
            "-d",
            "a.com",
            "-d",
            "b.com",
            "--expiration-threshold",
            "0",
            "--no-overcome-threshold",
        )

        assert result.exit_code == 0, result.output
        assert update_mock.call_args.args[3] == {
            "email": "x@y.com",
            "domains": ["a.com", "b.com"],
            "expiration_threshold": 0,
            "overcome_threshold": False,
        }
