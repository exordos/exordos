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

import json
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "idp"
ENTITY_COLLECTION = c.IDP_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Scope": "scope",
    "Iam_client": "iam_client",
    "Status": "status",
}

idps_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


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
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Uuid of the project",
)
@click.option(
    "-i",
    "--iam-client",
    type=click.UUID,
    required=True,
    help="Uuid of iam_client",
)
@click.option(
    "--scope",
    type=str,
    required=False,
    help="scope",
)
@click.option(
    "--nonce_required",
    type=bool,
    is_flag=True,
    default=True,
)
@click.option(
    "--callback",
    type=str,
    required=True,
    help="JSON string for callbacks",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    iam_client: sys_uuid.UUID,
    scope: str | None,
    nonce_required: bool,
    callback: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    try:
        # Convert string to dictionary
        callback_data = json.loads(callback)
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON string: '{callback}'", err=True)
        return

    data = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "iam_client": f"{c.CLIENT_COLLECTION}{iam_client}",
        "nonce_required": nonce_required,
        "callback": callback_data,
    }
    if scope is not None:
        data["scope"] = scope

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


idps_group.add_command(add_cmd, aliases=["a"])
