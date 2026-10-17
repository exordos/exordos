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
        # a prefix stays an address; anything else names an security group,
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
        rule["remote_group_id"] = resolve(client, c.SECURITY_GROUP_COLLECTION, ref)
    return rule


def format_rule(rule: dict) -> str:
    """The inverse of :func:`parse_filter_rule`, for listings."""
    text = f"{rule.get('direction')}:{rule.get('protocol', 'any')}"
    if rule.get("port") is not None:
        text += f":{rule['port']}"
    if rule.get("remote_ip"):
        text += f"@{rule['remote_ip']}"
    if rule.get("remote_group_id"):
        text += f"@{rule['remote_group_id']}"
    return text
