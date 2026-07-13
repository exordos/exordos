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

ENTITY = "reservation"
ENTITY_COLLECTION = c.RESERVATION_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Resource Name": "resource_name",
}
SUMMARY_MAP = {
    "Project": "project_id",
    "Resource Name": "resource_name",
    "reserved_count": "reserved_count",
}

reservations_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, add_delete_command=False
)


@click.command("summary", help=f"Get summary of {ENTITY}s")
@click.pass_context
def summary_cmd(
    ctx: click.Context,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entities = client.filter(f"{ENTITY_COLLECTION}summary/")
    entities.sort(key=lambda x: f"{x['project_id']}-{x['resource_name']}")
    print_table(fill_table(entities, SUMMARY_MAP))


reservations_group.add_command(summary_cmd)
