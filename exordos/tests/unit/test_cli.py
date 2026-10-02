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
import pathlib
from unittest.mock import MagicMock

from click.testing import CliRunner
import pytest
from requests.exceptions import RequestException

from exordos.cmd import cli

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


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


POLICY_REFUSAL = (
    '{"type":"PolicyNotAuthorized","code":10000001,'
    '"message":"Policy rule exordos_ecosystem.realm.create is disallowed."}'
)


def test_explain_surfaces_the_reason_the_server_gave() -> None:
    """A refused policy is a missing permission, not a malformed request."""
    message = cli._explain(400, POLICY_REFUSAL)

    assert "exordos_ecosystem.realm.create is disallowed" in message
    assert "PolicyNotAuthorized" in message
    # The envelope itself is noise once the message is out of it.
    assert '"code"' not in message


def test_explain_keeps_a_body_that_is_not_json() -> None:
    assert "nginx bad gateway" in cli._explain(502, "nginx bad gateway")


def test_explain_says_so_when_there_is_no_body() -> None:
    assert "<empty response>" in cli._explain(500, "   ")


def test_main_reports_an_http_error_instead_of_raising_it(monkeypatch, capsys) -> None:
    """The reason has to survive the trip to the user's terminal.

    Before, this handling sat under `if __name__ == "__main__"` — which the
    console script does not execute — and the user got a traceback.
    """
    response = MagicMock(status_code=400, text=POLICY_REFUSAL)
    failing = MagicMock(side_effect=RequestException(response=response))
    monkeypatch.setattr(cli, "exordos", failing)

    with pytest.raises(SystemExit) as exit_code:
        cli.main()

    assert exit_code.value.code == 1
    assert "is disallowed" in capsys.readouterr().out


def test_the_console_script_goes_through_the_error_handling() -> None:
    """Pointing the entry point at the bare group is what hid the reason."""
    pyproject = pathlib.Path(cli.__file__).parents[2] / "pyproject.toml"
    with pyproject.open("rb") as f:
        scripts = tomllib.load(f)["project"]["scripts"]

    assert scripts["exordos"] == "exordos.cmd.cli:main"
