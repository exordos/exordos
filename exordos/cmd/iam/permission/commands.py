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
from exordos.common.table import fill_table
from exordos.common.table import print_table
from exordos.common.table import show_data

ENTITY = "permission"
ENTITY_COLLECTION = c.PERMISSION_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Status": "status",
}


permissions_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


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
    "-n",
    "--name",
    type=str,
    default=f"test_{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
    }

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@click.command("role", help="List permissions bound to a role")
@click.pass_context
@click.argument(
    "role",
    type=str,
    required=True,
    help="role name or uuid",
)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
def by_role_cmd(ctx: click.Context, role: str, output: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    role = base_client.get_entity(client, c.ROLE_COLLECTION, role)
    bindings = base_client.list_entities(
        client, c.PERMISSION_BINDING_COLLECTION, role=role["uuid"]
    )
    permissions = []
    for binding in bindings:
        permissions.append(
            base_client.get_entity(
                client, c.PERMISSION_COLLECTION, binding["permission"].split("/")[-1]
            )
        )
    permissions.sort(key=lambda x: x["name"])
    print_table(fill_table(permissions, FIELDS_MAP), output)


permissions_group.add_command(add_cmd, aliases=["a"])
permissions_group.add_command(by_role_cmd, aliases=["r"])
