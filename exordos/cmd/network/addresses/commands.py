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
from exordos.cmd.network import common as net_common
from exordos.common.table import show_data

ENTITY = "address"
ENTITY_COLLECTION = c.ADDRESS_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Address": "address",
    "Subnet": "subnet",
    "Allocation": "allocation",
    "Origin": "origin",
    # Absent from the response when unset, so read through a callable: a
    # listing that mixes bound and free addresses would blow up on the key.
    "Owner port": lambda x: str(x.get("owner_port") or ""),
    "Association": lambda x: str(x.get("association") or ""),
    "Project": "project_id",
}

addresses_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    group_name="addresses",
)


@addresses_group.command("add", help="Allocate an address in a subnet")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the address")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option(
    "-s", "--subnet", type=str, required=True, help="Subnet to allocate in (UUID/name)"
)
@click.option(
    "-a",
    "--address",
    type=str,
    default=None,
    help="The address to reserve (allocated from the subnet if omitted)",
)
def address_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    subnet: str,
    address: str | None,
) -> None:
    """The allocation outlives whoever uses it: associate it with a port
    through that port's `public` setting, disassociate it and it stays yours."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "project_id": str(project_id),
        "subnet": net_common.resolve(client, c.SUBNET_COLLECTION, subnet),
    }
    if address:
        data["address"] = address
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))
