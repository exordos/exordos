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

from rich.live import Live
import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.common.table import fill_table
from exordos.common.table import print_table
from exordos.common.table import show_data

ENTITY = "backend_pool"
ENTITY_COLLECTION = c.BACKEND_POOL_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Balance": "balance",
    "Endpoints": "endpoints",
    "Status": "status",
}


@click.group(
    f"{ENTITY}s",
    cls=ClickAliasedGroup,
    invoke_without_command=True,
    help=f"Manage {ENTITY}s",
)
def backend_pools_group():
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
    "--lb-uuid",
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
    lb_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    if watch:
        with Live(refresh_per_second=4) as live:
            while True:
                entities = base_client.list_entities(
                    client, ENTITY_COLLECTION.format(lb_uuid=lb_uuid), **filters
                )
                live.update(fill_table(entities, FIELDS_MAP), refresh=True)
                time.sleep(interval)
    else:
        entities = base_client.list_entities(
            client, ENTITY_COLLECTION.format(lb_uuid=lb_uuid), **filters
        )
        print_table(fill_table(entities, FIELDS_MAP), output)


backend_pools_group.add_command(list_cmd, aliases=["l"])


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
    "--lb-uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
    output: str,
    lb_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(
        client, ENTITY_COLLECTION.format(lb_uuid=lb_uuid), uuid
    )
    show_data(data, output)


backend_pools_group.add_command(show_cmd, aliases=["get", "g"])


@click.command("delete", help=f"Delete {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-d",
    "--lb-uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    uuid: str,
    lb_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    base_client.delete_entity(client, ENTITY_COLLECTION.format(lb_uuid=lb_uuid), uuid)
    click.echo(f"{ENTITY} {uuid} deleted")


backend_pools_group.add_command(delete_cmd, aliases=["d"])
