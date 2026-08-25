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

ENTITY = "store"
ENTITY_COLLECTION = c.REPOSITORY_STORE_ELEMENT_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Version": "version",
    "Status": "status",
}
LATEST_STABLE_URL = f"{c.REPOSITORY_STORE_COLLECTION}latest_stable_elements/"


store_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    group_name="store",
    add_list_command=True,  # repo store l --filters name=dbaas --filters sort_key=version --filters sort_dir=desc --filters q="version != latest" -o json
    add_show_command=True,
    add_delete_command=False,
    no_auth=True,
)


@store_group.command("latest_stable_elements")
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def latest_stable_elements_cmd(
    ctx: click.Context,
    output: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entities = base_client.list_entities(client, LATEST_STABLE_URL)
    print_table(fill_table(entities, FIELDS_MAP), output)
