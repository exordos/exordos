#    Copyright 2025 Genesis Corporation.
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

import re
import uuid as sys_uuid

from packaging import version as packaging_version
import rich_click as click

from exordos import constants as c
from exordos.cmd.base import create_entity_group

ELEMENT_ENTITY = "repo element"


def _extract_repository_uuid(x):
    repo_ref = x.get("repository")
    if not repo_ref or not isinstance(repo_ref, str):
        return ""

    try:
        return str(sys_uuid.UUID(repo_ref[-36:]))
    except ValueError:
        return repo_ref


ELEMENT_FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Version": "version",
    "Repository": _extract_repository_uuid,
    "Status": "status",
    "Installation State": "installation_state",
}

_STABLE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
_HIDDEN_STATUSES = {"NEW", "AVAILABLE", None}


def _filter_and_sort_elements(entities: list[dict], kwargs: dict) -> list[dict]:
    if not kwargs.get("dev"):
        entities = [
            e
            for e in entities
            if _STABLE_VERSION_RE.match(str(e.get("version", "")))
            or e.get("status") not in _HIDDEN_STATUSES
        ]

    def _parse_version(version):
        try:
            return packaging_version.parse(version)
        except packaging_version.InvalidVersion:
            return packaging_version.parse("0")

    return sorted(
        entities,
        key=lambda e: (
            e.get("name", ""),
            _parse_version(e.get("version", "0")),
        ),
    )


_DEV_OPTION = click.Option(
    ["--dev"],
    is_flag=True,
    default=False,
    help="Show all versions including dev",
)


@click.group("elements", help="Manage repo elements")
def elements_group():
    pass


# Add list command to elements subgroup
_elements_group = create_entity_group(
    ELEMENT_ENTITY,
    c.REPOSITORY_ELEMENT_COLLECTION,
    ELEMENT_FIELDS_MAP,
    None,
    add_list_command=True,
    add_show_command=True,
    add_delete_command=False,
    post_fetch_handler=_filter_and_sort_elements,
    extra_options=[_DEV_OPTION],
)

elements_group.add_command(_elements_group.commands["list"], aliases=["l"])
elements_group.add_command(_elements_group.commands["show"], aliases=["get", "g"])
