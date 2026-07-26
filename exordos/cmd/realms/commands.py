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

from concurrent.futures import ThreadPoolExecutor
import dataclasses
import ipaddress
import os
from urllib.parse import urljoin
import uuid as sys_uuid

import questionary
import requests
import rich_click as click

from exordos import utils as exordos_utils
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.common.table import show_data
from exordos.infra.driver import libvirt as libvirt_infra
from exordos.infra.libvirt import libvirt
from exordos.logger import ClickLogger
from exordos.stand import models as stand_models

ENTITY_COLLECTION = "/v1/realms/"
ENTITY = "realm"
REALM_SCOPE = "openid email profile project:default"
ECOSYSTEM_URL_PART = "/api/ecosystem/"


def get_ecosystem_client(ctx: click.Context):
    auth_data = ctx.obj.auth_data.copy()
    if not auth_data.get("scope"):
        auth_data["scope"] = REALM_SCOPE
    auth_data["login"] = auth_data["username"]

    client = base_client.get_user_api_client(
        auth_data,
    )
    client._auth.authenticate()

    ecosystem_endpoint = auth_data.get("ecosystem_endpoint")
    if not ecosystem_endpoint:
        base_url = exordos_utils.get_base_url(auth_data.get("endpoint", ""))
        ecosystem_endpoint = urljoin(base_url, ECOSYSTEM_URL_PART)
    client._base_url = ecosystem_endpoint

    return client


def get_stand_core_ip(
    stand: "stand_models.Stand",
) -> str | ipaddress.IPv4Address | None:
    """Return the core VM's IP address for a local libvirt stand.

    Shared by the realm listing/deletion commands here and by
    `exordos deploy`'s bind-address auto-detection.
    """
    if stand.network.dhcp:
        return libvirt.get_domain_ip(stand.bootstraps[0].name)
    return stand.network.cidr[2]


@click.group("realms", cls=ClickAliasedGroup, help="Manage realms")
def realms_group():
    pass


@realms_group.command("ssh", help="Connect to local realm")
@click.option(
    "-r",
    "--realm",
    default=None,
    help="Realm to connect to",
)
@click.option(
    "-u",
    "--username",
    default="ubuntu",
    help="Default username",
)
def ssh_cmd(realm: str | None, username: str) -> None:
    logger = ClickLogger()
    infra = libvirt_infra.LibvirtInfraDriver()
    stands = infra.list_stands()

    if len(stands) == 0:
        logger.warning("No exordos realms found")
        return

    if len(stands) > 1 and realm is None:
        logger.warning("Multiple exordos realms found, please specify one")
        return

    # If the stand is not specified, use the first one
    for dev_stand in stands:
        if realm is None:
            break

        if dev_stand.name == realm:
            break
    else:
        raise click.UsageError("No exordos realm found")

    ip_address = get_stand_core_ip(dev_stand)

    os.system(f"ssh {username}@{ip_address}")


@dataclasses.dataclass
class Realm:
    name: str
    ip: str
    provider: str
    status: str


def check_api(url: str) -> bool:
    try:
        requests.get(url, timeout=1)
        return True
    except requests.exceptions.RequestException:
        return False


@click.command("list", help="List of realms")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    def get_ecosystem_realms() -> dict[str, Realm]:
        # Get the list of realms from the ecosystem
        from yretry import defaults

        defaults.HTTP_RETRY_ATTEMPTS = 1
        ecosystem_client = get_ecosystem_client(ctx)
        try:
            ecosystem_realms = base_client.list_entities(
                ecosystem_client,
                ENTITY_COLLECTION,
            )
        except Exception:
            # TODO(slashburygin): raise Error after telemetry on all stands will send info about themselves
            ecosystem_realms = []
        return {
            realm["name"]: Realm(
                realm["name"], realm["domain"], "ecosystem", realm["status"]
            )
            for realm in ecosystem_realms
        }

    def get_local_realms() -> dict[str, Realm]:
        # Get the list of local realms by libvirt
        infra = libvirt_infra.LibvirtInfraDriver()
        return {
            str(ip): Realm(stand.name, str(ip), "local", "ACTIVE")
            for stand in infra.list_stands()
            if (ip := get_stand_core_ip(stand))
        }

    def get_config_realms() -> dict[str, Realm]:
        # Get the list of remote realms by config
        realms = {}
        for config_realm_name, config_realm in ctx.obj.cfg.get("realms", {}).items():
            endpoint = config_realm.get("endpoint", "")
            if not endpoint:
                continue
            try:
                ip = exordos_utils.get_ip_from_url(endpoint)
            except ValueError:
                continue
            status = "CONNECTED" if check_api(endpoint) else "DISCONNECTED"
            realms[ip] = Realm(config_realm_name, ip, "remote", status)
        return realms

    with ThreadPoolExecutor(max_workers=3) as executor:
        ecosystem_future = executor.submit(get_ecosystem_realms)
        local_future = executor.submit(get_local_realms)
        config_future = executor.submit(get_config_realms)
        realms = ecosystem_future.result()
        realms.update(local_future.result())
        config_realms = config_future.result()

    for ip, config_realm in config_realms.items():
        if realm := realms.get(ip):
            realm.name = config_realm.name
        else:
            realms[ip] = config_realm

    table = get_table(*["Name", "Address", "Provider", "Status"])
    for realm in realms.values():
        table.add_row(realm.name, realm.ip, realm.provider, realm.status)

    print_table(table)


@click.command("add", help=f"Add a new ecosystem {ENTITY}")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=f"example_{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "--admin-password",
    type=str,
    required=False,
    help=f"Password of the {ENTITY}. If not provided, will be asked interactively",
    hide_input=True,
)
@click.option(
    "--node-cores",
    type=int,
    required=False,
)
@click.option(
    "--node-ram",
    type=int,
    required=False,
)
@click.option(
    "--node-root-disk-size",
    type=int,
    required=False,
)
@click.option(
    "--node-image",
    type=str,
    required=False,
    help=f"Url of the {ENTITY} image",
)
@click.option(
    "--core-version",
    type=str,
    required=False,
)
@click.option(
    "--ssh-public-key",
    envvar="SSH_PUBLIC_KEY",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=False,
    help="Path to the ssh public key",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    admin_password: str | None,
    node_cores: int | None,
    node_ram: int | None,
    node_root_disk_size: int | None,
    node_image: str | None,
    core_version: str | None,
    ssh_public_key: str | None,
) -> None:
    ecosystem_client = get_ecosystem_client(ctx)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "name": name,
        "kind": "MANAGED",
        "admin_password": admin_password
        or questionary.password(f"Enter admin password for {ENTITY} {name}:").ask(),
    }
    if node_cores is not None:
        data["node_cores"] = node_cores
    if node_ram is not None:
        data["node_ram"] = node_ram
    if node_root_disk_size is not None:
        data["node_root_disk_size"] = node_root_disk_size
    if node_image is not None:
        data["node_image"] = node_image
    if core_version is not None:
        data["core_version"] = core_version
    if ssh_public_key is not None:
        with open(ssh_public_key, "r") as f:
            ssh_public_key = f.read()
        data["ssh_public_key"] = ssh_public_key
    data = base_client.add_entity(ecosystem_client, ENTITY_COLLECTION, data)
    show_data(data)


@click.command("delete", help="Delete realm")
@click.argument("name_uuid", type=str)
@click.pass_context
def delete_cmd(ctx: click.Context, name_uuid: str) -> None:
    # Get the list of realms from the ecosystem
    from yretry import defaults

    defaults.HTTP_RETRY_ATTEMPTS = 1
    ecosystem_client = get_ecosystem_client(ctx)
    try:
        ecosystem_realms = base_client.list_entities(
            ecosystem_client,
            ENTITY_COLLECTION,
        )
    except Exception:
        ecosystem_realms = []

    for realm in ecosystem_realms:
        if realm["name"] == name_uuid:
            base_client.delete_entity(
                ecosystem_client, ENTITY_COLLECTION, realm["uuid"]
            )
            click.echo(f"{ENTITY} {name_uuid} deleted")
            return None
        elif realm["uuid"] == name_uuid:
            base_client.delete_entity(ecosystem_client, ENTITY_COLLECTION, name_uuid)
            click.echo(f"{ENTITY} {name_uuid} deleted")
            return None

    infra = libvirt_infra.LibvirtInfraDriver()
    local_stands = infra.list_stands()

    def clear_local_realm() -> None:
        try:
            import time

            from rich.progress import track

            from exordos.cmd.em.elements.commands import clear

            click.echo(f"Clearing local realm {stand.name}...")
            was_cleared = ctx.invoke(
                clear,
                y=True,
            )

            if was_cleared:
                for _ in track(range(5), description="Waiting clearing resources..."):
                    time.sleep(1)
        except Exception:
            pass

    for stand in local_stands:
        if stand.name == name_uuid:
            clear_local_realm()
            click.echo(f"Deleting local realm {stand.name}...")
            infra.delete_stand(stand)
            return None

    config = ctx.obj.cfg
    config_realm = config.get("realms", {}).get(name_uuid)
    if config_realm:
        try:
            endpoint = config_realm.get("endpoint", "")
            config_ip = exordos_utils.get_ip_from_url(endpoint)
            for stand in local_stands:
                ip = get_stand_core_ip(stand)
                if str(ip) == config_ip:
                    clear_local_realm()
                    click.echo(f"Deleting local realm {stand.name}...")
                    infra.delete_stand(stand)
                    return None
        except ValueError as err:
            click.echo(f"Error while converting IP address: {err}")

    raise click.ClickException(f"Local realm {name_uuid} not found")


realms_group.add_command(list_cmd, aliases=["l"])
realms_group.add_command(delete_cmd, aliases=["d"])
realms_group.add_command(add_cmd, aliases=["a"])
