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
"""Unit tests for pushing to a project's internal repository."""

from unittest.mock import MagicMock
from unittest.mock import patch

import click
import pytest

from exordos.repo import internal

PROJECT = "00000000-0000-4000-8000-00000000000a"
AUTH_DATA = {
    "endpoint": "https://realm.example.com/api/core",
    "scope": f"project:{PROJECT}",
}


def test_repo_url_is_on_the_api_host():
    assert (
        internal.repo_url("https://realm.example.com:8443/api/core", PROJECT)
        == f"https://realm.example.com:8443/repo/{PROJECT}"
    )


def test_resolve_repo_project_keeps_the_token_unscoped():
    with patch.object(internal.base_client, "get_user_api_client") as client:
        auth_data, project_id = internal.resolve(AUTH_DATA, "p2")

    # A token scoped to p2 would lack an admin's unscoped permissions.
    assert project_id == "p2"
    assert auth_data["scope"] is None
    client.assert_not_called()


def test_resolve_keeps_the_given_project():
    with patch.object(internal.base_client, "get_user_api_client") as client:
        assert internal.resolve(AUTH_DATA) == (AUTH_DATA, PROJECT)

    client.assert_not_called()


@pytest.mark.parametrize("scope", [None, ""])
def test_resolve_falls_back_to_the_default_project(scope):
    client = MagicMock()
    client.introspect.return_value = {"project_id": PROJECT}
    with patch.object(
        internal.base_client, "get_user_api_client", return_value=client
    ) as get_client:
        auth_data, project_id = internal.resolve({**AUTH_DATA, "scope": scope})

    assert project_id == PROJECT
    # Core scopes a `project:default` token to the user's default project.
    assert auth_data["scope"] == "project:default"
    assert get_client.call_args.args[0]["scope"] == "project:default"


def test_resolve_without_a_default_project_says_what_to_do():
    client = MagicMock()
    client.introspect.return_value = {"project_id": None}
    with (
        patch.object(internal.base_client, "get_user_api_client", return_value=client),
        pytest.raises(click.ClickException, match="--project-id"),
    ):
        internal.resolve({**AUTH_DATA, "scope": None})


def test_driver_pushes_with_a_fresh_token_and_keeps_the_index():
    auth = MagicMock()
    auth.get_auth_header.return_value = {"Authorization": "Bearer tkn"}
    with patch.object(internal.base_client, "get_authenticator", return_value=auth):
        driver = internal.load_driver(AUTH_DATA, PROJECT)

    auth.authenticate.assert_called_once()
    assert driver._session.headers["Authorization"] == "Bearer tkn"
    assert driver._update_index is True
    assert driver.elements_path == (
        f"https://realm.example.com/repo/{PROJECT}/exordos-elements"
    )


def test_a_bare_access_token_is_used_as_is():
    auth = MagicMock()
    auth.get_auth_header.return_value = {"Authorization": "Bearer given"}
    with patch.object(internal.base_client, "get_authenticator", return_value=auth):
        driver = internal.load_driver({**AUTH_DATA, "access_token": "given"}, PROJECT)

    # Nothing to refresh from: re-authenticating would run a password grant.
    auth.authenticate.assert_not_called()
    assert driver._session.headers["Authorization"] == "Bearer given"


def test_refresh_refreshes_the_internal_repo_only():
    repos = [
        {"uuid": "nginx-uuid", "driver_spec": {"kind": "nginx"}},
        {"uuid": "internal-uuid", "driver_spec": {"kind": "internal"}},
    ]
    with (
        patch.object(internal.base_client, "get_user_api_client"),
        patch.object(internal.base_client, "list_entities", return_value=repos) as ls,
        patch.object(internal.base_client, "action_entity") as action,
    ):
        internal.refresh(AUTH_DATA, PROJECT)

    assert ls.call_args.kwargs == {"project_id": PROJECT}
    assert action.call_args.args[2:] == ("refresh", "internal-uuid")


def test_refresh_without_a_pushed_repo_does_nothing():
    with (
        patch.object(internal.base_client, "get_user_api_client"),
        patch.object(internal.base_client, "list_entities", return_value=[]),
        patch.object(internal.base_client, "action_entity") as action,
    ):
        internal.refresh(AUTH_DATA, PROJECT)

    action.assert_not_called()
