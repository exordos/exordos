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
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "value"
ENTITY_COLLECTION = c.VALUE_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Variable": "variable_id",
    "Value": "value",
    "ReadOnly": "read_only",
    "Status": "status",
}


values_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("add", help=f"Add a new {ENTITY} to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the value",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the value",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_value",
    help="Name of the value",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the value",
)
@click.option(
    "--var",
    type=str,
    default=None,
    help="UUID of a variable the value belongs to",
)
@click.option(
    "-V",
    "--value",
    type=click.STRING,
    default="",
    help="value",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    var: str | None,
    value: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "value": utils.convert_to_nearest_type(value),
    }

    # Validate variable UUID if provided
    if var:
        try:
            sys_uuid.UUID(var)
        except ValueError:
            raise click.ClickException(f"Variable {var} is not a valid UUID")
        data["variable"] = f"{c.VARIABLE_COLLECTION}{var}"

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@click.command("update", help="Update value")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="Name of the project in which to deploy the value",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the value",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the value",
)
@click.option(
    "-V",
    "--value",
    type=click.STRING,
    default=None,
    help="value",
)
@click.option(
    "-v",
    "--variable",
    type=str,
    default=None,
    help="uuid of the variable",
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
    value: str | None,
    variable: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if value is not None:
        data["value"] = utils.convert_to_nearest_type(value)
    if variable is not None:
        data["variable"] = variable
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


values_group.add_command(add_cmd, aliases=["a"])
values_group.add_command(update_cmd, aliases=["u"])
