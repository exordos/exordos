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

ENTITY = "limit"
ENTITY_COLLECTION = c.LIMIT_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Resource Name": "resource_name",
    "Field Name": "field_name",
    "Limit": "limit",
}


limits_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, add_clear_command=True
)


@click.command("add", help=f"Add a new {ENTITY}")
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
    required=True,
    help=f"Name of the project in which to deploy the {ENTITY}",
)
@click.option(
    "-r",
    "--resource-name",
    type=str,
    required=True,
    help=f"Resource name of the {ENTITY}",
)
@click.option(
    "-f",
    "--field-name",
    type=str,
    required=False,
    help=f"Resource field name of the {ENTITY}",
)
@click.option(
    "-l",
    "--limit",
    type=int,
    required=True,
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    resource_name: str,
    field_name: str | None,
    limit: int,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "resource_name": resource_name,
        "limit": limit,
    }
    if field_name is not None:
        data["field_name"] = field_name
    data = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(data)


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument(
    "uuid",
    type=click.UUID,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="Uuid of the project",
)
@click.option(
    "-r",
    "--resource-name",
    type=str,
    required=False,
    help=f"Resource name of the {ENTITY}",
)
@click.option(
    "-l",
    "--limit",
    type=int,
    required=False,
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    resource_name: str | None,
    limit: int | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if resource_name is not None:
        data["resource_name"] = resource_name
    if limit is not None:
        data["limit"] = limit

    if not data:
        raise click.UsageError("At least one option to update must be provided.")

    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


limits_group.add_command(add_cmd, aliases=["a"])
limits_group.add_command(update_cmd, aliases=["u"])
