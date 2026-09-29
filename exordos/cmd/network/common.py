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
"""Shared helpers for the SDN network commands.

Every SDN object cites the others by uuid (a subnet its network, a port its
subnet and its groups), which is unusable by hand — these resolve a name to
the uuid the API wants, and parse the compact rule syntax the filter
surfaces (security group, splitter function) share.
"""

from __future__ import annotations

import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client

DIRECTIONS = ("ingress", "egress")
PROTOCOLS = ("tcp", "udp", "icmp", "any")


def is_cidr(value: str) -> bool:
    """True for an address or a prefix — anything else names a group."""
    import ipaddress

    try:
        ipaddress.ip_network(str(value), strict=False)
    except ValueError:
        return False
    return True


def resolve(client, collection: str, ref: str) -> str:
    """Return the uuid of ``ref``, which may already be one or be a name."""
    if utils.is_valid_uuid(ref):
        return str(ref)
    return str(base_client.get_entity(client, collection, ref)["uuid"])


def parse_filter_rule(spec: str) -> dict:
    """``<ingress|egress>:<proto>[:<port>][@<remote_cidr>]``.

    The allow-list entry shared by security groups and splitter functions:
    ``ingress:tcp:22``, ``ingress:tcp:443@10.0.0.0/8``, ``egress:any``.
    """
    body, sep, remote_ip = spec.partition("@")
    parts = body.split(":")
    if len(parts) not in (2, 3) or (sep and not remote_ip):
        raise click.ClickException(
            f"Invalid rule: {spec!r} (expected "
            "<ingress|egress>:<tcp|udp|icmp|any>[:<port>][@<remote_cidr>])"
        )
    direction, protocol = parts[0], parts[1]
    if direction not in DIRECTIONS:
        raise click.ClickException(f"Invalid rule direction: {direction!r}")
    if protocol not in PROTOCOLS:
        raise click.ClickException(f"Invalid rule protocol: {protocol!r}")
    rule = {"direction": direction, "protocol": protocol}
    if len(parts) == 3:
        if not parts[2].isdigit():
            raise click.ClickException(f"Invalid rule port: {parts[2]!r}")
        rule["port"] = int(parts[2])
    if remote_ip:
        # "From where" and "from whom" share one place in the syntax,
        # because they answer the same question about a rule. An address or
        # a prefix stays an address; anything else names an identity group,
        # which the command resolves to its uuid before sending.
        if is_cidr(remote_ip):
            rule["remote_ip"] = remote_ip
        else:
            rule["remote_group_ref"] = remote_ip
    return rule


def resolve_rule(client, rule: dict) -> dict:
    """Turn a group named on the command line into the uuid the API wants."""
    ref = rule.pop("remote_group_ref", None)
    if ref is not None:
        rule["remote_group"] = resolve(client, c.IDENTITY_GROUP_COLLECTION, ref)
    return rule


def format_rule(rule: dict) -> str:
    """The inverse of :func:`parse_filter_rule`, for listings."""
    text = f"{rule.get('direction')}:{rule.get('protocol', 'any')}"
    if rule.get("port") is not None:
        text += f":{rule['port']}"
    if rule.get("remote_ip"):
        text += f"@{rule['remote_ip']}"
    if rule.get("remote_group"):
        text += f"@{rule['remote_group']}"
    return text


# What a `--interface` may say. Kept to what a leg is: where it goes, what
# address it takes, and what the port it makes is allowed to do. Anything
# richer belongs on the port, which has its own commands.
INTERFACE_KEYS = ("subnet", "network", "port", "address", "index", "sg", "public")

# What only a leg the node *builds* can say. An adopted port already has
# them, and it keeps its own: the node names it and nothing more.
BUILT_LEG_KEYS = ("subnet", "network", "address", "sg", "public")


def parse_interface(client, spec: str) -> dict:
    """``subnet=<ref>[,address=<ip>][,index=<n>][,sg=<ref>]…[,public=<ref>]``
    or ``port=<ref>[,index=<n>]``

    One `--interface` is one leg of the node. ``subnet`` is the ordinary
    way to say where it goes; ``network`` is accepted for the case of a
    network with a single placeable subnet, and the API refuses it with the
    candidates listed when there is more than one.

    ``port`` is the other kind of leg: one that already exists, which the
    node adopts rather than builds. It keeps its own configuration, so the
    keys that describe one are refused here rather than silently dropped --
    a caller who writes them means them, and the port is not going to take
    them. For the same reason the node releases such a port when it goes
    instead of deleting it.

    ``sg`` may be repeated within one interface — a port carries a set of
    groups, and a single one is not a special case worth a second spelling.
    """
    interface: dict = {"kind": "subnet"}
    config: dict = {"kind": "simple"}
    groups: list[str] = []
    said: list[str] = []

    for chunk in spec.split(","):
        key, sep, value = chunk.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not value:
            raise click.ClickException(
                f"Invalid interface part: {chunk!r} (expected <key>=<value>, "
                f"one of {', '.join(INTERFACE_KEYS)})"
            )
        said.append(key)
        if key == "subnet":
            interface["subnet"] = resolve(client, c.SUBNET_COLLECTION, value)
        elif key == "port":
            interface["port"] = resolve(client, c.PORT_COLLECTION, value)
        elif key == "network":
            interface["network"] = resolve(client, c.NETWORK_COLLECTION, value)
        elif key == "address":
            interface["address"] = value
        elif key == "index":
            if not value.isdigit():
                raise click.ClickException(
                    f"Invalid interface index: {value!r} (0 is the primary leg)"
                )
            interface["index"] = int(value)
        elif key == "sg":
            groups.append(resolve(client, c.SECURITY_GROUP_COLLECTION, value))
        elif key == "public":
            config["public"] = {"address": resolve(client, c.ADDRESS_COLLECTION, value)}
        else:
            raise click.ClickException(
                f"Unknown interface key: {key!r} "
                f"(expected one of {', '.join(INTERFACE_KEYS)})"
            )

    if "port" in interface:
        described = [key for key in said if key in BUILT_LEG_KEYS]
        if described:
            raise click.ClickException(
                f"Interface {spec!r} adopts an existing port, which keeps its "
                f"own configuration: drop {', '.join(sorted(set(described)))}="
                " or build a leg with subnet= instead"
            )
        interface["kind"] = "port"
        return interface

    if ("subnet" in interface) == ("network" in interface):
        raise click.ClickException(
            f"Interface {spec!r} must name exactly one of subnet= or network="
        )
    if groups:
        config["security_groups"] = groups
    if len(config) > 1:
        interface["config"] = config
    return interface
