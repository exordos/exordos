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

import json
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "network"
ENTITY_COLLECTION = c.NETWORK_COLLECTION

# Driver settings and allocated overlay state are separate API fields.
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Driver": lambda x: str((x.get("driver_spec") or {}).get("driver", "unknown")),
    "VNI": lambda x: str((x.get("driver_state") or {}).get("vni", "")),
    "RT": lambda x: str((x.get("driver_state") or {}).get("rt", "")),
    "MTU": lambda x: str((x.get("driver_state") or {}).get("mtu", "")),
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
@click.option(
    "--driver-spec-file",
    type=click.File("r"),
    default=None,
    help="JSON driver specification for a local network",
)
@click.option(
    "--cidr",
    default=None,
    help="Logical network address pool; subnets allocate /23 blocks",
)
@click.option("--connectivity", type=click.Choice(["auto", "openvpn"]), default=None)
def network_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    mtu: int | None,
    access: str,
    driver_spec_file=None,
    cidr=None,
    connectivity=None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    # Default to a local overlay when no driver specification is supplied.
    driver_spec: dict = {"driver": "ovs_evpn"}
    if mtu is not None:
        driver_spec["mtu"] = mtu
    if cidr is not None and (mtu is not None or driver_spec_file is not None):
        raise click.UsageError(
            "A logical network uses --cidr without a local driver specification"
        )
    if connectivity is not None and cidr is None:
        raise click.UsageError("--connectivity requires --cidr")
    if driver_spec_file is not None:
        if mtu is not None:
            raise click.UsageError(
                "Set MTU in the driver specification when using --driver-spec-file"
            )
        driver_spec = read_spec(driver_spec_file)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "driver_spec": driver_spec,
        "access": access,
    }
    if cidr is not None:
        data.pop("driver_spec")
        data["cidr"] = cidr
        if connectivity is not None:
            data["connectivity"] = {"driver": connectivity}
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))


def read_spec(source):
    try:
        value = json.load(source)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, TypeError):
        raise click.ClickException(
            "Driver specification must be a JSON object"
        ) from None


@networks_group.command(
    "update", help="Update network metadata or its complete driver specification"
)
@click.pass_context
@click.argument("network")
@click.option("--name", default=None)
@click.option("--description", default=None)
@click.option("--driver-spec-file", type=click.File("r"), default=None)
def network_update_cmd(ctx, network, name, description, driver_spec_file):
    data = {
        key: value
        for key, value in {"name": name, "description": description}.items()
        if value is not None
    }
    if driver_spec_file is not None:
        data["driver_spec"] = read_spec(driver_spec_file)
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    show_data(base_client.update_entity(client, ENTITY_COLLECTION, network, data))
