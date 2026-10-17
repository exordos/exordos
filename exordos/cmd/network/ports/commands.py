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

ENTITY = "port"
ENTITY_COLLECTION = c.PORT_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Node": lambda x: str(x.get("node") or ""),
    "Machine": lambda x: str(x.get("machine") or ""),
    "Subnet": "subnet",
    "IPv4": lambda x: str(x.get("ipv4") or ""),
    "MAC": lambda x: str(x.get("mac") or ""),
    "Groups": lambda x: ", ".join(x.get("security_groups") or []),
    "Status": "status",
}

ports_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


def _port_options(f):
    options = [
        click.option("--mac", "target_mac", default=None, help="Requested MAC address"),
        click.option(
            "--ipv4", "target_ipv4", default=None, help="Requested IPv4 address"
        ),
        click.option("--dhcp/--no-dhcp", default=None, help="Override subnet DHCP"),
        click.option("--dns/--no-dns", default=None, help="Serve host-local DNS"),
    ]
    for option in reversed(options):
        f = option(f)
    return f


@ports_group.command("add", help="Add a port (a NIC on a subnet) to a node")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the port")
@click.option("-n", "--name", type=str, default=None, help="Name (also its DNS name)")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option("-s", "--subnet", required=True, help="Subnet (UUID or name)")
@click.option("-N", "--node", required=True, help="Node (UUID or name)")
@click.option(
    "--port-security/--no-port-security",
    default=True,
    show_default=True,
    help="Allow only the port's own source MAC/IP",
)
@_port_options
def port_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str | None,
    description: str,
    project_id: sys_uuid.UUID,
    subnet: str,
    node: str,
    port_security: bool,
    **settings,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    port_uuid = uuid or sys_uuid.uuid4()
    data = {
        "uuid": str(port_uuid),
        "name": name or f"port-{str(port_uuid)[:8]}",
        "description": description,
        "project_id": str(project_id),
        "subnet": net_common.resolve(client, c.SUBNET_COLLECTION, subnet),
        "node": net_common.resolve(client, c.NODE_COLLECTION, node),
        "port_security": port_security,
        **{key: value for key, value in settings.items() if value is not None},
    }
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))


@ports_group.command("update", help="Update a port's requested addresses and toggles")
@click.pass_context
@click.argument("port", type=str)
@click.option(
    "--port-security/--no-port-security",
    default=None,
    help="Allow only the port's own source MAC/IP",
)
@_port_options
def port_update_cmd(ctx: click.Context, port: str, **settings) -> None:
    data = {key: value for key, value in settings.items() if value is not None}
    if not data:
        raise click.ClickException("Nothing to change; pass at least one setting")
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    show_data(base_client.update_entity(client, ENTITY_COLLECTION, port, data))
