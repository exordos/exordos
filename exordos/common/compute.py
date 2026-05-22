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

import rich_click as click

from exordos.clients import base_client
import exordos.constants as c


def get_compute_targets_from_element(client, element_data: dict) -> list:
    nodes_resources = base_client.list_entities(
        client,
        f"{c.ELEMENT_COLLECTION}{element_data['uuid']}/resources/",
        kind="em_core_compute_nodes",
    )
    sets_resources = base_client.list_entities(
        client,
        f"{c.ELEMENT_COLLECTION}{element_data['uuid']}/resources/",
        kind="em_core_compute_sets",
    )
    if len(nodes_resources) == 0 and len(sets_resources) == 0:
        raise click.ClickException(
            f"No nodes and sets found for element {element_data['name']}"
        )

    targets = []
    for resource in nodes_resources:
        compute_node = base_client.get_entity(
            client, c.NODE_COLLECTION, resource["uuid"]
        )
        targets.append(
            {
                "target": {
                    "kind": "node",
                    "node": resource["uuid"],
                },
                "ips": [compute_node["default_network"].get("ipv4", None)],
                "project_id": compute_node["project_id"],
                "name": compute_node["name"],
                "uuid": compute_node["uuid"],
            }
        )
    for resource in sets_resources:
        compute_set = base_client.get_entity(client, c.SET_COLLECTION, resource["uuid"])
        targets.append(
            {
                "target": {
                    "kind": "node_set",
                    "node_set": resource["uuid"],
                },
                "ips": [
                    node.get("ipv4", None) for node in compute_set["nodes"].values()
                ],
                "project_id": compute_set["project_id"],
                "name": compute_set["name"],
                "uuid": compute_set["uuid"],
            }
        )
    return targets


def get_compute_targets_from_service(client, service_data: dict) -> list:
    kind = service_data["target"]["kind"]
    targets = []
    if kind == "node":
        compute_node = base_client.get_entity(
            client, c.NODE_COLLECTION, service_data["target"][kind]
        )
        targets.append(
            {
                "target": {
                    "kind": kind,
                    kind: compute_node["uuid"],
                },
                "ips": [compute_node["default_network"].get("ipv4", None)],
                "project_id": compute_node["project_id"],
                "name": compute_node["name"],
            }
        )
    elif kind == "node_set":
        compute_set = base_client.get_entity(
            client, c.SET_COLLECTION, service_data["target"][kind]
        )
        targets.append(
            {
                "target": {
                    "kind": kind,
                    kind: compute_set["uuid"],
                },
                "ips": [
                    node.get("ipv4", None) for node in compute_set["nodes"].values()
                ],
                "project_id": compute_set["project_id"],
                "name": compute_set["name"],
            }
        )
    return targets
