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

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.network import common as net_common
from exordos.common.table import show_data

ENTITY = "network_function"
ENTITY_COLLECTION = c.NF_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Kind": "kind",
    "Config": "config",
    "Provenance": "provenance",
    "Owner port": lambda x: str(x.get("owner_port") or ""),
}

nfs_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    group_name="nfs",
)


# No `add`: a function is not made on its own. A subnet is seeded with its
# DHCP and its default security group, a network with its resolver and its
# metadata proxy, and a port with what it expands into — so what there is to
# do here is find the one that already serves the object you mean and change
# what it answers with.
@nfs_group.command("set", help="Change what a network function answers with")
@click.pass_context
@click.argument("nf", type=str)
@click.option(
    "-r",
    "--rule",
    "rule_specs",
    multiple=True,
    help=(
        "splitter: the allow-list, as <ingress|egress>:<tcp|udp|icmp|any>"
        "[:<port>][@<remote_cidr>|@<identity_group>] (repeatable; "
        "replaces the whole list)"
    ),
)
@click.option(
    "--forwarder",
    "forwarders",
    multiple=True,
    help="dns: an upstream resolver of this network (repeatable, replaces)",
)
@click.option("--zone-suffix", default=None, help="dns: the internal zone's suffix")
@click.option(
    "--platform-name",
    "platform_names",
    multiple=True,
    help="dns: a name of the installation itself (repeatable, replaces)",
)
@click.option("--filename", default=None, help="dhcp: the netboot script to chain to")
@click.option(
    "--lease-seconds", type=int, default=None, help="dhcp: how long a lease is held"
)
@click.option(
    "-a",
    "--address",
    default=None,
    help="fip: the address object (UUID) or a literal IP",
)
def nf_set_cmd(
    ctx: click.Context,
    nf: str,
    rule_specs: tuple[str, ...],
    forwarders: tuple[str, ...],
    zone_suffix: str | None,
    platform_names: tuple[str, ...],
    filename: str | None,
    lease_seconds: int | None,
    address: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entity = base_client.get_entity(client, ENTITY_COLLECTION, nf)
    config = dict(entity.get("config") or {})
    if rule_specs:
        config["rules"] = [
            net_common.resolve_rule(client, net_common.parse_filter_rule(r))
            for r in rule_specs
        ]
    if forwarders:
        config["forwarders"] = list(forwarders)
    if zone_suffix is not None:
        config["zone_suffix"] = zone_suffix
    if platform_names:
        config["platform_names"] = list(platform_names)
    if filename is not None:
        config["filename"] = filename
    if lease_seconds is not None:
        config["lease_seconds"] = lease_seconds
    if address is not None:
        config["address"] = address
    if config == (entity.get("config") or {}):
        raise click.ClickException("Nothing to change; pass at least one setting")
    show_data(
        base_client.update_entity(client, ENTITY_COLLECTION, nf, {"config": config})
    )
