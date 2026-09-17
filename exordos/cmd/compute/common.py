#    Copyright 2025-2026 Genesis Corporation.
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

from exordos.clients import base_client
from exordos.common.table import show_data

# CLI command name -> (API action, help)
POWER_ACTIONS = {
    "power-on": ("power_on", "Power on the {entity}"),
    "power-off": ("power_off", "Power off the {entity}"),
    "reboot": ("reboot", "Reboot the {entity}"),
}


def extract_disks_from_entity(entity: dict) -> str:
    """Extract disks information from entity."""
    if "disk_spec" not in entity:
        return "Unknown"

    if entity["disk_spec"]["kind"] == "root_disk":
        return f"{entity['disk_spec']['size']}"

    if entity["disk_spec"]["kind"] == "disks":
        disks = [str(d["size"]) for d in entity["disk_spec"]["disks"]]
        return ",".join(disks)

    return "Unknown"


def extract_image_from_entity(entity: dict) -> str:
    """Extract image information from entity."""
    if "disk_spec" not in entity:
        return "Unknown"

    if entity["disk_spec"]["kind"] == "root_disk":
        return entity["disk_spec"]["image"]

    if entity["disk_spec"]["kind"] == "disks":
        return entity["disk_spec"]["disks"][0]["image"]

    return "Unknown"


def _power_command(
    name: str, action: str, help: str, entity: str, collection: str
) -> click.Command:
    @click.command(name, help=help)
    @click.pass_context
    @click.argument(
        "uuid_or_name",
        type=str,
        required=True,
        help=f"{entity} UUID or name",
    )
    def power_cmd(ctx: click.Context, uuid_or_name: str) -> None:
        client = base_client.get_user_api_client(ctx.obj.auth_data)
        obj = base_client.get_entity(client, collection, uuid_or_name)
        show_data(base_client.action_entity(client, collection, action, obj["uuid"]))

    return power_cmd


def add_power_commands(group: click.Group, entity: str, collection: str) -> None:
    """Add the power management commands to the entity group."""
    for name, (action, help) in POWER_ACTIONS.items():
        group.add_command(
            _power_command(name, action, help.format(entity=entity), entity, collection)
        )
