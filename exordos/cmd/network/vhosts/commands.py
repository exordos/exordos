#    Copyright 2025 Genesis Corporation.
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

import typing as tp
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "vhost"
ENTITY_COLLECTION = c.VHOST_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Protocol": "protocol",
    "Port": "port",
    "Domains": lambda x: str(x.get("domains", "")),
    "Enabled": "enabled",
    "External Sources": "external_sources",
    "Status": "status",
}

vhosts_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, add_clear_command=True, parents=["lb"]
)


def _cert(cert: tp.TextIO | None, key: tp.TextIO | None) -> dict | None:
    if cert is None and key is None:
        return None
    if cert is None or key is None:
        raise click.ClickException("Both --cert and --key must be provided")
    return {"kind": "raw", "crt": cert.read(), "key": key.read()}


@click.command("add", help=f"Add a new {ENTITY}")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the vhost")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option("--lb-uuid", type=click.UUID, required=True, help="Load balancer UUID")
@click.option("-n", "--name", type=str, default="", help="Name of the vhost")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option(
    "--protocol",
    type=click.Choice(["http", "https", "tcp", "udp"]),
    default="http",
    show_default=True,
    help="Protocol of the vhost",
)
@click.option("--port", type=click.IntRange(80, 65535), default=80, show_default=True)
@click.option(
    "--domain",
    "domains",
    multiple=True,
    help="Domain served by the vhost (required for http/https), may be repeated",
)
@click.option("--cert", type=click.File("r"), default=None, help="PEM certificate file")
@click.option("--key", type=click.File("r"), default=None, help="PEM private key file")
@click.option(
    "--proxy-protocol-from",
    type=str,
    default=None,
    help="CIDR allowed to send PROXY protocol headers, e.g. 10.0.0.1/32",
)
@click.option("--disabled", is_flag=True, default=False, help="Create disabled vhost")
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    lb_uuid: sys_uuid.UUID,
    name: str,
    description: str,
    protocol: str,
    port: int,
    domains: tuple[str, ...],
    cert: tp.TextIO | None,
    key: tp.TextIO | None,
    proxy_protocol_from: str | None,
    disabled: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "protocol": protocol,
        "port": port,
        "domains": list(domains) or None,
        "cert": _cert(cert, key),
        "proxy_protocol_from": proxy_protocol_from,
        "enabled": not disabled,
    }
    entity = base_client.add_entity(
        client, ENTITY_COLLECTION.format(lb_uuid=lb_uuid), data
    )
    show_data(entity)


vhosts_group.add_command(add_cmd, aliases=["a", "create"])


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument("uuid", type=str, required=True)
@click.option("--lb-uuid", type=click.UUID, required=True, help="Load balancer UUID")
@click.option("-n", "--name", type=str, default=None, help="Name of the vhost")
@click.option("-D", "--description", type=str, default=None, help="Description")
@click.option("--port", type=click.IntRange(80, 65535), default=None)
@click.option(
    "--domain",
    "domains",
    multiple=True,
    help="Domain served by the vhost, replaces the current list, may be repeated",
)
@click.option("--cert", type=click.File("r"), default=None, help="PEM certificate file")
@click.option("--key", type=click.File("r"), default=None, help="PEM private key file")
@click.option(
    "--proxy-protocol-from",
    type=str,
    default=None,
    help="CIDR allowed to send PROXY protocol headers, e.g. 10.0.0.1/32",
)
@click.option("--enabled/--disabled", default=None, help="Enable or disable the vhost")
def update_cmd(
    ctx: click.Context,
    uuid: str,
    lb_uuid: sys_uuid.UUID,
    name: str | None,
    description: str | None,
    port: int | None,
    domains: tuple[str, ...],
    cert: tp.TextIO | None,
    key: tp.TextIO | None,
    proxy_protocol_from: str | None,
    enabled: bool | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "name": name,
        "description": description,
        "port": port,
        "domains": list(domains) or None,
        "cert": _cert(cert, key),
        "proxy_protocol_from": proxy_protocol_from,
        "enabled": enabled,
    }
    data = {k: v for k, v in data.items() if v is not None}
    entity = base_client.update_entity(
        client, ENTITY_COLLECTION.format(lb_uuid=lb_uuid), uuid, data
    )
    show_data(entity)


vhosts_group.add_command(update_cmd, aliases=["u"])
