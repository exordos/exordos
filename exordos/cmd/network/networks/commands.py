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
from exordos.common.table import show_data

ENTITY = "network"
ENTITY_COLLECTION = c.NETWORK_COLLECTION

# `driver_spec` carries the driver name plus what the core allocated for an
# overlay (vni/rt/mtu) — flatten it, nobody wants to read a JSON blob to see
# which network is the overlay one.
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Driver": lambda x: str((x.get("driver_spec") or {}).get("driver", "unknown")),
    "VNI": lambda x: str((x.get("driver_spec") or {}).get("vni", "")),
    "RT": lambda x: str((x.get("driver_spec") or {}).get("rt", "")),
    "MTU": lambda x: str((x.get("driver_spec") or {}).get("mtu", "")),
    "Access": "access",
    "Project": "project_id",
}

networks_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@networks_group.command("add", help="Add a new network")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the network")
@click.option("-n", "--name", type=str, required=True, help="Name of the network")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option(
    "--mtu",
    type=int,
    default=None,
    help="Overlay MTU (default: underlay MTU - 50, allocated by the core)",
)
@click.option(
    "--access",
    type=click.Choice(["private", "public"]),
    default="private",
    show_default=True,
    help="private: this project only; public: visible/allocatable to everyone",
)
def network_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    mtu: int | None,
    access: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    # The only driver the core makes over its API; a flat network is the
    # operator's, set up by bootstrap.
    driver_spec: dict = {"driver": "ovs_evpn"}
    if mtu is not None:
        driver_spec["mtu"] = mtu
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "driver_spec": driver_spec,
        "access": access,
    }
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))
