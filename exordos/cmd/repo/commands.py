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
import pathlib
import typing as tp

import rich.status as rich_status
import rich_click as click

from exordos import constants as c
from exordos.builder import base as base_builder
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.repo import base as base_repo
from exordos.repo import elements_inventory
from exordos.repo import fs as repo_fs
from exordos.repo import utils as repo_utils

if tp.TYPE_CHECKING:
    from exordos.common.cmd_context import ContextObject


@click.group("repo", help="Manage Exordos repository")
def repository_group():
    pass


@repository_group.command("init", help="Initialize the repository")
@click.option(
    "-c",
    "--exordos-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Force init even if the repo already exists",
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_obj
def repo_init_cmd(
    obj: "ContextObject",
    exordos_cfg_file: str,
    target: str | None,
    force: bool,
    project_dir: str,
) -> base_repo.AbstractRepoDriver:

    driver = repo_utils.load_repo_driver(
        exordos_cfg_file, target, project_dir, obj.cfg_path
    )

    try:
        driver.init_repo()
    except base_repo.RepoAlreadyExistsError:
        click.secho(
            "Repository already exists.",
            fg="yellow",
        )
        if force:
            driver.delete_repo()
            driver.init_repo()
    return driver


@repository_group.command("delete", help="Delete the repository")
@click.option(
    "-c",
    "--exordos-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_obj
def repo_delete_cmd(
    obj: "ContextObject",
    exordos_cfg_file: str,
    target: str | None,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(
        exordos_cfg_file, target, project_dir, obj.cfg_path
    )
    driver.delete_repo()


@repository_group.command("list", help="List elements in the repository")
@click.option(
    "-c",
    "--exordos-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.option(
    "-e",
    "--element",
    default=None,
    help="Element to list",
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_obj
def repo_list_cmd(
    obj: "ContextObject",
    exordos_cfg_file: str,
    target: str | None,
    element: str | None,
    project_dir: str,
) -> None:
    table = get_table()
    driver = repo_utils.load_repo_driver(
        exordos_cfg_file, target, project_dir, obj.cfg_path
    )
    try:
        elements = driver.list()
    except base_repo.RepoNotFoundError:
        click.secho("Repositories not found", fg="red")
        return

    click.secho(f"Repository: {driver.name}", fg="green")
    if element is not None:
        if element not in elements:
            raise click.UsageError(f"Element {element} not found")

        table.add_column("version")

        for version in sorted(elements[element]):
            table.add_row(version)

        print_table(table)
        return

    table.add_column("name")
    table.add_column("latest version")
    table.add_column("versions")

    for element in elements:
        table.add_row(
            element, sorted(elements[element])[-1], str(len(elements[element]))
        )

    print_table(table)


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
        'url=http://repo.local.genesis-core.tech:8080/ --driver-params auth=["user","password"]'
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
    project_dir: pathlib.Path,
) -> None:
    repo_driver = repo_utils.load_repo_driver(
        exordos_cfg_file, target, project_dir, obj.cfg_path, driver, driver_params
    )

    # Every build creates a local repo with built elements into it.
    if not os.path.isabs(element_dir):
        element_dir = os.path.join(project_dir, element_dir)
    build_repo = repo_fs.FSRepoDriver(element_dir)
    build_repo_dir = pathlib.Path(build_repo.elements_path)

    with open(build_repo_dir / "inventory.json") as f:
        repo_inventory = json.load(f)
        repo_elements = repo_inventory["elements"]

    for e_name in repo_elements:
        # FIXME(akremenetsky): In the build repo only single version is available
        e_version = tuple(repo_elements[e_name].keys())[0]
        e_dir = build_repo_dir / e_name / e_version
        e_inventory = base_builder.ElementInventory.from_dict(
            repo_elements[e_name][e_version]
        )
        e_inventory = e_inventory.replace_with_abspath(e_dir)

        try:
            with rich_status.Status("Push the element to the repo...", spinner="dots"):
                repo_driver.push(e_inventory, latest=latest)
        except base_repo.ElementAlreadyExistsError:
            if force:
                repo_driver.remove(e_inventory)
                with rich_status.Status(
                    "Push the element to the repo...", spinner="dots"
                ):
                    repo_driver.push(e_inventory, latest=latest)
                    continue

            click.secho(
                f"Element {e_inventory.name} version "
                f"{e_inventory.version} already exists.",
                fg="red",
            )


@repository_group.command("build-inventory", help="Build elements inventory")
@click.option(
    "-e",
    "--elements-dir",
    type=click.Path(),
    default=".",
    help="Directory where elements are stored",
)
@click.argument("project_dir", type=click.Path(), default=".")
def build_elements_inventory_cmd(
    elements_dir: str,
    project_dir: str,
) -> None:
    elements_inventory.build(project_dir, elements_dir)
