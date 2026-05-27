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
from unittest.mock import MagicMock

from click.testing import CliRunner

from exordos.cmd import cli


def test_refresh_token_auth_does_not_prompt_for_password(monkeypatch) -> None:
    prompt = MagicMock()
    monkeypatch.setattr(cli.click, "prompt", prompt)

    runner = CliRunner()
    result = runner.invoke(
        cli.exordos,
        ["--user", "alice", "--refresh-token", "refresh-token", "auth", "--help"],
    )

    assert result.exit_code == 0
    prompt.assert_not_called()
    assert "enable-otp" in result.output


def test_settings_command_does_not_prompt_for_password(monkeypatch) -> None:
    prompt = MagicMock()
    monkeypatch.setattr(cli.click, "prompt", prompt)

    runner = CliRunner()
    result = runner.invoke(
        cli.exordos,
        ["--config", "missing.yaml", "--user", "alice", "settings", "view", "--raw"],
    )

    assert result.exit_code == 0
    prompt.assert_not_called()
