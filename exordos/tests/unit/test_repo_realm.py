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
"""Unit tests for pushing to a realm's project repository."""

from unittest.mock import MagicMock
from unittest.mock import patch

import click
import pytest

from exordos.repo import realm

PROJECT = "00000000-0000-4000-8000-00000000000a"
AUTH_DATA = {
    "endpoint": "https://realm.example.com/api/core",
    "scope": f"project:{PROJECT}",
}


def test_repo_url_is_on_the_api_host():
    assert (
        realm.repo_url("https://realm.example.com:8443/api/core", PROJECT)
        == f"https://realm.example.com:8443/repo/{PROJECT}"
    )


@pytest.mark.parametrize("scope", [None, ""])
def test_a_project_is_required(scope):
    with pytest.raises(click.ClickException, match="--project-id"):
        realm.load_driver({**AUTH_DATA, "scope": scope})


def test_driver_pushes_with_a_fresh_token_and_keeps_the_index():
    auth = MagicMock()
    auth.get_auth_header.return_value = {"Authorization": "Bearer tkn"}
    with patch.object(realm.base_client, "get_authenticator", return_value=auth):
        driver = realm.load_driver(AUTH_DATA)

    auth.authenticate.assert_called_once()
    assert driver._session.headers["Authorization"] == "Bearer tkn"
    assert driver._update_index is True
    assert driver.elements_path == (
        f"https://realm.example.com/repo/{PROJECT}/exordos-elements"
    )


def test_refresh_refreshes_the_internal_repo_only():
    repos = [
        {"uuid": "nginx-uuid", "driver_spec": {"kind": "nginx"}},
        {"uuid": "internal-uuid", "driver_spec": {"kind": "internal"}},
    ]
    with (
        patch.object(realm.base_client, "get_user_api_client"),
        patch.object(realm.base_client, "list_entities", return_value=repos) as ls,
        patch.object(realm.base_client, "action_entity") as action,
    ):
        realm.refresh(AUTH_DATA)

    assert ls.call_args.kwargs == {"project_id": PROJECT}
    assert action.call_args.args[2:] == ("refresh", "internal-uuid")


def test_refresh_without_a_pushed_repo_does_nothing():
    with (
        patch.object(realm.base_client, "get_user_api_client"),
        patch.object(realm.base_client, "list_entities", return_value=[]),
        patch.object(realm.base_client, "action_entity") as action,
    ):
        realm.refresh(AUTH_DATA)

    action.assert_not_called()
