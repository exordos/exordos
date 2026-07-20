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

ENTITY = "record"
ENTITY_COLLECTION = c.RECORD_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Type": "type",
    "TTL": "ttl",
    "Record": "record",
    "Disabled": "disabled",
}


records_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, parents=["domain"]
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
    help=f"UUID of the project in which to deploy the {ENTITY}",
)
@click.option(
    "--record-type",
    type=click.Choice(["A", "NS", "SOA", "TXT"], case_sensitive=False),
    required=True,
)
@click.option(
    "--ttl",
    type=int,
    default=3600,
)
@click.option(
    "--prio",
    type=int,
    default=None,
)
@click.option(
    "--disabled",
    is_flag=True,
    default=False,
)
@click.option(
    "--record",
    multiple=True,
)
@click.option(
    "-d",
    "--domain-uuid",
    type=str,
    required=True,
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    record_type: str,
    ttl: int,
    prio: int | None,
    disabled: bool,
    record: tuple[str, ...],
    domain_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    record = utils.convert_input_multiply(record)
    if "kind" not in record:
        record["kind"] = record_type.upper()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "type": record_type,
        "ttl": ttl,
        "prio": prio,
        "disabled": disabled,
        "record": record,
    }
    entity = base_client.add_entity(
        client, ENTITY_COLLECTION.format(domain_uuid=domain_uuid), data
    )
    show_data(entity)


records_group.add_command(add_cmd, aliases=["a"])


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "--record-type",
    type=click.Choice(["A", "NS", "SOA", "TXT"], case_sensitive=False),
    required=False,
)
@click.option(
    "--ttl",
    type=int,
    required=False,
)
@click.option(
    "--prio",
    type=int,
    required=False,
)
@click.option(
    "--disabled",
    is_flag=True,
    required=False,
)
@click.option(
    "--record",
    multiple=True,
)
@click.option(
    "-d",
    "--domain-uuid",
    type=str,
    required=True,
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    record_type: str | None,
    ttl: int | None,
    prio: int | None,
    disabled: bool | None,
    record: tuple[str, ...] | None,
    domain_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if record_type is not None:
        data["record_type"] = record_type
    if ttl is not None:
        data["ttl"] = ttl
    if prio is not None:
        data["prio"] = prio
    if disabled is not None:
        data["disabled"] = disabled
    record = utils.convert_input_multiply(record)
    if record:
        data["record"] = record

    entity = base_client.update_entity(
        client, ENTITY_COLLECTION.format(domain_uuid=domain_uuid), uuid, data
    )
    show_data(entity)


records_group.add_command(update_cmd, aliases=["u"])
