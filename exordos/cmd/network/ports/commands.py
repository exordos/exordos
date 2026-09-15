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
    "Node": "node",
    # Optional fields are omitted from the response until they are set.
    "Machine": lambda x: str(x.get("machine") or ""),
    "Subnet": "subnet",
    "IPv4": lambda x: str(x.get("ipv4") or ""),
    "MAC": lambda x: str(x.get("mac") or ""),
    "Groups": lambda x: ", ".join((x.get("config") or {}).get("security_groups") or []),
    "Identity": lambda x: ", ".join(
        (x.get("config") or {}).get("identity_groups") or []
    ),
    "Status": "status",
}

ports_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


def _config_options(f):
    """The knobs of the `simple` port kind — shared by add and update."""
    options = [
        click.option(
            "-g",
            "--security-group",
            "security_groups",
            multiple=True,
            help="Security group to apply (UUID or name, repeatable)",
        ),
        click.option(
            "--identity-group",
            "identity_groups",
            multiple=True,
            help=(
                "A group this port belongs to (UUID or name, repeatable); "
                "rules elsewhere admit it by that name. Its subnet's default "
                "group is always included, so joining one adds access rather "
                "than trading the subnet's away."
            ),
        ),
        click.option(
            "--subnet-group/--no-subnet-group",
            default=None,
            help=(
                "Belong to the subnet's default group as well (the default). "
                "--no-subnet-group leaves it: the port is then reachable only "
                "where a rule names a group it is actually in."
            ),
        ),
        click.option(
            "--dhcp/--no-dhcp",
            default=None,
            help="Override the subnet's DHCP setting for this port",
        ),
        click.option(
            "--dns/--no-dns",
            default=None,
            help="Serve this port from the host-local resolver",
        ),
        click.option(
            "--public-address",
            type=str,
            default=None,
            help="Give the port a floating IP: an existing address object (UUID)",
        ),
        click.option(
            "--floating-from",
            type=str,
            default=None,
            help="Give the port a floating IP taken out of this subnet",
        ),
        click.option(
            "--no-public",
            is_flag=True,
            default=False,
            help="Take the port's floating IP away (the address stays allocated)",
        ),
    ]
    for option in reversed(options):
        f = option(f)
    return f


def _build_config(
    client,
    security_groups: tuple[str, ...],
    identity_groups: tuple[str, ...],
    subnet_group: bool | None,
    dhcp: bool | None,
    dns: bool | None,
    public_address: str | None,
    floating_from: str | None,
    no_public: bool = False,
    base: dict | None = None,
) -> dict:
    """Merge the given knobs into a `simple` config (kept whole: the kind is
    a polymorphic field, so a partial update would drop the rest)."""
    if sum(bool(x) for x in (public_address, floating_from, no_public)) > 1:
        raise click.ClickException(
            "--public-address, --floating-from and --no-public are mutually exclusive"
        )
    config = dict(base or {})
    config["kind"] = "simple"
    if security_groups:
        config["security_groups"] = [
            net_common.resolve(client, c.SECURITY_GROUP_COLLECTION, sg)
            for sg in security_groups
        ]
    config.setdefault("security_groups", [])
    if identity_groups:
        config["identity_groups"] = [
            net_common.resolve(client, c.IDENTITY_GROUP_COLLECTION, group)
            for group in identity_groups
        ]
    if subnet_group is not None:
        config["subnet_group"] = subnet_group
    if dhcp is not None:
        config["dhcp"] = dhcp
    if dns is not None:
        config["dns"] = dns
    if no_public:
        config["public"] = None
    elif public_address:
        config["public"] = {
            "address": net_common.resolve(client, c.ADDRESS_COLLECTION, public_address)
        }
    elif floating_from:
        config["public"] = {
            "floating_from": net_common.resolve(
                client, c.SUBNET_COLLECTION, floating_from
            )
        }
    return config


@ports_group.command("add", help="Add a port (a NIC on a subnet) to a node")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the port")
@click.option("-n", "--name", type=str, default=None, help="Name (also its DNS name)")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option(
    "-s", "--subnet", type=str, required=True, help="Subnet to attach to (UUID or name)"
)
@click.option(
    "-N",
    "--node",
    type=str,
    required=True,
    help="Node the port belongs to (its machine gets the NIC)",
)
@click.option(
    "--mac", type=str, default=None, help="MAC address (generated if omitted)"
)
@click.option(
    "--ipv4",
    type=str,
    default=None,
    help="Fixed address (allocated from the subnet if omitted)",
)
@click.option(
    "--port-security/--no-port-security",
    default=True,
    show_default=True,
    help="Anti-spoofing: only the port's own MAC/IP may be sourced",
)
@_config_options
def port_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str | None,
    description: str,
    project_id: sys_uuid.UUID,
    subnet: str,
    node: str,
    mac: str | None,
    ipv4: str | None,
    port_security: bool,
    security_groups: tuple[str, ...],
    identity_groups: tuple[str, ...],
    subnet_group: bool | None,
    dhcp: bool | None,
    dns: bool | None,
    public_address: str | None,
    floating_from: str | None,
    no_public: bool,
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
        "config": _build_config(
            client,
            security_groups,
            identity_groups,
            subnet_group,
            dhcp,
            dns,
            public_address,
            floating_from,
            no_public,
        ),
    }
    if mac:
        data["mac"] = mac
    if ipv4:
        data["ipv4"] = ipv4
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))


@ports_group.command("update", help="Update a port's groups and toggles")
@click.pass_context
@click.argument("port", type=str)
@click.option(
    "--port-security/--no-port-security",
    default=None,
    help="Anti-spoofing: only the port's own MAC/IP may be sourced",
)
@_config_options
def port_update_cmd(
    ctx: click.Context,
    port: str,
    port_security: bool | None,
    security_groups: tuple[str, ...],
    identity_groups: tuple[str, ...],
    subnet_group: bool | None,
    dhcp: bool | None,
    dns: bool | None,
    public_address: str | None,
    floating_from: str | None,
    no_public: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entity = base_client.get_entity(client, ENTITY_COLLECTION, port)
    base = entity.get("config") or {}
    data: dict = {
        "config": _build_config(
            client,
            security_groups,
            identity_groups,
            subnet_group,
            dhcp,
            dns,
            public_address,
            floating_from,
            no_public,
            base=base,
        )
    }
    if port_security is not None:
        data["port_security"] = port_security
    show_data(base_client.update_entity(client, ENTITY_COLLECTION, port, data))
