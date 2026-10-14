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
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.network import bindings
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

bindings.add_binding_commands(
    security_groups_group,
    c.PORT_SECURITY_GROUP_COLLECTION,
    ENTITY_COLLECTION,
    "security_group",
)


@security_groups_group.command("add", help="Add a new security group")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the group")
@click.option("-n", "--name", type=str, required=True, help="Name of the group")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
def security_group_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
) -> None:
    """A group with no rules denies everything but the established traffic —
    attaching one to a port is what turns filtering on."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
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
    show_data(
        base_client.add_entity(
            client,
            c.SECURITY_GROUP_RULE_COLLECTION,
            {
                "uuid": str(sys_uuid.uuid4()),
                "project_id": entity["project_id"],
                "security_group": entity["uuid"],
                **rule,
            },
        )
    )


@security_groups_group.command("rule-del", help="Remove an allow rule from a group")
@click.pass_context
@click.argument("group", type=str)
@click.argument("spec", type=str)
def rule_del_cmd(ctx: click.Context, group: str, spec: str) -> None:
    """SPEC: a rule UUID or the rule as `list` shows it, e.g. ingress:tcp:22."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entity = base_client.get_entity(client, ENTITY_COLLECTION, group)
    if utils.is_valid_uuid(spec):
        matches = base_client.list_entities(
            client,
            c.SECURITY_GROUP_RULE_COLLECTION,
            security_group=entity["uuid"],
            uuid=spec,
        )
    else:
        rule = net_common.resolve_rule(client, net_common.parse_filter_rule(spec))
        rules = base_client.list_entities(
            client, c.SECURITY_GROUP_RULE_COLLECTION, security_group=entity["uuid"]
        )
        fields = ("direction", "protocol", "port", "remote_ip", "remote_group")
        matches = [
            row for row in rules if all(row.get(key) == rule.get(key) for key in fields)
        ]
    if not matches:
        raise click.ClickException(f"No such rule: {spec}")
    if len(matches) != 1:
        raise click.ClickException("Multiple matching rules found; give a rule UUID")
    base_client.delete_entity(
        client, c.SECURITY_GROUP_RULE_COLLECTION, matches[0]["uuid"]
    )
