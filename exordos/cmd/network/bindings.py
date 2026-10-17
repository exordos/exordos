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
"""Independent security and security group bindings for ports."""

import uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.network import common as net_common
from exordos.common.table import show_data


def add_binding_commands(
    group, collection: str, group_collection: str, group_field: str
) -> None:
    @group.command("bind", help="Bind this group to a port")
    @click.pass_context
    @click.argument("group_ref")
    @click.argument("port")
    def bind_cmd(ctx, group_ref: str, port: str) -> None:
        client = base_client.get_user_api_client(ctx.obj.auth_data)
        entity = base_client.get_entity(client, c.PORT_COLLECTION, port)
        group_uuid = net_common.resolve(client, group_collection, group_ref)
        show_data(
            base_client.add_entity(
                client,
                collection,
                {
                    "uuid": str(uuid.uuid4()),
                    "project_id": entity["project_id"],
                    "port": entity["uuid"],
                    group_field: group_uuid,
                },
            )
        )

    @group.command("unbind", help="Unbind this group from a port")
    @click.pass_context
    @click.argument("group_ref")
    @click.argument("port")
    def unbind_cmd(ctx, group_ref: str, port: str) -> None:
        client = base_client.get_user_api_client(ctx.obj.auth_data)
        entity = base_client.get_entity(client, c.PORT_COLLECTION, port)
        group_uuid = net_common.resolve(client, group_collection, group_ref)
        bindings = base_client.list_entities(
            client,
            collection,
            project_id=entity["project_id"],
            port=entity["uuid"],
            **{group_field: group_uuid},
        )
        if not bindings:
            raise click.ClickException(f"Group {group_ref} is not bound to port {port}")
        base_client.delete_entity(client, collection, bindings[0]["uuid"])
