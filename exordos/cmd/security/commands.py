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

import typing as tp
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "rule"
ENTITY_COLLECTION = c.SECURITY_RULES_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Condition": "condition",
    "Action": "action",
    "Operator": "operator",
}


rules_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command(
    "add",
    help=f"Add a new {ENTITY}",
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
    help="UUID of the project",
)
@click.option(
    "-n",
    "--name",
    type=str,
    required=False,
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
    "-o",
    "--operator",
    type=click.Choice(["OR", "AND"]),
    required=False,
)
@click.option(
    "--action",
    multiple=True,
)
@click.option(
    "--condition",
    multiple=True,
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str,
    operator: str | None,
    action: tuple[str, ...],
    condition: tuple[str, ...],
) -> None:
    """
    Example for anonymous-registration:
    exordos rules add -n anonymous-registration --action kind=grant_permission --action permission=iam.user.create --condition method=POST --condition uri_regex=^/v1/iam/users/ --condition kind=uri_regex
    """
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data: dict[str, tp.Any] = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "action": utils.convert_input_multiply(action),
        "condition": utils.convert_input_multiply(condition),
    }
    if operator is not None:
        data["operator"] = operator
    if project_id is not None:
        data["project_id"] = str(project_id)

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    click.echo(f"{ENTITY} {entity['uuid']} created")
    show_data(entity)


rules_group.add_command(add_cmd, aliases=["a"])
