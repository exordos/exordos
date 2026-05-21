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

import subprocess
import uuid as sys_uuid

from rich.prompt import Confirm
import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common import compute
from exordos.common import ssh
from exordos.common.table import show_data

ENTITY = "service"
ENTITY_COLLECTION = c.SERVICE_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Status": "status",
}

services_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("add", help="Add a new service to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the service",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the service",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_service",
    help="Name of the service",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the service",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
    }
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@click.command("update", help="Update service")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="Name of the project in which to deploy the service",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the service",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the service",
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


services_group.add_command(add_cmd, aliases=["a"])
services_group.add_command(update_cmd, aliases=["u"])


@services_group.command(
    hidden=True,
    help="copy exordos element from local git repo to element nodes, "
    "example cmd: exordos e s restart example-service",
)
@click.option(
    "--user",
    type=str,
    required=False,
    help="ssh user name",
)
@click.argument("name")
@click.option(
    "--y", "-y", help="Automatically answer yes for all questions", is_flag=True
)
@click.pass_context
def restart(ctx: click.Context, user: str, name: str, y: bool) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    service_data = base_client.get_entity(client, c.SERVICE_COLLECTION, name)
    service_name = service_data["name"]
    targets = compute.get_compute_targets_from_service(client, service_data)

    key_pair_name = ssh.generate_random_ssh_key_name()
    with ssh.generate_keys(key_pair_name) as (priv_path, pub_path):
        with open(pub_path, "r") as f:
            target_public_key = f.read()
        ssh_keys = []
        try:
            ssh_key_base_data = {
                "user": str(user or c.BOOTSTRAP_USER),
                "target_public_key": target_public_key,
            }
            for target in targets:
                target_data = ssh_key_base_data.copy()
                target_data["name"] = f"{key_pair_name}_for_{target['name']}"
                target_data["uuid"] = str(sys_uuid.uuid4())
                target_data["target"] = target["target"]
                target_data["project_id"] = target["project_id"]
                ssh_key = base_client.add_entity(
                    client, c.SSH_KEY_COLLECTION, target_data
                )
                ssh_keys.append(ssh_key)

            ssh.wait_for_ssh_keys(client, ssh_keys)

            for target in targets:
                for ip in target["ips"]:
                    click.echo(f"Restarting service on {ip}")

                    if y or Confirm.ask(f"Do you want to deploy code to {ip}?"):
                        cmd = [
                            "ssh",
                            f"{user or c.BOOTSTRAP_USER}@{ip}",
                            "-i",
                            priv_path,
                            "echo",
                            f"restarting service {service_name}",
                        ]
                        try:
                            pr = subprocess.run(
                                cmd, check=True, capture_output=True, text=True
                            )
                            click.echo(
                                f"Service {service_name} restarted on {ip}: {pr.stdout}"
                            )
                        except subprocess.CalledProcessError as e:
                            raise click.ClickException(e.stderr)
        finally:
            for ssh_key in ssh_keys:
                base_client.delete_entity(client, c.SSH_KEY_COLLECTION, ssh_key["uuid"])
    return None
