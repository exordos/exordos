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
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.run import run_command
from exordos.common.run import runsh
from exordos.common.table import show_data
from exordos.logger import ClickLogger

ENTITY = "hypervisor"
ENTITY_COLLECTION = c.HYPERVISOR_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Machine type": "machine_type",
    "All cores": "all_cores",
    "Avail cores": "avail_cores",
    "All ram": "all_ram",
    "Avail ram": "avail_ram",
    "Status": "status",
}


hypervisors_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("add", help="Add a new hypervisor")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the hypervisor",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="hypervisor",
    help="Name of the hypervisor",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the hypervisor",
)
@click.option(
    "--avail_cores",
    type=int,
    required=False,
)
@click.option(
    "--avail_ram",
    type=int,
    required=False,
)
@click.option(
    "--cores_ratio",
    type=float,
    required=False,
)
@click.option(
    "--ram_ratio",
    type=float,
    required=False,
)
@click.option(
    "-m",
    "--machine_type",
    required=False,
    type=click.Choice(["VM", "HW"], case_sensitive=False),
)
@click.option(
    "-d",
    "--driver_spec",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: -d "
        "a=b -d c=d --driver_spec e=f"
    ),
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    avail_cores: int | None,
    avail_ram: int | None,
    cores_ratio: float | None,
    ram_ratio: float | None,
    machine_type: str | None,
    driver_spec: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    driver_spec = utils.convert_input_multiply(driver_spec)
    data: dict = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "driver_spec": driver_spec,
    }
    if avail_cores is not None:
        data["avail_cores"] = avail_cores
    if avail_ram is not None:
        data["avail_ram"] = avail_ram
    if cores_ratio is not None:
        data["cores_ratio"] = cores_ratio
    if ram_ratio is not None:
        data["ram_ratio"] = ram_ratio
    if machine_type is not None:
        data["machine_type"] = machine_type
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help=f"Description of the {ENTITY}",
)
@click.option(
    "--avail_cores",
    type=int,
    required=False,
)
@click.option(
    "--avail_ram",
    type=int,
    required=False,
)
@click.option(
    "--cores_ratio",
    type=float,
    required=False,
)
@click.option(
    "--ram_ratio",
    type=float,
    required=False,
)
@click.option(
    "-m",
    "--machine_type",
    required=False,
    type=click.Choice(["VM", "HW"], case_sensitive=False),
)
@click.option(
    "-d",
    "--driver_spec",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: -d "
        "a=b -d c=d --driver_spec e=f"
    ),
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    name: str | None,
    description: str,
    avail_cores: int | None,
    avail_ram: int | None,
    cores_ratio: float | None,
    ram_ratio: float | None,
    machine_type: str | None,
    driver_spec: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if avail_cores is not None:
        data["avail_cores"] = avail_cores
    if avail_ram is not None:
        data["avail_ram"] = avail_ram
    if cores_ratio is not None:
        data["cores_ratio"] = cores_ratio
    if ram_ratio is not None:
        data["ram_ratio"] = ram_ratio
    if machine_type is not None:
        data["machine_type"] = machine_type

    driver_spec = utils.convert_input_multiply(driver_spec)
    if driver_spec:
        data["driver_spec"] = driver_spec

    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


def _install_packages() -> None:
    """Install required Debian packages."""
    packages = [
        "qemu-system-x86",
        "qemu-utils",
        "libvirt-daemon-system",
        "libvirt-dev",
        "genisoimage",
        "unzip",
    ]
    cmd = ["apt-get", "update"]
    run_command(cmd)
    cmd = ["apt-get", "install", "-y"]
    cmd.extend(packages)
    run_command(cmd)


def _add_user_to_groups() -> None:
    """Add current user to libvirt and kvm groups."""
    username = os.environ.get("USER")
    if not username:
        raise click.ClickException("Cannot determine current username")
    else:
        click.echo(f"Current username: {username}")

    cmd = ["usermod", "-a", "-G", "libvirt", username]
    run_command(cmd)
    cmd = ["usermod", "-a", "-G", "kvm", username]
    run_command(cmd)


def _create_storage_pool(pool_name: str) -> None:
    """Create libvirt storage pool if it doesn't exist."""
    # Check if pool exists
    result = runsh("virsh pool-list --all").raise_on_result()
    if pool_name not in result.output:
        # Create storage pool
        cmd = [
            "virsh",
            "pool-define-as",
            pool_name,
            "dir",
            "--target",
            "/var/lib/libvirt/images",
        ]
        run_command(cmd)
        cmd = ["virsh", "pool-build", pool_name]
        run_command(cmd)
        cmd = ["virsh", "pool-start", pool_name]
        run_command(cmd)
        cmd = ["virsh", "pool-autostart", pool_name]
        run_command(cmd)


def _download_rom_file(version: str) -> None:
    """Download ROM file if it doesn't exist."""
    rom_filename = "1af41041.rom"
    rom_path = f"/usr/share/qemu/{rom_filename}"
    if not os.path.exists(rom_path):
        runsh(
            f"wget -O {rom_path} --timeout=30 https://repo.exordos.com/seed_os/{version}/{rom_filename}"
        ).raise_on_result()

    else:
        click.echo(f"ROM file {rom_path} already exists")


def _configure_libvirt() -> None:
    """Configure libvirt to enable TCP connection."""
    config_file = "/etc/libvirt/libvirtd.conf"

    # Read existing config
    try:
        with open(config_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise click.ClickException(f"Config file not found: {config_file}")

    # Add required lines if not present
    required_lines = ["listen_tcp = 1", 'listen_addr = "0.0.0.0"', 'auth_tcp = "none"']

    for line in required_lines:
        if line not in content:
            content += f"\n{line}"

    # Write back to file
    with open(config_file, "w") as f:
        f.write(content)

    # Restart services
    cmd = ["systemctl", "stop", "libvirtd"]
    run_command(cmd)
    cmd = ["systemctl", "enable", "--now", "libvirtd-tcp.socket"]
    run_command(cmd)
    cmd = ["systemctl", "start", "libvirtd"]
    run_command(cmd)


def _check_debian_like():
    """Check if the OS is Debian-like."""
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read()
            if "Debian" in content or "Ubuntu" in content or "Kali" in content:
                return True
    except FileNotFoundError:
        pass

    try:
        with open("/etc/debian_version", "r") as f:
            f.read()
            return True
    except FileNotFoundError:
        pass

    return False


def _install_packer() -> None:
    """Install packer."""

    try:
        run_command(["which", "packer"])
        click.echo("Packer is already installed")
        return None
    except Exception:
        pass

    cmd = ["mkdir", "-p", "/opt/packer"]
    run_command(cmd)
    # Version 1.9.2 is the latest free
    cmd = [
        "wget",
        "https://hashicorp-releases.yandexcloud.net/packer/1.9.2/packer_1.9.2_linux_amd64.zip",
        "-P",
        "/opt/packer",
    ]
    run_command(cmd)
    cmd = ["unzip", "/opt/packer/packer_1.9.2_linux_amd64.zip", "-d", "/opt/packer"]
    run_command(cmd)
    cmd = ["mv", "/opt/packer/packer", "/usr/local/bin/"]
    run_command(cmd)
    cmd = ["/usr/local/bin/packer", "-version"]
    run_command(cmd)
    return None


@hypervisors_group.command("init", help="Initialize hypervisor")
@click.option(
    "--romfile_version",
    type=str,
    default="latest",
    help="version of the rom file",
)
@click.option(
    "--pool_name",
    type=str,
    default="default",
    help="storage pool name",
)
@click.option(
    "-p",
    "--packer",
    show_default=True,
    is_flag=True,
    default=False,
    help="Install packer",
)
def init_cmd(romfile_version: str, pool_name: str, packer: bool) -> None:
    """Initialize hypervisor with all required components."""

    if not _check_debian_like():
        raise click.ClickException(
            "This command is only supported on Debian-based systems."
        )

    import subprocess

    if subprocess.call(["sudo", "-n", "true"], stderr=subprocess.DEVNULL) != 0:
        click.secho("Sudo privileges are required to proceed.", fg="yellow")
        if subprocess.call(["sudo", "-v"]) != 0:
            raise click.ClickException("Failed to obtain sudo privileges. Aborting.")

    log = ClickLogger()

    log.info("Installing required packages...")
    _install_packages()

    log.info("Adding user to required groups...")
    _add_user_to_groups()

    log.info("Setting up storage pool...")
    _create_storage_pool(pool_name)

    log.info("Checking ROM file...")
    _download_rom_file(romfile_version)

    log.info("Configuring libvirt...")
    _configure_libvirt()

    if packer:
        log.info("Configuring packer...")
        _install_packer()

    log.important("Hypervisor environment initialized successfully")


hypervisors_group.add_command(add_cmd, aliases=["a"])
hypervisors_group.add_command(update_cmd, aliases=["u"])
