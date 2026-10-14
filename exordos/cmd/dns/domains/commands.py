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
from __future__ import annotations

import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.base import tag_options
from exordos.cmd.base import tags_payload
from exordos.common.table import fill_table
from exordos.common.table import print_table
from exordos.common.table import show_data

ENTITY = "domain"
ENTITY_COLLECTION = c.DOMAIN_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
}


domains_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, add_tags_command=True
)


@click.command("info", help="Show domain details with DNS records")
@click.argument("uuid", type=str, required=True)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def info_cmd(ctx: click.Context, uuid: str, output: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    domain = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(domain, output)

    records = base_client.list_entities(
        client, c.RECORD_COLLECTION.format(domain_uuid=domain["uuid"])
    )
    if records:
        from exordos.cmd.dns.records.commands import FIELDS_MAP as RECORDS_FIELDS_MAP

        print_table(fill_table(records, RECORDS_FIELDS_MAP), output)


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
@tag_options()
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    sync_to_ecosystem: bool,
    tags: tuple[str, ...] = (),
) -> None:
    tag_data = tags_payload(tags)
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "sync_to_ecosystem": sync_to_ecosystem,
    }
    data.update(tag_data)
    data = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(data)


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-n",
    "--name",
    type=str,
    required=False,
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-s",
    "--sync-to-ecosystem",
    required=False,
    is_flag=True,
    help=f"Sync the {ENTITY} to the ecosystem",
)
@tag_options(update=True)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    name: str | None,
    sync_to_ecosystem: bool | None,
    tags: tuple[str, ...] = (),
    clear_tags: bool = False,
) -> None:
    tag_data = tags_payload(tags, clear_tags)
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if name is not None:
        data["name"] = name
    if sync_to_ecosystem is not None:
        data["sync_to_ecosystem"] = sync_to_ecosystem

    data.update(tag_data)
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


domains_group.add_command(add_cmd, aliases=["a"])
domains_group.add_command(update_cmd, aliases=["u"])
domains_group.add_command(info_cmd, aliases=["i"])
