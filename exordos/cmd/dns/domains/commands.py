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

ENTITY = "domain"
ENTITY_COLLECTION = c.DOMAIN_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
}


domains_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


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
    "-n",
    "--name",
    type=str,
    default=f"example_{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-s",
    "--sync-to-ecosystem",
    default=False,
    is_flag=True,
    help=f"Sync the {ENTITY} to the ecosystem",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    sync_to_ecosystem: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "sync_to_ecosystem": sync_to_ecosystem,
    }
    data = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(data)


domains_group.add_command(add_cmd, aliases=["a"])
