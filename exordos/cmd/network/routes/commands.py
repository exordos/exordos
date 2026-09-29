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

import json
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "route"
ENTITY_COLLECTION = c.ROUTE_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Condition": "condition",
    "Enabled": "enabled",
    "Status": "status",
}


routes_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, parents=["lb", "vhost"]
)


def _condition_options(f):
    """Options describing the route condition."""
    options = [
        click.option(
            "--condition",
            type=str,
            default=None,
            help="Full condition as a JSON string, other condition options are ignored",
        ),
        click.option(
            "--kind",
            type=click.Choice(["prefix", "exact", "regex", "raw"]),
            default="prefix",
            show_default=True,
            help="Condition kind, 'raw' is for tcp/udp vhosts",
        ),
        click.option(
            "--value",
            type=str,
            default="/",
            show_default=True,
            help="Path to match (ignored for 'raw' kind)",
        ),
        click.option("--pool", type=click.UUID, default=None, help="Backend pool UUID"),
        click.option(
            "--backend-protocol",
            type=click.Choice(["http", "https"]),
            default="http",
            show_default=True,
            help="Protocol used to reach the backend pool",
        ),
        click.option(
            "--allowed-ip",
            "allowed_ips",
            multiple=True,
            help="CIDR allowed to access the route, may be repeated",
        ),
    ]
    for option in reversed(options):
        f = option(f)
    return f


def _build_condition(
    condition: str | None,
    kind: str,
    value: str,
    pool: sys_uuid.UUID | None,
    backend_protocol: str,
    allowed_ips: tuple[str, ...],
) -> dict:
    if condition is not None:
        try:
            return json.loads(condition)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON string: '{condition}': {e}")

    if pool is None:
        raise click.ClickException("Either --condition or --pool must be provided")

    action = {"kind": "backend", "pool": str(pool)}
    result = {"kind": kind, "actions": [action]}
    if kind != "raw":
        action["protocol"] = {"kind": backend_protocol}
        result["value"] = value
    if allowed_ips:
        result["allowed_ips"] = list(allowed_ips)
    return result


@click.command("add", help=f"Add a new {ENTITY}")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the route")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option("--lb-uuid", type=click.UUID, required=True, help="Load balancer UUID")
@click.option("--vhost-uuid", type=click.UUID, required=True, help="Vhost UUID")
@click.option("-n", "--name", type=str, default="", help="Name of the route")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("--disabled", is_flag=True, default=False, help="Create disabled route")
@_condition_options
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    lb_uuid: sys_uuid.UUID,
    vhost_uuid: sys_uuid.UUID,
    name: str,
    description: str,
    disabled: bool,
    condition: str | None,
    kind: str,
    value: str,
    pool: sys_uuid.UUID | None,
    backend_protocol: str,
    allowed_ips: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "enabled": not disabled,
        "condition": _build_condition(
            condition, kind, value, pool, backend_protocol, allowed_ips
        ),
    }
    entity = base_client.add_entity(
        client,
        ENTITY_COLLECTION.format(lb_uuid=lb_uuid, vhost_uuid=vhost_uuid),
        data,
    )
    show_data(entity)


routes_group.add_command(add_cmd, aliases=["a", "create"])


@click.command(
    "update",
    help=(
        f"Update {ENTITY}. Passing --condition or --pool replaces "
        "the whole route condition"
    ),
)
@click.pass_context
@click.argument("uuid", type=str, required=True)
@click.option("--lb-uuid", type=click.UUID, required=True, help="Load balancer UUID")
@click.option("--vhost-uuid", type=click.UUID, required=True, help="Vhost UUID")
@click.option("-n", "--name", type=str, default=None, help="Name of the route")
@click.option("-D", "--description", type=str, default=None, help="Description")
@click.option("--enabled/--disabled", default=None, help="Enable or disable the route")
@_condition_options
def update_cmd(
    ctx: click.Context,
    uuid: str,
    lb_uuid: sys_uuid.UUID,
    vhost_uuid: sys_uuid.UUID,
    name: str | None,
    description: str | None,
    enabled: bool | None,
    condition: str | None,
    kind: str,
    value: str,
    pool: sys_uuid.UUID | None,
    backend_protocol: str,
    allowed_ips: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {"name": name, "description": description, "enabled": enabled}
    data = {k: v for k, v in data.items() if v is not None}
    if condition is not None or pool is not None:
        data["condition"] = _build_condition(
            condition, kind, value, pool, backend_protocol, allowed_ips
        )
    entity = base_client.update_entity(
        client,
        ENTITY_COLLECTION.format(lb_uuid=lb_uuid, vhost_uuid=vhost_uuid),
        uuid,
        data,
    )
    show_data(entity)


routes_group.add_command(update_cmd, aliases=["u"])
