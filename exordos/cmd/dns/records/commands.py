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

import time
import uuid as sys_uuid

from rich.live import Live
import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.common.table import fill_table
from exordos.common.table import print_table
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


@click.group(
    f"{ENTITY}s",
    cls=ClickAliasedGroup,
    invoke_without_command=True,
    help=f"Manage {ENTITY}s",
)
def records_group():
    pass


@click.command("list", help=f"List {ENTITY}s")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: --f "
        "parent=11111111-1111-1111-1111-11111111111 --filters status=NEW"
    ),
)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.option(
    "-w",
    "--watch",
    show_default=True,
    is_flag=True,
    help=f"Watch the list of {ENTITY}s",
)
@click.option(
    "--interval",
    type=click.FloatRange(min=0.1),
    default=0.5,
    help="Refresh interval in seconds.",
)
@click.option(
    "-d",
    "--domain-uuid",
    type=str,
    required=True,
)
@click.pass_context
def list_cmd(
    ctx: click.Context,
    filters: tuple[str, ...],
    output: str,
    watch: bool,
    interval: float,
    domain_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    if watch:
        with Live(refresh_per_second=4) as live:
            while True:
                entities = base_client.list_entities(
                    client, ENTITY_COLLECTION.format(domain_uuid=domain_uuid), **filters
                )
                live.update(fill_table(entities, FIELDS_MAP), refresh=True)
                time.sleep(interval)
    else:
        entities = base_client.list_entities(
            client, ENTITY_COLLECTION.format(domain_uuid=domain_uuid), **filters
        )
        print_table(fill_table(entities, FIELDS_MAP), output)


records_group.add_command(list_cmd, aliases=["l"])


@click.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.option(
    "-d",
    "--domain-uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
    output: str,
    domain_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(
        client, ENTITY_COLLECTION.format(domain_uuid=domain_uuid), uuid
    )
    show_data(data, output)


records_group.add_command(show_cmd, aliases=["get", "g"])


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
    record: tuple[str, str],
    domain_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "type": record_type,
        "ttl": ttl,
        "prio": prio,
        "disabled": disabled,
        "record": utils.convert_input_multiply(record),
    }
    entity = base_client.add_entity(
        client, ENTITY_COLLECTION.format(domain_uuid=domain_uuid), data
    )
    show_data(entity)


records_group.add_command(add_cmd, aliases=["a"])
