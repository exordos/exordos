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
import os

import rich_click as click

from exordos.cmd.aliases import ClickAliasedGroup
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.infra.driver import libvirt as libvirt_infra
from exordos.infra.libvirt import libvirt
from exordos.logger import ClickLogger
from exordos.utils import get_ip_from_url


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
        logger.warn("No exordos realms found")
        return

    if len(stands) > 1 and realm is None:
        logger.warn("Multiple exordos realms found, please specify one")
        return

    # If the stand is not specified, use the first one
    for dev_stand in stands:
        if realm is None:
            break

        if dev_stand.name == realm:
            break
    else:
        raise click.UsageError("No exordos realm found")

    if dev_stand.network.dhcp:
        ip_address = libvirt.get_domain_ip(dev_stand.bootstraps[0].name)
    else:
        ip_address = dev_stand.network.cidr[2]

    os.system(f"ssh {username}@{ip_address}")


@dataclasses.dataclass
class Realm:
    name: str
    ip: str
    local: bool


@click.command("list", help="List of realms")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    config = ctx.obj.cfg
    config_realms = config.get("realms", {})

    realms: dict[str, Realm] = {}

    infra = libvirt_infra.LibvirtInfraDriver()

    # Get the list of local realms by libvirt
    for stand in infra.list_stands():
        if stand.network.dhcp:
            ip = libvirt.get_domain_ip(stand.bootstraps[0].name)
        else:
            ip = stand.network.cidr[2]
        realms[str(ip)] = Realm(stand.name, str(ip), True)

    # Get the list of remote realms by config
    for config_realm_name, config_realm in config_realms.items():
        try:
            ip = get_ip_from_url(config_realm.get("endpoint", ""))
            if realm := realms.get(ip):
                realm.name = config_realm_name
                continue
        except ValueError:
            continue
        realms[ip] = Realm(config_realm_name, ip, False)

    table = get_table(*["Name", "IP", "Local/Remote"])
    for realm in realms.values():
        table.add_row(realm.name, realm.ip, "local" if realm.local else "remote")

    print_table(table)


realms_group.add_command(list_cmd, aliases=["l"])


@realms_group.command("delete", help="Delete local realm")
@click.argument("name", type=str)
def delete_cmd(name: str) -> None:
    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name == name:
            break
    else:
        raise click.UsageError(f"Local realm {name} not found")

    infra.delete_stand(stand)
