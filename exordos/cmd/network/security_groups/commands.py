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

ENTITY = "security_group"
ENTITY_COLLECTION = c.SECURITY_GROUP_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Rules": lambda x: ", ".join(
        net_common.format_rule(r) for r in x.get("rules") or []
    ),
    "Project": "project_id",
}

security_groups_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    group_name="security-groups",
)

RULE_HELP = (
    "Allow rule <ingress|egress>:<tcp|udp|icmp|any>[:<port>]"
    "[@<remote_cidr>|@<identity_group>], e.g. ingress:tcp:22 or "
    "ingress:tcp:5432@db (repeatable). Naming a group is ingress-only: what "
    "a packet carries is its sender's identity."
)


@security_groups_group.command("add", help="Add a new security group")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the group")
@click.option("-n", "--name", type=str, required=True, help="Name of the group")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option("-r", "--rule", "rule_specs", multiple=True, help=RULE_HELP)
def security_group_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    rule_specs: tuple[str, ...],
) -> None:
    """A group with no rules denies everything but the established traffic —
    attaching one to a port is what turns filtering on."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "rules": [
            net_common.resolve_rule(client, net_common.parse_filter_rule(r))
            for r in rule_specs
        ],
    }
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))


@security_groups_group.command("rule-add", help="Add an allow rule to a group")
@click.pass_context
@click.argument("group", type=str)
@click.argument("spec", type=str)
def rule_add_cmd(ctx: click.Context, group: str, spec: str) -> None:
    """SPEC: <ingress|egress>:<proto>[:<port>][@<remote_cidr>|@<group>]."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    rule = net_common.resolve_rule(client, net_common.parse_filter_rule(spec))
    entity = base_client.get_entity(client, ENTITY_COLLECTION, group)
    rules = [r for r in entity.get("rules") or [] if r != rule]
    rules.append(rule)
    show_data(
        base_client.update_entity(client, ENTITY_COLLECTION, group, {"rules": rules})
    )


@security_groups_group.command("rule-del", help="Remove an allow rule from a group")
@click.pass_context
@click.argument("group", type=str)
@click.argument("spec", type=str)
def rule_del_cmd(ctx: click.Context, group: str, spec: str) -> None:
    """SPEC: the rule as `list` shows it, e.g. ingress:tcp:22."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    rule = net_common.resolve_rule(client, net_common.parse_filter_rule(spec))
    entity = base_client.get_entity(client, ENTITY_COLLECTION, group)
    rules = entity.get("rules") or []
    kept = [r for r in rules if r != rule]
    if len(kept) == len(rules):
        raise click.ClickException(f"No such rule: {spec}")
    show_data(
        base_client.update_entity(client, ENTITY_COLLECTION, group, {"rules": kept})
    )
