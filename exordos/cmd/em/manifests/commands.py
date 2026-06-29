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
import os

import rich_click as click
import yaml

from exordos.clients import base_client
from exordos.clients import repo as repo_lib
from exordos.cmd.base import create_entity_group
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.common.table import show_data
import exordos.constants as c
from exordos.spec.schema import validate_manifest

ENTITY = "manifest"
ENTITY_COLLECTION = c.MANIFEST_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Version": "version",
    "Status": "status",
}

manifests_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    add_show_command=False,
    add_delete_command=True,
)


@click.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(ctx: click.Context, uuid: str) -> None:
    """Show manifest general information"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)

    if data["resources"]:
        click.echo("Resources json:")
        click.echo(json.dumps(data["resources"], indent=4))
    if data["requirements"]:
        click.echo("Requirements json:")
        click.echo(json.dumps(data["requirements"], indent=4))
    if data["imports"]:
        click.echo("Imports json:")
        click.echo(json.dumps(data["imports"], indent=4))
    if data["exports"]:
        click.echo("Exports json:")
        click.echo(json.dumps(data["exports"], indent=4))

    resources = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/resources/"
    )
    table = get_table(
        "UUID", "Name", "Kind", "Full hash", "Status", "Created at", "Updated at"
    )

    for resource in resources:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            str(resource["full_hash"]),
            resource["status"],
            resource["created_at"],
            resource["updated_at"],
        )

    print_table(table, msg="Resources:")


@manifests_group.command("validate", help=f"Validate {ENTITY}")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.argument("path_or_name")
def validate_cmd(repository: str, path_or_name: str) -> None:
    if os.path.isfile(path_or_name):
        with open(path_or_name, "r", encoding="utf-8") as f:
            manifest_data = yaml.safe_load(f)
    else:
        manifest_data = repo_lib.Repository(repository).get_manifest(path_or_name)
    validate_manifest(manifest_data, repository)
    name = f"{manifest_data['name']} ({manifest_data['version']})"
    click.echo(f"Manifest {click.style(name, fg='green')} validated successfully")


@click.command("uninstall", help=f"Uninstall {ENTITY} by UUID or name")
@click.argument(
    "uuid_or_name",
    type=str,
    required=True,
)
@click.pass_context
def uninstall_cmd(ctx: click.Context, uuid_or_name: str) -> None:
    """Uninstall manifest by UUID or name"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    manifest = base_client.get_entity(client, ENTITY_COLLECTION, uuid_or_name)

    base_client.action_entity(client, ENTITY_COLLECTION, "uninstall", manifest["uuid"])

    name = f"{manifest['name']} ({manifest['version']})"
    click.echo(f"Manifest {click.style(name, fg='green')} was uninstalled successfully")


manifests_group.add_command(show_cmd, aliases=["get", "g"])
manifests_group.add_command(uninstall_cmd)
