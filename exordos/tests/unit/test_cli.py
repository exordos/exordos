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
    """HTTP failures print their reason and exit with status 1."""
    response = MagicMock(status_code=400, text=POLICY_REFUSAL)
    failing = MagicMock(side_effect=RequestException(response=response))
    monkeypatch.setattr(cli, "exordos", failing)

    with pytest.raises(SystemExit) as exit_code:
        cli.main()

    assert exit_code.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "is disallowed" in captured.err


def test_the_console_script_goes_through_the_error_handling() -> None:
    """Pointing the entry point at the bare group is what hid the reason."""
    pyproject = pathlib.Path(cli.__file__).parents[2] / "pyproject.toml"
    with pyproject.open("rb") as f:
        scripts = tomllib.load(f)["project"]["scripts"]

    assert scripts["exordos"] == "exordos.cmd.cli:main"


@pytest.mark.parametrize("structured", [False, True])
def test_main_escapes_terminal_controls(monkeypatch, capsys, structured) -> None:
    detail = "denied\x1b[2J\x1b]52;c;payload\x07\r\b\x9b"
    body = json.dumps({"message": detail}) if structured else detail
    response = MagicMock(status_code=400, text=body)
    monkeypatch.setattr(
        cli, "exordos", MagicMock(side_effect=RequestException(response=response))
    )
    with pytest.raises(SystemExit):
        cli.main()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "denied" in captured.err
    assert "\\x1b" in captured.err
    assert not any(char in captured.err for char in "\x1b\x07\r\b\x9b")


def test_push_global_credentials_reach_realm_driver(tmp_path, monkeypatch) -> None:
    from exordos.cmd.repo import commands
    from exordos.repo import realm

    factory = MagicMock()
    monkeypatch.setattr(realm, "realm_authenticator", factory)
    monkeypatch.setattr(commands.repo_utils, "do_push", MagicMock())
    result = CliRunner().invoke(
        cli.exordos,
        [
            "--config",
            str(tmp_path / "missing.yaml"),
            "-e",
            "https://dcda9a.exordos.io/api/core",
            "-u",
            "admin",
            "-p",
            "secret",
            "push",
            "--driver",
            "realm",
            "--driver-params",
            "url=https://dcda9a.exordos.io/repo/00000000-0000-0000-0000-000000000000",
        ],
    )
    assert result.exit_code == 0, result.output
    assert factory.call_args.kwargs == {
        "endpoint": "https://dcda9a.exordos.io/api/core",
        "user": "admin",
        "password": "secret",
    }
    factory.return_value.authenticate.assert_called_once()


def test_push_local_credentials_override_global_options(tmp_path, monkeypatch) -> None:
    from exordos.cmd.repo import commands

    load = MagicMock()
    monkeypatch.setattr(commands.repo_utils, "load_repo_driver", load)
    monkeypatch.setattr(commands.repo_utils, "do_push", MagicMock())
    result = CliRunner().invoke(
        cli.exordos,
        [
            "--config",
            str(tmp_path / "missing.yaml"),
            "-u",
            "global",
            "-p",
            "global-password",
            "push",
            "--driver",
            "realm",
            "-u",
            "local",
            "-p",
            "local-password",
        ],
    )
    assert result.exit_code == 0, result.output
    assert load.call_args.kwargs["user"] == "local"
    assert load.call_args.kwargs["password"] == "local-password"


def test_push_keeps_saved_realm_when_global_options_omitted(
    tmp_path, monkeypatch
) -> None:
    from exordos.cmd.repo import commands

    load = MagicMock()
    monkeypatch.setattr(commands.repo_utils, "load_repo_driver", load)
    monkeypatch.setattr(commands.repo_utils, "do_push", MagicMock())
    result = CliRunner().invoke(
        cli.exordos,
        [
            "--config",
            str(tmp_path / "missing.yaml"),
            "push",
            "--driver",
            "realm",
        ],
    )
    assert result.exit_code == 0, result.output
    assert load.call_args.kwargs["user"] is None
    assert load.call_args.kwargs["password"] is None
    assert load.call_args.kwargs["endpoint"] is None
