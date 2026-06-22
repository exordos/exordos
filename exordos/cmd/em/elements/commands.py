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

import os
import subprocess
import tempfile
import time
import typing as tp
import uuid as sys_uuid

from bazooka import exceptions as bazooka_exc
import questionary
from rich.prompt import Confirm
from rich.text import Text
import rich_click as click

from exordos import utils
from exordos.clients import base_client
from exordos.clients import repo as repo_lib
from exordos.cmd.base import create_entity_group
from exordos.common import compute
from exordos.common import ssh
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.common.table import show_data
import exordos.constants as c
from exordos.logger import ClickLogger

if tp.TYPE_CHECKING:
    from exordos.clients.base import CollectionBaseClient


ENTITY = "element"
ENTITY_COLLECTION = c.ELEMENT_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Version": "version",
    "Manifest": lambda x: x.get("manifest").split("/")[-1],
    "Status": "status",
}


ee_group = create_entity_group(
    ENTITY,
    ENTITY_COLLECTION,
    FIELDS_MAP,
    "ee",
    add_show_command=False,
    add_delete_command=False,
)


@click.command("show", help="Show element general information")
@click.argument("name")
@click.pass_context
def show_cmd(ctx: click.Context, name: str) -> None:
    """Show element general information"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, name)
    show_data(data)

    resources = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/resources/"
    )
    table = get_table("UUID", "Name", "Kind", "Full hash", "Status")
    for resource in resources:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            resource["full_hash"],
            resource["status"],
        )
    print_table(table, msg="Resources:")

    imports = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/imports/"
    )
    table = get_table("UUID", "Name", "Kind", "Link")
    for resource in imports:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            resource["link"],
        )
    print_table(table, msg="Imports:")

    exports = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/exports/"
    )
    table = get_table("UUID", "Name", "Kind", "Link")
    for resource in exports:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            resource["link"],
        )
    print_table(table, msg="Exports:")


@ee_group.command("ips", help="Show element ips")
@click.argument("name")
@click.pass_context
def show_element_ips(ctx: click.Context, name: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    data = base_client.get_entity(client, ENTITY_COLLECTION, name)

    resources = base_client.list_entities(
        client,
        f"{c.ELEMENT_COLLECTION}{data['uuid']}/resources/",
        kind="em_core_compute_nodes",
    )
    if len(resources) == 0:
        raise click.ClickException(f"No nodes found for element {name}")
    elif len(resources) > 1:
        for resource in resources:
            node = client.get(c.NODE_COLLECTION, uuid=resource["uuid"])
            click.echo(
                f"Name: {node['name']}, IP: {node['default_network'].get('ipv4', None)}"
            )
    else:
        node = client.get(c.NODE_COLLECTION, uuid=resources[0]["uuid"])
        click.echo(node["default_network"].get("ipv4", None))


def _apply_with_cleanup(
    client: "CollectionBaseClient",
    manifest_data: dict[str, tp.Any],
    install_only: bool = False,
    update_manifest: bool = False,
    **kwargs: tp.Any,
) -> dict[str, tp.Any]:
    """Apply a manifest and clean up old versions on success."""

    found_manifest_uuids = [
        item["uuid"]
        for item in base_client.list_entities(
            client, c.MANIFEST_COLLECTION, name=manifest_data["name"]
        )
    ]
    if update_manifest:
        manifest_uuid = kwargs["manifest_uuid"]
        manifest_data.pop("created_at", None)
        manifest_data.pop("updated_at", None)
        manifest_data.pop("status", None)
        manifest_data.pop("uuid", None)
        try:
            manifest_data = base_client.update_entity(
                client, c.MANIFEST_COLLECTION, manifest_uuid, manifest_data
            )
        except bazooka_exc.NotFoundError:
            manifest_data = base_client.add_entity(
                client, c.MANIFEST_COLLECTION, manifest_data
            )
        manifest_data["uuid"] = manifest_uuid
    else:
        manifest_data = base_client.add_entity(
            client, c.MANIFEST_COLLECTION, manifest_data
        )
    manifest_uuid = manifest_data["uuid"]

    try:
        if install_only:
            base_client.action_entity(
                client, c.MANIFEST_COLLECTION, "install", manifest_uuid
            )
        else:
            base_client.action_entity(
                client, c.MANIFEST_COLLECTION, "upgrade", manifest_uuid
            )
    except Exception:
        base_client.delete_entity(client, c.MANIFEST_COLLECTION, manifest_uuid)
        raise

    for found_manifest_uuid in found_manifest_uuids:
        if found_manifest_uuid != manifest_uuid:
            base_client.delete_entity(
                client, c.MANIFEST_COLLECTION, found_manifest_uuid
            )

    return manifest_data


def upgrade_manifest(
    client: "CollectionBaseClient",
    repository: str,
    path_or_name: str,
    install_only: bool = False,
    version: str | None = None,
    update_manifest: bool = False,
    **kwargs: tp.Any,
) -> dict[str, tp.Any]:
    """Install or update element from a YAML file or repository.

    The command will install the element if it's not installed or update it
    if it's installed.
    """

    if os.path.exists(path_or_name):
        if not os.path.isfile(path_or_name):
            raise click.ClickException(f"{path_or_name} is not a file")
        manifest = utils.load_yaml(path_or_name)
    else:
        manifest = repo_lib.download_manifest(repository, path_or_name, version)

    requirements: dict = manifest.get("requirements", {})

    installed = bool(
        base_client.list_entities(client, ENTITY_COLLECTION, name=manifest["name"])
    )

    if installed and install_only:
        raise click.ClickException(f"Element {manifest['name']} is already installed")

    # Install element if no requirements
    if not requirements:
        new_manifest = _apply_with_cleanup(
            client, manifest, install_only, update_manifest, **kwargs
        )
        return new_manifest

    # Resolve dependencies
    installed_elements = {
        e["name"] for e in base_client.list_entities(client, ENTITY_COLLECTION)
    }
    required_elements = [
        item for item in requirements.keys() if item not in installed_elements
    ]
    all_installed_elements = required_elements.copy()
    all_installed_elements.append(manifest["name"])
    click.echo(
        f"The following elements will be {'installed' if install_only else 'upgraded'} first: "
        f"{click.style(', '.join(all_installed_elements), fg='green')}"
    )

    while required_elements:
        requirement = required_elements.pop()
        if requirement not in installed_elements:
            click.echo(
                f"The following dependency element will be installed: {requirement}"
            )
        req_manifest = repo_lib.download_manifest(repository, requirement)

        # Determine requirements for the element
        req_requirements = req_manifest.get("requirements", {})
        req_required_elements = [
            item for item in req_requirements.keys() if item not in installed_elements
        ]
        required_elements.extend(req_required_elements)
        required_elements = list(set(required_elements))

        # NOTE(akremenetsky): We should install the element since there are
        # unresolved dependencies but for the simplicity we will install it here
        req_manifest = base_client.add_entity(
            client, c.MANIFEST_COLLECTION, req_manifest
        )
        try:
            base_client.action_entity(
                client, c.MANIFEST_COLLECTION, "install", req_manifest["uuid"]
            )
        except bazooka_exc.BaseHTTPException as e:
            if e.code == 400 and e.cause.response.json().get("code") == 1000:
                required_elements.insert(0, req_manifest["name"])
                continue
            else:
                raise
        installed_name = f"{req_manifest['name']} ({req_manifest['version']})"
        click.echo(
            f"Element {click.style(installed_name, fg='green')} was installed successfully"
        )

        installed_elements.add(req_manifest["name"])

        # TODO(akremenetsky): The installation is stuck for some reason
        # so we need to wait a bit. Solve the issue in GC and remove this
        # sleep.
        time.sleep(3)

    new_manifest = _apply_with_cleanup(
        client, manifest, install_only, update_manifest, **kwargs
    )
    return new_manifest


@click.command("install", help="Install element")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=False,
    help="version of the element",
)
@click.argument("path_or_name", required=False)
@click.pass_context
def install_cmd(
    ctx: click.Context, repository: str, version: str | None, path_or_name: str | None
) -> None:
    """Install manifest from a YAML file"""
    if not path_or_name:
        all_elements = repo_lib.get_all_elements(repository)
        path_or_name = questionary.select(
            "Select manifest to install",
            choices=all_elements,
        ).ask()
        if not path_or_name:
            click.echo("No manifest selected, aborting")
            return
    manifest = upgrade_manifest(
        base_client.get_user_api_client(ctx.obj.auth_data),
        repository,
        path_or_name,
        install_only=True,
        version=version,
    )
    installed_name = f"{manifest['name']} ({manifest['version']})"
    click.echo(
        f"Element {click.style(installed_name, fg='green')} was installed successfully"
    )


@click.command("update", help="Update element")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=False,
    help="version of the element",
)
@click.argument("path_or_name")
@click.pass_context
def update_cmd(
    ctx: click.Context, repository: str, version: str | None, path_or_name: str
) -> None:
    """Update manifest from a YAML file"""
    manifest = upgrade_manifest(
        base_client.get_user_api_client(ctx.obj.auth_data),
        repository,
        path_or_name,
        version=version,
    )
    click.echo(
        f"Element {click.style(manifest['name'], fg='green')} was successfully updated to version {click.style(manifest['version'], fg='green')}"
    )


@click.command("uninstall", help="Uninstall manifest by UUID, path or name")
@click.argument("path_uuid_name", type=str)
@click.pass_context
def uninstall_cmd(ctx: click.Context, path_uuid_name: str) -> None:
    """Uninstall manifest by UUID, path or name"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    log = ClickLogger()

    def _uninstall(element_uuid: str, element_name: str = None) -> None:
        base_client.action_entity(
            client, c.MANIFEST_COLLECTION, "uninstall", element_uuid
        )
        base_client.delete_entity(client, c.MANIFEST_COLLECTION, element_uuid)
        log.important(
            f"Element {element_name or element_uuid} uninstalled successfully"
        )

    # UUID
    if utils.is_valid_uuid(path_uuid_name):
        _uninstall(path_uuid_name)
        return

    # Name
    name = path_uuid_name

    manifests = base_client.list_entities(client, c.MANIFEST_COLLECTION, name=name)
    if len(manifests) == 1:
        uuid = manifests[0]["uuid"]
        _uninstall(uuid, name)
        return
    elif len(manifests) > 1:
        raise click.ClickException(f"Multiple elements found with name {name}")

    # Path
    if os.path.exists(path_uuid_name):
        manifest = utils.load_yaml(path_uuid_name)
        if "uuid" in manifest:
            filters = {"uuid": manifest["uuid"]}
        elif "name" in manifest:
            filters = {"name": manifest["name"]}
        else:
            raise click.ClickException("Manifest must have uuid or name")

        manifests = base_client.list_entities(client, c.MANIFEST_COLLECTION, **filters)
        if len(manifests) == 1:
            uuid = manifests[0]["uuid"]
            _uninstall(uuid, manifests[0]["name"])
            return
        if len(manifests) > 1:
            raise click.ClickException(f"Multiple elements found with name {name}")
        log.warning(f"manifest {list(filters.values())[0]} not found")
        return

    log.warning(f"Element {path_uuid_name} not found")


@ee_group.command("available", help="Print available elements in repository")
def available_elements() -> None:
    """Update manifest from a YAML file"""
    elements = repo_lib.get_all_elements(c.ELEMENT_REPO_URL)
    for e in elements:
        click.echo(e)


@ee_group.command("versions", help="Print available elements in repository")
@click.argument("name")
def versions(name) -> None:
    """Update manifest from a YAML file"""
    element_versions = repo_lib.get_element_versions_by_inventory(
        c.ELEMENT_REPO_URL, name
    )
    for version in element_versions:
        click.echo(version)


def edit_data(data: str, editor: str = "nano") -> tp.Tuple[str, dict]:
    tf_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="a+", delete=False) as tf:
            tf.write(data)
            tf.flush()
            tf_path = tf.name
            subprocess.call([editor, tf_path])
            tf.seek(0)
            new_data = tf.read()
    finally:
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)
    json_data = utils.load_yaml(new_data)
    return new_data, json_data


@ee_group.command(help="Edit manifest", context_settings={"show_default": True})
@click.argument("uuid_name")
@click.option(
    "-e",
    "--editor",
    default="nano",
    type=click.Choice(["nano", "vim"], case_sensitive=False),
    help="Editor (nano or vim)",
)
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.pass_context
def edit(ctx: click.Context, uuid_name: str, editor: str, repository: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, c.MANIFEST_COLLECTION, uuid_name)
    tf_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="a+", delete=False) as tf:
            utils.dump_yaml(data, tf)
            tf.flush()
            tf_path = tf.name
            subprocess.call([editor, tf_path])
            tf.seek(0)
            manifest = upgrade_manifest(
                client,
                repository,
                tf_path,
                update_manifest=True,
                manifest_uuid=data["uuid"],
            )
    finally:
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)
    click.echo(
        f"Element {click.style(manifest['name'], fg='green')} was successfully edited"
    )


@ee_group.command(
    "define", help="Add resource to manifest", context_settings={"show_default": True}
)
@click.argument("uuid_name")
@click.option(
    "-e",
    "--editor",
    default="nano",
    type=click.Choice(["nano", "vim"], case_sensitive=False),
    help="Editor (nano or vim)",
)
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "--resource-type",
    type=str,
    required=False,
    help="Type of resource to define",
)
@click.option(
    "--resource-name",
    type=str,
    required=False,
    help="Name of resource to define",
)
@click.pass_context
def define(
    ctx: click.Context,
    uuid_name: str,
    editor: str,
    repository: str,
    resource_type: str,
    resource_name: str,
) -> None:
    # Get Openapi schema
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    schema = client.filter(f"{c.MANIFEST_COLLECTION}schema/")

    # Get resource schema
    resources = schema["properties"]["resources"]["properties"]
    if not resource_type:
        resource_type = questionary.select(
            "Select resource to define",
            choices=resources.keys(),
        ).ask()
    if not resource_type:
        click.echo("No resource type selected, aborting")
        return
    if resource_type not in resources:
        click.echo(f"Resource type {resource_type} not found")
        return
    resource_ref = resources[resource_type]["additionalProperties"]["$ref"].split("/")[
        -1
    ]
    resource = schema["components"]["schemas"][resource_ref]
    resource_def = resource["properties"]
    resource_json = {k: v.get("example", "") for k, v in resource_def.items()}
    manifest = base_client.get_entity(client, c.MANIFEST_COLLECTION, uuid_name)
    if resource_type not in manifest["resources"]:
        manifest["resources"][resource_type] = {}
    if not resource_name:
        default_resource_name = (
            f"{manifest['name']}_{resource_ref.split('_')[0].lower()}"
        )
        resource_name = questionary.text(
            "Enter resource name", default=default_resource_name
        ).ask()
    if not resource_name:
        click.echo("No resource name selected, aborting")
        return
    if resource_name in manifest["resources"][resource_type]:
        click.echo(f"Resource {resource_name} with type {resource_type} already exists")
        return
    if "name" in resource_json.keys():
        resource_json["name"] = resource_name
    if "description" in resource_json.keys():
        resource_json["description"] = ""
    manifest["resources"][resource_type][resource_name] = resource_json

    # Edit manifest
    tf_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="a+", delete=False) as tf:
            utils.dump_yaml(manifest, tf)
            tf.flush()
            tf.seek(0)

            line_num = 0
            for line_num, line in enumerate(tf, 1):
                if resource_name in line:
                    break

            tf_path = tf.name
            subprocess.call([editor, f"+{line_num}", tf_path])
            manifest = upgrade_manifest(
                client,
                repository,
                tf_path,
                update_manifest=True,
                manifest_uuid=manifest["uuid"],
            )
    finally:
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)

    click.echo(
        f"Element {click.style(manifest['name'], fg='green')} was successfully edited"
    )


@ee_group.command("clear", help="Uninstall all elements, except base")
@click.option(
    "--y", "-y", help="Automatically answer yes for all questions", is_flag=True
)
@click.pass_context
def clear(ctx: click.Context, y: bool) -> bool:  # pragma: no cover
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entities = base_client.list_entities(client, ENTITY_COLLECTION)
    for entity in entities:
        if entity["name"] in c.BASE_ELEMENTS:
            click.echo(f"Skipping base element {entity['name']}")
            continue
        if y or Confirm.ask(f"Do you want to uninstall {entity['name']}?"):
            uninstalled_name = f"{entity['name']} ({entity['version']})"
            click.echo(
                f"Uninstalling element {click.style(uninstalled_name, fg='green')}"
            )
            base_client.delete_entity(client, ENTITY_COLLECTION, entity["uuid"])
        return True
    return False


@ee_group.command(
    name="ssh",
    help="copy exordos element from local git repo to element nodes, "
    "example cmd: exordos e e ssh empty",
)
@click.option(
    "--user",
    type=str,
    required=False,
    help="ssh user name",
)
@click.option(
    "-i",
    "--public-key",
    type=click.Path(exists=True),
    required=False,
    help="key or path to it, for example: /home/user/.ssh/id_rsa.pub",
)
@click.option(
    "-p",
    "--private-key",
    type=click.Path(exists=True),
    required=False,
    help="key or path to it, for example: /home/user/.ssh/id_rsa.pub",
)
@click.option(
    "--y", "-y", help="Automatically answer yes for all questions", is_flag=True
)
@click.argument("name")
@click.pass_context
def ssh_cmd(
    ctx: click.Context,
    user: str | None,
    public_key: str | None,
    private_key: str | None,
    y: bool,
    name: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    element_data = base_client.get_entity(client, c.ELEMENT_COLLECTION, name)
    targets = compute.get_compute_targets_from_element(client, element_data)
    if len(targets) == 1:
        target = targets[0]
    else:
        target = {}
        target_uuid = questionary.select(
            "Select target uuid for ssh",
            choices=[t["uuid"] for t in targets],
        ).ask()
        if not target_uuid:
            return None
        for target in targets:
            if target["uuid"] == target_uuid:
                break

    if public_key:
        with open(public_key, "r") as f:
            target_public_key = f.read()
        key_pair_name = public_key.split("/")[-1].split(".")[0]
        if not private_key:
            private_key_path = public_key.replace(".pub", "")
            if os.path.exists(private_key_path):
                private_key = private_key_path
    else:
        key_pair_name = ssh.generate_random_ssh_key_name()
        with ssh.generate_keys(key_pair_name, permanent=True) as (priv_path, pub_path):
            private_key = priv_path
            public_key = pub_path
            with open(pub_path, "r") as f:
                target_public_key = f.read()

    ssh_keys = []
    ssh_key_base_data = {
        "user": str(user or c.BOOTSTRAP_USER),
        "target_public_key": target_public_key,
    }
    target_data = ssh_key_base_data.copy()
    target_data["name"] = f"{key_pair_name}_for_{target['name']}"
    target_data["uuid"] = str(sys_uuid.uuid4())
    target_data["target"] = target["target"]
    target_data["project_id"] = target["project_id"]
    ssh_key = base_client.add_entity(client, c.SSH_KEY_COLLECTION, target_data)
    ssh_keys.append(ssh_key)

    ssh.wait_for_ssh_keys(client, ssh_keys)

    for ip in target["ips"]:
        if y or Confirm.ask(Text(f"Do you want ssh to {ip}?")):
            if private_key:
                click.secho(
                    f"Your private key is {click.style(private_key, fg='green')}"
                )
                click.secho(f"Your public key is {click.style(public_key, fg='green')}")
            cmd = [
                "ssh",
                "-t",
                f"{user or c.BOOTSTRAP_USER}@{ip}",
                "-o StrictHostKeyChecking=no",
                "-o UserKnownHostsFile=/dev/null",
            ]
            if private_key:
                cmd.append("-i")
                cmd.append(private_key)
            try:
                subprocess.Popen(cmd)
            except subprocess.CalledProcessError as e:
                raise click.ClickException(e.stderr)
    return None


ee_group.add_command(show_cmd, aliases=["get", "g"])
ee_group.add_command(uninstall_cmd, aliases=["d", "delete"])
ee_group.add_command(install_cmd, aliases=["i", "add"])
ee_group.add_command(update_cmd, aliases=["u"])
