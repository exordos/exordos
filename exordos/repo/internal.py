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
"""The project's internal repository of a realm.

The realm's core LB serves it at ``<realm>/repo/<project_id>/`` and lets a
request through only with a core IAM token of that project. Core creates the
matching `internal` repository on the first push.
"""

from __future__ import annotations

import typing as tp
from urllib import parse as urllib_parse

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.repo import nginx

PROJECT_SCOPE_PREFIX = "project:"
# Core scopes such a token to the user's default project.
DEFAULT_PROJECT_SCOPE = f"{PROJECT_SCOPE_PREFIX}default"


def resolve(
    auth_data: dict[str, tp.Any], repo_project: str | None = None
) -> tuple[dict[str, tp.Any], str]:
    """Return the auth data to push with and the ID of the project.

    `repo_project` wins and keeps the token unscoped: core takes a token's
    permissions from its project's bindings, so an admin's are only in an
    unscoped one. Then comes the project of --project-id or the context,
    then the user's default project.
    """
    if repo_project:
        return {**auth_data, "scope": None}, str(repo_project)

    scope = auth_data.get("scope") or ""
    if scope.startswith(PROJECT_SCOPE_PREFIX):
        return auth_data, scope[len(PROJECT_SCOPE_PREFIX) :]

    auth_data = {**auth_data, "scope": DEFAULT_PROJECT_SCOPE}
    client = base_client.get_user_api_client(auth_data)
    project_id = client.introspect().get("project_id")
    if not project_id:
        raise click.ClickException(
            "You have no default project: pass --project-id or set "
            "project_id in the current context."
        )
    return auth_data, str(project_id)


def repo_url(endpoint: str, project_id: str) -> str:
    """Return the repo base URL on the host of the realm's API endpoint."""
    parsed = urllib_parse.urlsplit(endpoint)
    return f"{parsed.scheme}://{parsed.netloc}/repo/{project_id}"


def load_driver(auth_data: dict[str, tp.Any], project_id: str) -> nginx.NginxRepoDriver:
    """Build a driver pushing to the project's internal repository.

    `auth_data` and `project_id` come from :func:`resolve`.
    """
    auth = base_client.get_authenticator(auth_data)
    if auth is None:
        raise click.ClickException("The internal repository requires authentication.")
    # A fresh token: a cached one may expire in the middle of a push. A
    # bare --access-token has nothing to refresh from, so it is used as is.
    if auth_data.get("refresh_token") or not auth_data.get("access_token"):
        auth.authenticate()
    token = auth.get_auth_header()["Authorization"].split(" ", 1)[1]
    return nginx.NginxRepoDriver(
        url=repo_url(auth_data["endpoint"], project_id),
        name=f"internal repo of project {project_id}",
        token=token,
        update_index=True,
    )


def refresh(auth_data: dict[str, tp.Any], project_id: str) -> None:
    """Make the realm pick up what was pushed to the project repository."""
    client = base_client.get_user_api_client(auth_data)
    repos = [
        r
        for r in base_client.list_entities(
            client, c.REPOSITORY_COLLECTION, project_id=project_id
        )
        if r["driver_spec"]["kind"] == "internal"
    ]
    if not repos:
        # Nothing was written, so core has not created it.
        return
    base_client.action_entity(
        client, c.REPOSITORY_COLLECTION, "refresh", repos[0]["uuid"]
    )
