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
import datetime
import ipaddress
import os
import subprocess
from urllib.parse import urljoin
import uuid as sys_uuid

from bazooka import exceptions as bazooka_exc
import requests
import rich_click as click

from exordos import constants as c
from exordos import utils as exordos_utils
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.cmd.settings import config as settings_config
from exordos.common.table import get_table
from exordos.common.table import print_table
from exordos.common.table import show_data
from exordos.infra.driver import libvirt as libvirt_infra
from exordos.infra.libvirt import libvirt
from exordos.logger import ClickLogger
from exordos.stand import models as stand_models

ENTITY_COLLECTION = "/v1/realms/"
POOL_COLLECTION = "/v1/realms/pool/"
ENTITY = "realm"
REALM_SCOPE = "openid email profile project:default"
ECOSYSTEM_URL_PART = "/api/ecosystem/"

# An empty pool is an ordinary answer, not a broken command: the caller orders
# a realm the usual way instead. It carries an exit code of its own so a script
# can tell it from a failure without reading stderr.
POOL_EMPTY_EXIT_CODE = 3


class PoolEmptyError(click.ClickException):
    exit_code = POOL_EMPTY_EXIT_CODE


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


def get_stand_auth_data(
    ctx: click.Context,
    stand: "stand_models.Stand",
) -> dict | None:
    """Return auth data of the config realm pointing to the local stand."""
    core_ip = str(get_stand_core_ip(stand))
    for realm_name, realm_conf in (ctx.obj.cfg.get("realms") or {}).items():
        endpoint = realm_conf.get("endpoint", "")
        try:
            if exordos_utils.get_ip_from_url(endpoint) != core_ip:
                continue
        except (ValueError, RuntimeError):
            continue

        # Keep CLI overrides if the realm is already selected
        if realm_name == ctx.obj.auth_data.get("realm"):
            return ctx.obj.auth_data

        context_conf = settings_config.get_context(realm_conf)
        return {
            **ctx.obj.auth_data,
            "endpoint": endpoint,
            "username": context_conf.get("user"),
            "login": context_conf.get("login"),
            "password": context_conf.get("password"),
            "access_token": context_conf.get("access_token"),
            "refresh_token": context_conf.get("refresh_token"),
            "scope": None,
            "realm": realm_name,
        }
    return None


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
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def list_cmd(ctx: click.Context, output: str) -> None:
    def get_ecosystem_realms() -> dict[str, Realm]:
        # Get the list of realms from the ecosystem
        from yretry import defaults

        defaults.HTTP_RETRY_ATTEMPTS = 1
        try:
            ecosystem_client = get_ecosystem_client(ctx)
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
        try:
            return {
                str(ip): Realm(stand.name, str(ip), "local", "ACTIVE")
                for stand in infra.list_stands()
                if (ip := get_stand_core_ip(stand))
            }
        except subprocess.CalledProcessError:
            return {}

    def get_config_realms() -> dict[str, Realm]:
        # Get the list of remote realms by config
        realms = {}
        for config_realm_name, config_realm in ctx.obj.cfg.get("realms", {}).items():
            endpoint = config_realm.get("endpoint", "")
            if not endpoint:
                continue
            try:
                ip = exordos_utils.get_ip_from_url(endpoint)
            except (ValueError, RuntimeError):
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

    print_table(table, output)


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
    import questionary

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


@click.command("claim", help=f"Claim a warm {ENTITY} from the pool")
@click.pass_context
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help=f"Name to give the claimed {ENTITY}",
)
@click.option(
    "--description",
    type=str,
    required=False,
)
@click.option(
    "--ttl-hours",
    type=float,
    required=False,
    help=f"Delete the {ENTITY} automatically this many hours from now",
)
@click.option(
    "--ssh-public-key",
    envvar="SSH_PUBLIC_KEY",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=False,
    help="Path to the ssh public key",
)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
def claim_cmd(
    ctx: click.Context,
    name: str,
    description: str | None,
    ttl_hours: float | None,
    ssh_public_key: str | None,
    output: str,
) -> None:
    """Take one ready realm out of the pool.

    A warm realm is handed over already provisioned, so the answer is the
    realm itself -- and it is the only time its generated admin password is
    ever readable. An empty pool exits with POOL_EMPTY_EXIT_CODE.
    """
    ecosystem_client = get_ecosystem_client(ctx)
    data = {"name": name}
    if description is not None:
        data["description"] = description
    if ttl_hours is not None:
        # The platform refuses a naive deadline, so the offset travels with it.
        expires_at = datetime.datetime.now(datetime.timezone.utc) + (
            datetime.timedelta(hours=ttl_hours)
        )
        data["expires_at"] = expires_at.isoformat()
    if ssh_public_key is not None:
        with open(ssh_public_key, "r") as f:
            data["ssh_public_key"] = f.read()

    try:
        data = base_client.add_entity(
            ecosystem_client,
            POOL_COLLECTION,
            data,
            handle_conflict_error=False,
        )
    except bazooka_exc.ConflictError:
        raise PoolEmptyError(
            f"No warm {ENTITY} is ready in the pool; order one instead"
        ) from None

    show_data(data, output)


@click.command("delete", help="Delete realm")
@click.argument("name_uuid", type=str)
@click.pass_context
def delete_cmd(ctx: click.Context, name_uuid: str) -> None:
    from yretry import defaults

    # An unreachable realm or ecosystem must fail fast, not retry
    defaults.HTTP_RETRY_ATTEMPTS = 1

    def warn(message: str) -> None:
        # Teardown must never fail the caller, so problems are warnings
        click.secho(message, fg="yellow", err=True)

    # Local realms go first so a same-named ecosystem realm isn't touched
    infra = libvirt_infra.LibvirtInfraDriver()
    try:
        local_stands = infra.list_stands()
    except Exception as err:
        warn(f"Unable to list local stands: {err}")
        local_stands = []

    def clear_local_realm(stand: "stand_models.Stand") -> None:
        try:
            import time

            from rich.progress import track

            from exordos.cmd.em.elements.commands import clear

            # Clear the realm being deleted, not the current one
            auth_data = get_stand_auth_data(ctx, stand)
            if auth_data is None:
                warn(
                    f"Realm of local stand {stand.name} not found in config, "
                    "skipping elements cleanup"
                )
                return
            ctx.obj = ctx.obj._replace(auth_data=auth_data)

            click.echo(f"Clearing local realm {stand.name}...")
            was_cleared = ctx.invoke(
                clear,
                y=True,
            )

            if was_cleared:
                for _ in track(range(5), description="Waiting clearing resources..."):
                    time.sleep(1)
        except Exception as err:
            warn(
                f"Failed to clear local realm {stand.name}, "
                f"element resources may be left behind: {err}"
            )

    def delete_local_realm(stand: "stand_models.Stand") -> None:
        clear_local_realm(stand)
        click.echo(f"Deleting local realm {stand.name}...")
        try:
            infra.delete_stand(stand)
        except Exception as err:
            warn(
                f"Failed to delete local realm {stand.name}, "
                f"resources may be left behind: {err}"
            )

    for stand in local_stands:
        if stand.name == name_uuid:
            delete_local_realm(stand)
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
                    delete_local_realm(stand)
                    return None
        except Exception as err:
            warn(f"Unable to match local stands by endpoint: {err}")

    # Get the list of realms from the ecosystem
    try:
        ecosystem_client = get_ecosystem_client(ctx)
        ecosystem_realms = base_client.list_entities(
            ecosystem_client,
            ENTITY_COLLECTION,
        )
    except Exception:
        ecosystem_realms = []

    for realm in ecosystem_realms:
        if name_uuid in (realm["name"], realm["uuid"]):
            try:
                base_client.delete_entity(
                    ecosystem_client, ENTITY_COLLECTION, realm["uuid"]
                )
                click.echo(f"{ENTITY} {name_uuid} deleted")
            except Exception as err:
                warn(f"Failed to delete {ENTITY} {name_uuid}: {err}")
            return None

    warn(f"Realm {name_uuid} not found, nothing to delete")


@click.command("show", help="Show realm details")
@click.argument("name_uuid", type=str)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def show_cmd(ctx: click.Context, name_uuid: str, output: str) -> None:
    from yretry import defaults

    defaults.HTTP_RETRY_ATTEMPTS = 1
    ecosystem_client = get_ecosystem_client(ctx)
    try:
        data = base_client.get_entity(ecosystem_client, ENTITY_COLLECTION, name_uuid)
        show_data(data, output)
    except Exception:
        raise click.ClickException(f"{ENTITY} {name_uuid} not found")


@click.command("ssh_connection", help="Show realm ssh connection info")
@click.argument("name_uuid", type=str)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def ssh_connection_cmd(ctx: click.Context, name_uuid: str, output: str) -> None:
    from yretry import defaults

    defaults.HTTP_RETRY_ATTEMPTS = 1
    ecosystem_client = get_ecosystem_client(ctx)
    try:
        data = base_client.action_entity(
            ecosystem_client,
            ENTITY_COLLECTION,
            "ssh_connection",
            name_uuid,
            False,
        )
        show_data(data, output)
    except Exception:
        raise click.ClickException(f"{ENTITY} {name_uuid} not found")


realms_group.add_command(list_cmd, aliases=["l"])
realms_group.add_command(delete_cmd, aliases=["d"])
realms_group.add_command(add_cmd, aliases=["a"])
realms_group.add_command(claim_cmd, aliases=["c"])
realms_group.add_command(show_cmd, aliases=["get", "g"])
realms_group.add_command(ssh_connection_cmd)
