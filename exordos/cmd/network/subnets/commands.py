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

ENTITY = "subnet"
ENTITY_COLLECTION = c.SUBNET_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Network": "network",
    "CIDR": "cidr",
    "DHCP": "dhcp",
    # Optional fields are read through callables: the API omits an unset one
    # entirely, and a plain key would then blow up on the row that lacks it.
    "IP range": lambda x: str(x.get("ip_range") or ""),
    "Routers": lambda x: ", ".join(
        f"{r.get('to')} via {r.get('via')}" for r in x.get("routers") or []
    ),
    "DNS": lambda x: ", ".join(x.get("dns_servers") or []),
}

subnets_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


def _parse_router(spec: str) -> dict:
    """``<destination_cidr>=<next_hop>``, e.g. ``0.0.0.0/0=10.100.0.1``."""
    to, sep, via = spec.partition("=")
    if not sep or not to or not via:
        raise click.ClickException(
            f"Invalid route: {spec!r} (expected <destination_cidr>=<next_hop>)"
        )
    return {"to": to, "via": via}


@subnets_group.command("add", help="Add a new subnet to a network")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the subnet")
@click.option("-n", "--name", type=str, required=True, help="Name of the subnet")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option(
    "-N",
    "--network",
    type=str,
    required=True,
    help="Network the subnet belongs to (UUID or name)",
)
@click.option("-c", "--cidr", type=str, required=True, help="CIDR, e.g. 10.100.0.0/24")
@click.option(
    "--dhcp/--no-dhcp",
    default=True,
    show_default=True,
    help="Serve the guests of this subnet from the host-local DHCP responder",
)
@click.option(
    "--ip-range",
    type=str,
    default=None,
    help="Allocation range <first>-<last>, e.g. 10.100.0.20-10.100.0.200",
)
@click.option(
    "-r",
    "--router",
    "router_specs",
    multiple=True,
    help="Route handed out over DHCP: <destination_cidr>=<next_hop>",
)
@click.option(
    "-s",
    "--dns-server",
    "dns_servers",
    multiple=True,
    help="Resolver handed out over DHCP (repeatable)",
)
@click.option(
    "--pool-only",
    is_flag=True,
    default=False,
    help="Hand out addresses only — never place nodes in this subnet",
)
@click.option(
    "--shared-pool",
    is_flag=True,
    default=False,
    help=(
        "Let projects that do not own this subnet take addresses out of it — "
        "what an ingress pool of floating addresses is for. Narrower than "
        "publishing the whole network, which opens every subnet of it"
    ),
)
def subnet_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    network: str,
    cidr: str,
    dhcp: bool,
    ip_range: str | None,
    router_specs: tuple[str, ...],
    dns_servers: tuple[str, ...],
    pool_only: bool,
    shared_pool: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "network": net_common.resolve(client, c.NETWORK_COLLECTION, network),
        "cidr": cidr,
        "dhcp": dhcp,
        "routers": [_parse_router(r) for r in router_specs],
        "dns_servers": list(dns_servers),
        "placeable": not pool_only,
        "shared_pool": shared_pool,
    }
    if ip_range:
        data["ip_range"] = ip_range
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))
