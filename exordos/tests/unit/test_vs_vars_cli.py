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
from exordos.cmd.vs import vs_group
from exordos.common.cmd_context import ContextObject

VAR_UUID = "11111111-1111-1111-1111-111111111111"
PROJECT_ID = "22222222-2222-2222-2222-222222222222"


def _invoke(*args: str, input: str | None = None):
    return CliRunner().invoke(
        vs_group,
        list(args),
        input=input,
        obj=ContextObject(
            auth_data={},
            cfg_path=None,
            developer_key_path=None,
            cfg={},
            need_update=None,
        ),
    )


def _sent_value(client) -> object:
    value_calls = [
        call
        for call in client.add_entity.call_args_list
        if call.args[1] == c.VALUE_COLLECTION
    ]
    assert len(value_calls) == 1
    return value_calls[0].args[2]["value"]


@mock.patch("exordos.cmd.vs.vars.commands.show_data")
@mock.patch("exordos.cmd.vs.vars.commands.base_client")
class TestVarsSetCli:
    def _setup_variable(self, client) -> None:
        client.list_entities.return_value = [
            {"uuid": VAR_UUID, "project_id": PROJECT_ID, "name": "my_var"}
        ]

    def test_set_variable_cmd_value_argument(self, client, _show) -> None:
        self._setup_variable(client)

        result = _invoke("vars", "set", "my_var", "42")

        assert result.exit_code == 0, result.output
        assert _sent_value(client) == 42

    def test_set_variable_cmd_from_file_multiline(
        self, client, _show, tmp_path
    ) -> None:
        self._setup_variable(client)
        path = tmp_path / "value.txt"
        path.write_text("line1\nline2\n")

        result = _invoke("vars", "set", "my_var", "--from-file", str(path))

        assert result.exit_code == 0, result.output
        assert _sent_value(client) == "line1\nline2"

    def test_set_variable_cmd_from_file_crlf_normalized(
        self, client, _show, tmp_path
    ) -> None:
        self._setup_variable(client)
        path = tmp_path / "value.txt"
        path.write_bytes(b"line1\r\nline2\r\n")

        result = _invoke("vars", "set", "my_var", "-f", str(path))

        assert result.exit_code == 0, result.output
        assert _sent_value(client) == "line1\nline2"

    def test_set_variable_cmd_from_file_converts_type(
        self, client, _show, tmp_path
    ) -> None:
        self._setup_variable(client)
        path = tmp_path / "value.json"
        path.write_text('{"a": 1}\n')

        result = _invoke("vars", "set", "my_var", "-f", str(path))

        assert result.exit_code == 0, result.output
        assert _sent_value(client) == {"a": 1}

    def test_set_variable_cmd_from_stdin(self, client, _show) -> None:
        self._setup_variable(client)

        result = _invoke("vars", "set", "my_var", "-f", "-", input="s3cr3t\n")

        assert result.exit_code == 0, result.output
        assert _sent_value(client) == "s3cr3t"

    def test_set_variable_cmd_both_value_and_file(
        self, client, _show, tmp_path
    ) -> None:
        path = tmp_path / "value.txt"
        path.write_text("x")

        result = _invoke("vars", "set", "my_var", "42", "-f", str(path))

        assert result.exit_code != 0
        assert "either VALUE or '--from-file'" in result.output
        client.add_entity.assert_not_called()

    def test_set_variable_cmd_no_value(self, client, _show) -> None:
        result = _invoke("vars", "set", "my_var")

        assert result.exit_code != 0
        assert "either VALUE or '--from-file'" in result.output
        client.add_entity.assert_not_called()

    def test_set_variable_cmd_missing_file(self, client, _show, tmp_path) -> None:
        result = _invoke("vars", "set", "my_var", "-f", str(tmp_path / "nope"))

        assert result.exit_code != 0
        client.add_entity.assert_not_called()
