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
"""Identity groups: what a port *is*, as opposed to what it may do.

A port joins one, and a security-group rule names the group instead of
listing the addresses of whoever is in it. The number the group travels as
belongs to the fabric and is allocated by the platform — there is no option
to choose it, because a number chosen by hand could collide with another
project's group and hand its access away.
"""

from __future__ import annotations

import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.network import common as net_common
from exordos.common.table import show_data

ENTITY = "identity_group"
ENTITY_COLLECTION = c.IDENTITY_GROUP_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Network": "network",
    "Description": "description",
    "Project": "project_id",
}

identity_groups_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    group_name="identity-groups",
)


@identity_groups_group.command("add", help="Add a new identity group")
@click.pass_context
@click.option("-u", "--uuid", type=click.UUID, default=None, help="UUID of the group")
@click.option("-n", "--name", type=str, required=True, help="Name of the group")
@click.option("-D", "--description", type=str, default="", help="Description")
@click.option("-p", "--project-id", type=click.UUID, required=True, help="Project UUID")
@click.option(
    "-N",
    "--network",
    type=str,
    required=True,
    help="Network the group belongs to (UUID or name)",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    network: str,
) -> None:
    """A name for a set of workloads. Ports join it with
    `network ports update <port> --identity-group <name>`, and a rule admits
    it with `network sg rule-add <group> ingress:tcp:5432@<name>`."""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {
        "uuid": str(uuid or sys_uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "network": net_common.resolve(client, c.NETWORK_COLLECTION, network),
    }
    show_data(base_client.add_entity(client, ENTITY_COLLECTION, data))
