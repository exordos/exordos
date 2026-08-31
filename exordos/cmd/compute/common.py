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


def extract_disk_type_from_entity(entity: dict) -> str:
    """Extract the root disk's backend type from entity."""
    if "disk_spec" not in entity:
        return "Unknown"

    if entity["disk_spec"]["kind"] == "root_disk":
        return entity["disk_spec"].get("disk_kind", {}).get("kind", "qcow2")

    if entity["disk_spec"]["kind"] == "disks":
        disks = entity["disk_spec"]["disks"]
        if not disks:
            return "Unknown"
        return disks[0].get("disk_kind", {}).get("kind", "qcow2")

    return "Unknown"
