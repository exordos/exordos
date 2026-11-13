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
from types import SimpleNamespace
from unittest import mock

from click.testing import CliRunner
import pytest

from exordos.clients import base
from exordos.cmd.auth import commands


@pytest.mark.parametrize("refresh_token", [None, "refresh-token"])
def test_login_cmd_authenticates_and_prints_token(refresh_token):
    http = mock.Mock()
    http.post.return_value.json.return_value = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
    }
    auth = base.CoreIamAuthenticator(
        "https://core.example",
        username="admin",
        password="password",
        access_token="old-access-token",
        refresh_token=refresh_token,
        http_client=http,
    )
    auth_data = {"endpoint": "https://core.example"}
    with mock.patch.object(
        commands.base_client,
        "get_user_api_client",
        return_value=SimpleNamespace(_auth=auth),
    ) as factory:
        result = CliRunner().invoke(
            commands.auth_group,
            ["login"],
            obj=SimpleNamespace(auth_data=auth_data),
        )

    assert result.exit_code == 0, result.output
    assert result.stdout == "new-access-token\n"
    factory.assert_called_once_with(auth_data)
    assert http.post.call_args.kwargs["data"]["grant_type"] == (
        base.GRANT_TYPE_REFRESH_TOKEN if refresh_token else base.GRANT_TYPE_PASSWORD
    )


def test_login_cmd_prompts_on_stderr():
    def authenticate():
        commands.click.prompt("Password", hide_input=True)
        commands.click.prompt("OTP code")

    auth = mock.Mock()
    auth.authenticate.side_effect = authenticate
    auth.get_auth_header.return_value = {"Authorization": "Bearer token"}
    with mock.patch.object(
        commands.base_client,
        "get_user_api_client",
        return_value=SimpleNamespace(_auth=auth),
    ):
        result = CliRunner().invoke(
            commands.auth_group,
            ["login"],
            input="password\n123456\n",
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code == 0, result.output
    assert result.stdout == "token\n"
    assert "Password" in result.stderr
    assert "OTP code" in result.stderr


def test_login_cmd_authentication_failure_prints_no_token():
    auth = mock.Mock()
    auth.authenticate.side_effect = ValueError("Invalid credentials")
    with mock.patch.object(
        commands.base_client,
        "get_user_api_client",
        return_value=SimpleNamespace(_auth=auth),
    ):
        result = CliRunner().invoke(
            commands.auth_group,
            ["login"],
            obj=SimpleNamespace(auth_data={}),
        )

    assert result.exit_code != 0
    assert result.stdout == ""
    auth.get_auth_header.assert_not_called()
