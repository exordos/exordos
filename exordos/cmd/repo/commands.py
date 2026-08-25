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

import pathlib
import typing as tp
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.repo.elements import commands as elements_commands
from exordos.cmd.repo.store import commands as store_commands
from exordos.common.table import show_data
from exordos.repo import utils as repo_utils

if tp.TYPE_CHECKING:
    from exordos.common.cmd_context import ContextObject


# Repository management constants and functions
REPOSITORY_ENTITY = "repository"
REPOSITORY_FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Priority": "priority",
    "Refresh Rate": "refresh_rate",
    "Sync mode": "sync_mode",
    "URI": lambda x: x.get("driver_spec", {}).get("url", ""),
    "Status": "status",
}


def _build_driver_spec(
    url: str | None,
    username: str | None,
    password: str | None,
) -> dict[str, str] | None:
    if url is None:
        return None
    spec = {"kind": "nginx", "url": url}
    if username is not None:
        spec["username"] = username
    if password is not None:
        spec["password"] = password
    return spec


@click.group("repo", help="Manage Exordos repository")
def repository_group():
    pass


# Repository list and delete commands (from create_entity_group)
_repository_group = create_entity_group(
    REPOSITORY_ENTITY,
    c.REPOSITORY_COLLECTION,
    REPOSITORY_FIELDS_MAP,
    None,
    add_list_command=True,
    add_show_command=True,
    add_delete_command=True,
)

# Add list and delete commands to main repo group
repository_group.add_command(_repository_group.commands["list"], aliases=["l"])
repository_group.add_command(_repository_group.commands["show"], aliases=["get", "g"])
repository_group.add_command(_repository_group.commands["delete"], aliases=["d"])


@click.command("add", help=f"Add a new {REPOSITORY_ENTITY}")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {REPOSITORY_ENTITY}",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help=f"UUID of the project in which to deploy the {REPOSITORY_ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="",
    help=f"Name of the {REPOSITORY_ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {REPOSITORY_ENTITY}",
)
@click.option(
    "--priority",
    type=int,
    default=2048,
    help=f"Priority of the {REPOSITORY_ENTITY} (0-4096)",
)
@click.option(
    "--refresh-rate",
    type=int,
    default=3600,
    help=f"Refresh rate of the {REPOSITORY_ENTITY} in seconds",
)
@click.option(
    "--sync-mode",
    type=click.Choice(["copy", "lazy"]),
    default="lazy",
    help=f"Sync mode of the {REPOSITORY_ENTITY}",
)
@click.option(
    "--repo-url",
    type=str,
    required=True,
    help="URL of the repository. Example: https://repo.exordos.com/exordos-elements/",
)
@click.option(
    "--repo-user",
    type=str,
    default=None,
    help="Username for the repository",
)
@click.option(
    "--repo-password",
    type=str,
    default=None,
    help="Password for the repository",
)
def repository_add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    priority: int,
    refresh_rate: int,
    sync_mode: str,
    repo_url: str,
    repo_user: str | None,
    repo_password: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "priority": priority,
        "refresh_rate": refresh_rate,
        "sync_mode": sync_mode,
    }
    driver_spec = _build_driver_spec(repo_url, repo_user, repo_password)
    if driver_spec is not None:
        data["driver_spec"] = driver_spec
    entity = base_client.add_entity(client, c.REPOSITORY_COLLECTION, data)
    show_data(entity)


@click.command("update", help=f"Update {REPOSITORY_ENTITY}")
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
    help=f"UUID of the project in which to deploy the {REPOSITORY_ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help=f"Name of the {REPOSITORY_ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help=f"Description of the {REPOSITORY_ENTITY}",
)
@click.option(
    "--status",
    type=click.Choice(["NEW", "ACTIVE", "IN_PROGRESS", "DISABLED", "ERROR"]),
    default=None,
    help=f"Status of the {REPOSITORY_ENTITY}",
)
@click.option(
    "--priority",
    type=int,
    default=None,
    help=f"Priority of the {REPOSITORY_ENTITY} (0-4096)",
)
@click.option(
    "--refresh-rate",
    type=int,
    default=None,
    help=f"Refresh rate of the {REPOSITORY_ENTITY} in seconds",
)
@click.option(
    "--sync-mode",
    type=click.Choice(["copy", "lazy"]),
    default=None,
    help=f"Sync mode of the {REPOSITORY_ENTITY}",
)
@click.option(
    "--repo-url",
    type=str,
    default=None,
    help="URL of the repository. Example: https://repo.exordos.com/exordos-elements/",
)
@click.option(
    "--repo-user",
    type=str,
    default=None,
    help="Username for the repository",
)
@click.option(
    "--repo-password",
    type=str,
    default=None,
    help="Password for the repository",
)
def repository_update_cmd(
    ctx: click.Context,
    uuid: str,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
    status: str | None,
    priority: int | None,
    refresh_rate: int | None,
    sync_mode: str | None,
    repo_url: str | None,
    repo_user: str | None,
    repo_password: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if status is not None:
        data["status"] = status
    if priority is not None:
        data["priority"] = priority
    if refresh_rate is not None:
        data["refresh_rate"] = refresh_rate
    if sync_mode is not None:
        data["sync_mode"] = sync_mode

    driver_spec = _build_driver_spec(repo_url, repo_user, repo_password)
    if driver_spec is not None:
        data["driver_spec"] = driver_spec

    entity = base_client.update_entity(client, c.REPOSITORY_COLLECTION, uuid, data)
    show_data(entity)


repository_group.add_command(repository_add_cmd, aliases=["a"])
repository_group.add_command(repository_update_cmd, aliases=["u"])


@click.command("refresh", help=f"Refresh {REPOSITORY_ENTITY}")
@click.pass_context
@click.argument(
    "name_or_uuid",
    type=str,
    required=True,
)
def repository_refresh_cmd(
    ctx: click.Context,
    name_or_uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entity_uuid = base_client._get_entity_uuid(
        client, c.REPOSITORY_COLLECTION, name_or_uuid
    )
    base_client.action_entity(client, c.REPOSITORY_COLLECTION, "refresh", entity_uuid)
    click.echo(
        f"Repository {click.style(name_or_uuid, fg='green')} was refreshed successfully"
    )


repository_group.add_command(repository_refresh_cmd)


@click.command("upload", help=f"Upload element to {REPOSITORY_ENTITY}")
@click.pass_context
@click.option(
    "-r",
    "--repository",
    type=str,
    required=True,
    help="Repository name or UUID to upload element to",
)
@click.argument(
    "manifest",
    type=pathlib.Path,
    required=True,
)
def repository_upload_cmd(
    ctx: click.Context,
    repository: str,
    manifest: pathlib.Path,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    repo_utils.do_upload(client, repository, manifest)


repository_group.add_command(repository_upload_cmd)

# Add elements subgroup
repository_group.add_command(elements_commands.elements_group, aliases=["e"])
repository_group.add_command(store_commands.store_group, aliases=["s"])


@repository_group.command("push", help="Push the element to the repository")
@click.option(
    "-c",
    "--exordos-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-d",
    "--driver",
    default=None,
    help="Driver to use, nginx for example",
)
@click.option(
    "--driver-params",
    multiple=True,
    help=(
        "Additional params to pass to the driver. "
        "The format is 'key=value'. For example: --driver-params "
        'url=http://repo.local.exordos.com:8080/ --driver-params auth=["user","password"]'
    ),
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.option(
    "-e",
    "--element-dir",
    default=lambda: pathlib.Path(c.DEF_GEN_OUTPUT_DIR_NAME),
    help="Directory where element artifacts are stored",
    type=click.Path(path_type=pathlib.Path),
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Force push even if the element already exists",
)
@click.option(
    "-l",
    "--latest",
    show_default=True,
    is_flag=True,
    help="Push the element too as the latest version (if stable version)",
)
@click.option(
    "-j",
    "--jobs",
    default=1,
    show_default=True,
    type=click.IntRange(min=1),
    help="Number of artifacts to upload in parallel",
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_obj
def push_cmd(
    obj: "ContextObject",
    exordos_cfg_file: str,
    driver: str | None,
    driver_params: tuple[str, ...],
    target: str | None,
    element_dir: pathlib.Path,
    force: bool,
    latest: bool,
    jobs: int,
    project_dir: pathlib.Path,
) -> None:
    repo_driver = repo_utils.load_repo_driver(
        exordos_cfg_file, target, project_dir, obj.cfg_path, driver, driver_params
    )
    repo_utils.do_push(repo_driver, element_dir, force, latest, jobs)
