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

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import fill_table
from exordos.common.table import print_table
from exordos.common.table import show_data

ENTITY = "load_balancer"
ENTITY_COLLECTION = c.LB_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "ipsv4": "ipsv4",
    "Type": "type",
    "Status": "status",
}


lbs_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("info", help="Show load balancer details with vhosts and backend_pools")
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
@click.pass_context
def info_cmd(ctx: click.Context, uuid: str, output: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    # Show LB details
    lb_data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(lb_data, output)

    # Show associated vhosts
    vhosts = base_client.list_entities(
        client, c.VHOST_COLLECTION.format(lb_uuid=lb_data["uuid"])
    )
    if vhosts:
        from exordos.cmd.network.vhosts.commands import FIELDS_MAP as VHOSTS_FIELDS_MAP

        print_table(fill_table(vhosts, VHOSTS_FIELDS_MAP), output)

    # Show associated backend_pools
    backend_pools = base_client.list_entities(
        client, c.BACKEND_POOL_COLLECTION.format(lb_uuid=lb_data["uuid"])
    )
    if backend_pools:
        from exordos.cmd.network.backend_pools.commands import (
            FIELDS_MAP as BACKEND_POOLS_FIELDS_MAP,
        )

        print_table(fill_table(backend_pools, BACKEND_POOLS_FIELDS_MAP), output)


lbs_group.add_command(info_cmd, aliases=["i"])
