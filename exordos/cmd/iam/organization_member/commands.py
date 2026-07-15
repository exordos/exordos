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

import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "organization_member"
ENTITY_COLLECTION = c.ORGANIZATION_MEMBER_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Organization": "organization",
    "User": "user",
    "Role": "role",
}


organization_members_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, parents=["organization"]
)


@click.command("add", help=f"Add a new {ENTITY} to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-o",
    "--organization-uuid",
    type=click.UUID,
    required=True,
    help="organization uuid",
)
@click.option(
    "--user",
    type=click.UUID,
    required=True,
    help="user uuid",
)
@click.option(
    "-r",
    "--role",
    type=click.Choice(["MEMBER", "OWNER"], case_sensitive=False),
    required=False,
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    organization_uuid: sys_uuid.UUID,
    user: sys_uuid.UUID,
    role: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "user": f"/v1/iam/users/{user}",
    }
    if role is not None:
        data["role"] = role

    entity = base_client.add_entity(
        client, ENTITY_COLLECTION.format(organization_uuid=organization_uuid), data
    )
    show_data(entity)


organization_members_group.add_command(add_cmd, aliases=["a"])
