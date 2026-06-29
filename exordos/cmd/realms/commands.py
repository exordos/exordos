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

import dataclasses
import ipaddress
import os

import requests
import rich_click as click

from exordos.cmd.aliases import ClickAliasedGroup
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.infra.driver import libvirt as libvirt_infra
from exordos.infra.libvirt import libvirt
from exordos.logger import ClickLogger
from exordos.stand import models as stand_models
from exordos.utils import get_ip_from_url


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
    config = ctx.obj.cfg
    config_realms = config.get("realms", {})

    realms: dict[str, Realm] = {}

    infra = libvirt_infra.LibvirtInfraDriver()

    # Get the list of local realms by libvirt
    for stand in infra.list_stands():
        ip = get_stand_core_ip(stand)
        realms[str(ip)] = Realm(stand.name, str(ip), "local", "Active")

    # Get the list of remote realms by config
    for config_realm_name, config_realm in config_realms.items():
        endpoint = config_realm.get("endpoint", "")
        if not endpoint:
            continue
        try:
            ip = get_ip_from_url(endpoint)
            if realm := realms.get(ip):
                realm.name = config_realm_name
                continue
        except ValueError:
            continue
        if check_api(endpoint):
            status = "Connected"
        else:
            status = "Disconnected"

        realms[ip] = Realm(config_realm_name, ip, "remote", status)

    table = get_table(*["Name", "IP", "Provider", "Status"])
    for realm in realms.values():
        table.add_row(realm.name, realm.ip, realm.provider, realm.status)

    print_table(table)


@click.command("delete", help="Delete local realm")
@click.argument("name", type=str)
@click.pass_context
def delete_cmd(ctx: click.Context, name: str) -> None:
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
        if stand.name == name:
            clear_local_realm()
            click.echo(f"Deleting local realm {stand.name}...")
            infra.delete_stand(stand)
            return None

    config = ctx.obj.cfg
    config_realm = config.get("realms", {}).get(name)
    if config_realm:
        try:
            endpoint = config_realm.get("endpoint", "")
            config_ip = get_ip_from_url(endpoint)
            for stand in local_stands:
                ip = get_stand_core_ip(stand)
                if str(ip) == config_ip:
                    clear_local_realm()
                    click.echo(f"Deleting local realm {stand.name}...")
                    infra.delete_stand(stand)
                    return None
        except ValueError as err:
            click.echo(f"Error while converting IP address: {err}")

    raise click.ClickException(f"Local realm {name} not found")


realms_group.add_command(list_cmd, aliases=["l"])
realms_group.add_command(delete_cmd, aliases=["d"])
