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


def _project_id(auth_data: dict[str, tp.Any]) -> str:
    scope = auth_data.get("scope") or ""
    if not scope.startswith(PROJECT_SCOPE_PREFIX):
        raise click.ClickException(
            "The internal repository belongs to a project: pass --project-id "
            "or set project_id in the current context."
        )
    return scope[len(PROJECT_SCOPE_PREFIX) :]


def repo_url(endpoint: str, project_id: str) -> str:
    """Return the repo base URL on the host of the realm's API endpoint."""
    parsed = urllib_parse.urlsplit(endpoint)
    return f"{parsed.scheme}://{parsed.netloc}/repo/{project_id}"


def load_driver(auth_data: dict[str, tp.Any]) -> nginx.NginxRepoDriver:
    """Build a driver pushing to the current realm's project repository."""
    project_id = _project_id(auth_data)
    auth = base_client.get_authenticator(auth_data)
    if auth is None:
        raise click.ClickException("The internal repository requires authentication.")
    # A fresh token: a cached one may expire in the middle of a push.
    auth.authenticate()
    token = auth.get_auth_header()["Authorization"].split(" ", 1)[1]
    return nginx.NginxRepoDriver(
        url=repo_url(auth_data["endpoint"], project_id),
        name=f"internal repo of project {project_id}",
        token=token,
        update_index=True,
    )


def refresh(auth_data: dict[str, tp.Any]) -> None:
    """Make the realm pick up what was pushed to the project repository."""
    project_id = _project_id(auth_data)
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
