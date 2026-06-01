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
#    License for the specific language governing role_bindings and limitations
#    under the License.
from __future__ import annotations

import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "role_binding"
ENTITY_COLLECTION = c.ROLE_BINDING_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Role": "role",
    "User": "user",
    "Status": "status",
}


role_bindings_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@role_bindings_group.command(
    "add", help=f"Add a new {ENTITY} to the Exordos installation"
)
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=False,
    help=f"UUID of the project in which to deploy the {ENTITY}",
)
@click.option(
    "--user",
    type=click.UUID,
    required=True,
    help="role uuid",
)
@click.option(
    "--role",
    type=click.UUID,
    required=True,
    help="user uuid",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID | None,
    user: sys_uuid.UUID,
    role: sys_uuid.UUID,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "role": f"{c.ROLE_COLLECTION}{role}",
        "user": f"{c.USER_COLLECTION}{user}",
    }
    if project_id is not None:
        data["project"] = f"{c.PROJECT_COLLECTION}{project_id}"
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)
