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
from exordos.common.table import show_data

ENTITY = "resource"
ENTITY_COLLECTION = c.RESOURCE_COLLECTION

FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Kind": "kind",
    "Full hash": "full_hash",
    "Status": "status",
    "Created at": "created_at",
    "Updated at": "updated_at",
}


resources_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    add_delete_command=False,
)


@resources_group.command(
    "info", help="Show resource and its target and actual resource"
)
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
def info_cmd(
    ctx: click.Context,
    uuid: str,
    output: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    resource = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(resource, output, "Resource")

    # Find target_resource
    targets = base_client.list_entities(client, c.TARGET_RESOURCE_COLLECTION, uuid=uuid)
    target_resource = None
    if targets:
        target_resource = targets[0]
        for target in targets:
            show_data(target, output, "Target resource")

    # Find actual_resource
    actuals = base_client.list_entities(client, c.ACTUAL_RESOURCE_COLLECTION, uuid=uuid)
    actual_resource = None
    if actuals:
        actual_resource = actuals[0]
        for actual in actuals:
            show_data(actual, output, "Actual resource")

    if (
        target_resource
        and actual_resource
        and target_resource["hash"] != actual_resource["hash"]
    ):
        click.secho(
            "Target resource and actual resource hashes are different", fg="red"
        )
