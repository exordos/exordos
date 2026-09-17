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

from unittest import mock

from click.testing import CliRunner

from exordos import constants as c
from exordos.cmd.secret import secret_group
from exordos.common.cmd_context import ContextObject

UUID = "11111111-1111-1111-1111-111111111111"
PROJECT_ID = "22222222-2222-2222-2222-222222222222"


def _invoke(*args: str):
    return CliRunner().invoke(
        secret_group,
        list(args),
        obj=ContextObject(
            auth_data={},
            cfg_path=None,
            developer_key_path=None,
            cfg={},
            need_update=None,
        ),
    )


@mock.patch("exordos.cmd.secret.secrets.commands.show_data")
@mock.patch("exordos.cmd.secret.secrets.commands.base_client")
class TestSecretsCli:
    def test_add_sends_value_and_default(self, client, _show) -> None:
        result = _invoke(
            "secrets",
            "add",
            "-u",
            UUID,
            "-p",
            PROJECT_ID,
            "-n",
            "token",
            "--value",
            "s3cr3t",
            "--default-value",
            "sandbox",
        )

        assert result.exit_code == 0, result.output
        client.add_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            c.SECRET_COLLECTION,
            {
                "uuid": UUID,
                "project_id": PROJECT_ID,
                "name": "token",
                "description": "",
                "value": "s3cr3t",
                "default_value": "sandbox",
            },
        )

    def test_add_omits_unset_values(self, client, _show) -> None:
        result = _invoke("sec", "a", "-u", UUID, "-p", PROJECT_ID)

        assert result.exit_code == 0, result.output
        data = client.add_entity.call_args.args[2]
        assert "value" not in data
        assert "default_value" not in data

    def test_update_sends_only_given_fields(self, client, _show) -> None:
        result = _invoke("secrets", "update", UUID, "-v", "rotated")

        assert result.exit_code == 0, result.output
        client.update_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            c.SECRET_COLLECTION,
            UUID,
            {"value": "rotated"},
        )
