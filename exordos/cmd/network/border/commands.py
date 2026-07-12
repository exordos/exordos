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


# ---------------------------------------------------------------------------
# border
#
# SNAT/DNAT rules are carried inline on the Border resource (no nested
# sub-collections), so rule editing is read-modify-update on the border.
# ---------------------------------------------------------------------------
BORDER_FIELDS = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Status": "status",
    "Node": "node",
    "Type": "type",
    "IPs": "ipsv4",
}

borders_group = create_entity_group("border", c.BORDER_COLLECTION, BORDER_FIELDS)


def _parse_snat(spec: str) -> dict:
    """`<source_cidr>` -> masquerade, `<source_cidr>=<addr>` -> snat to addr."""
    cidr, sep, snat_to = spec.partition("=")
    if not cidr or (sep and not snat_to):
        raise click.ClickException(f"Invalid SNAT spec: {spec!r}")
    return {
        "source_cidr": cidr,
        "mode": "snat" if sep else "masquerade",
        "snat_to": snat_to or None,
    }


def _parse_forward(spec: str) -> dict:
    """`<proto>:<listen_port>:<to_host>:<to_port>[@<public_ip>][+nat]`.

    `+nat` full-NATs the forwarded flow (needed when the target does not
    route replies back through the border, e.g. a VM gateway DNAT'ing to
    a host outside its private subnet).
    """
    full_nat = spec.endswith("+nat")
    if full_nat:
        spec_body = spec[: -len("+nat")]
    else:
        spec_body = spec
    body, sep, public_ip = spec_body.partition("@")
    parts = body.split(":")
    if len(parts) != 4 or parts[0] not in ("tcp", "udp") or (sep and not public_ip):
        raise click.ClickException(
            f"Invalid forward spec: {spec!r} (expected "
            "<tcp|udp>:<listen_port>:<to_host>:<to_port>[@<public_ip>][+nat])"
        )
    proto, listen_port, to_host, to_port = parts
    try:
        fwd = {
            "proto": proto,
            "public_ip": public_ip or None,
            "listen_port": int(listen_port),
            "to_host": to_host,
            "to_port": int(to_port),
        }
    except ValueError:
        raise click.ClickException(f"Invalid port in forward spec: {spec!r}")
    if full_nat:
        fwd["full_nat"] = True
    return fwd


@borders_group.command("add", help="Add a new border (NAT gateway)")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the border")
@click.option("-n", "--name", type=str, default="border", help="Name of the border")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option(
    "-p", "--project-id", type=click.UUID, required=True, help="Project UUID"
)
@click.option(
    "--node",
    type=click.UUID,
    default=None,
    help="Target compute node (border_node); wins over --kind",
)
@click.option(
    "-k",
    "--kind",
    type=click.Choice(["core_agent", "core"]),
    default="core_agent",
    show_default=True,
    help="core_agent: the core node's agent; core: a dedicated VM gateway",
)
@click.option("--cpu", type=int, default=1, show_default=True, help="VM vCPUs (kind=core)")
@click.option("--ram", type=int, default=512, show_default=True, help="VM RAM MB (kind=core)")
@click.option(
    "--disk-size", type=int, default=10, show_default=True, help="VM disk GB (kind=core)"
)
@click.option(
    "-s",
    "--snat",
    "snat_specs",
    multiple=True,
    help="SNAT rule: <source_cidr> (masquerade) or <source_cidr>=<snat_to>",
)
@click.option(
    "-f",
    "--forward",
    "forward_specs",
    multiple=True,
    help="DNAT forward: <tcp|udp>:<listen_port>:<to_host>:<to_port>[@<public_ip>]",
)
def border_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    node: sys_uuid.UUID | None,
    kind: str,
    cpu: int,
    ram: int,
    disk_size: int,
    snat_specs: tuple[str, ...],
    forward_specs: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if kind == "core":
        border_type = {
            "kind": "core",
            "cpu": cpu,
            "ram": ram,
            "disk_size": disk_size,
        }
    else:
        border_type = {"kind": "core_agent"}
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "type": border_type,
        "snat_rules": [_parse_snat(s) for s in snat_specs],
        "forwards": [_parse_forward(f) for f in forward_specs],
    }
    if node:
        data["node"] = str(node)
    show_data(base_client.add_entity(client, c.BORDER_COLLECTION, data))


def _update_rules(ctx: click.Context, border: str, field: str, rules: list) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    show_data(
        base_client.update_entity(client, c.BORDER_COLLECTION, border, {field: rules})
    )


def _get_border(ctx: click.Context, border: str) -> dict:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    return base_client.get_entity(client, c.BORDER_COLLECTION, border)


@borders_group.command("snat-add", help="Add a SNAT rule to a border")
@click.pass_context
@click.argument("border", type=str)
@click.argument("spec", type=str)
def snat_add_cmd(ctx: click.Context, border: str, spec: str) -> None:
    """SPEC: <source_cidr> (masquerade) or <source_cidr>=<snat_to>."""
    rule = _parse_snat(spec)
    entity = _get_border(ctx, border)
    rules = [
        r for r in entity.get("snat_rules") or [] if r["source_cidr"] != rule["source_cidr"]
    ]
    rules.append(rule)
    _update_rules(ctx, border, "snat_rules", rules)


@borders_group.command("snat-del", help="Remove a SNAT rule (by source CIDR)")
@click.pass_context
@click.argument("border", type=str)
@click.argument("source_cidr", type=str)
def snat_del_cmd(ctx: click.Context, border: str, source_cidr: str) -> None:
    entity = _get_border(ctx, border)
    rules = entity.get("snat_rules") or []
    kept = [r for r in rules if r["source_cidr"] != source_cidr]
    if len(kept) == len(rules):
        raise click.ClickException(f"No SNAT rule for {source_cidr}")
    _update_rules(ctx, border, "snat_rules", kept)


@borders_group.command("forward-add", help="Add a DNAT forward to a border")
@click.pass_context
@click.argument("border", type=str)
@click.argument("spec", type=str)
def forward_add_cmd(ctx: click.Context, border: str, spec: str) -> None:
    """SPEC: <tcp|udp>:<listen_port>:<to_host>:<to_port>[@<public_ip>]."""
    fwd = _parse_forward(spec)
    entity = _get_border(ctx, border)
    forwards = [
        f
        for f in entity.get("forwards") or []
        if (f["proto"], f["listen_port"]) != (fwd["proto"], fwd["listen_port"])
    ]
    forwards.append(fwd)
    _update_rules(ctx, border, "forwards", forwards)


@borders_group.command(
    "forward-del", help="Remove a DNAT forward (by <tcp|udp>:<listen_port>)"
)
@click.pass_context
@click.argument("border", type=str)
@click.argument("listen", type=str)
def forward_del_cmd(ctx: click.Context, border: str, listen: str) -> None:
    proto, _sep, port = listen.partition(":")
    if proto not in ("tcp", "udp") or not port.isdigit():
        raise click.ClickException(
            f"Invalid forward key: {listen!r} (expected <tcp|udp>:<listen_port>)"
        )
    entity = _get_border(ctx, border)
    forwards = entity.get("forwards") or []
    kept = [
        f for f in forwards if (f["proto"], f["listen_port"]) != (proto, int(port))
    ]
    if len(kept) == len(forwards):
        raise click.ClickException(f"No forward on {listen}")
    _update_rules(ctx, border, "forwards", kept)
