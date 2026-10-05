#    Copyright 2026 Genesis Corporation.
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
import fnmatch
import os
import subprocess
import time
import typing as tp

import rich_click as click

from exordos import utils
from exordos.backup import base as backup_base
from exordos.backup import local as backup_local
from exordos.cmd.backup.constants import BackupPeriod
from exordos.infra.libvirt import libvirt


def domains_for_backup(
    names: tp.List[str] | None = None,
    exclude_names: tp.List[str] | None = None,
    raise_on_domain_absence: bool = False,
) -> tp.List[str]:
    domains = set(libvirt.list_domains())
    names = set(names or [])
    exclude_names = set(exclude_names or [])

    # Check if the specified domains exist
    if raise_on_domain_absence and (names - domains):
        diff = ", ".join(names - domains)
        raise click.UsageError(f"Domains {diff} not found")

    if names:
        domains &= names

    if exclude_names:
        domains = {
            d
            for d in domains
            if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_names)
        }

    return list(domains)


@click.command("snapshot", help="Create ZFS snapshots of libvirt domain disks")
@click.option(
    "-n",
    "--name",
    default=None,
    multiple=True,
    help="Name of the libvirt domain, if not provided, all will be snapshotted",
)
@click.option(
    "--no",
    "--exclude-name",
    "exclude_name",
    multiple=True,
    help="Name or pattern of libvirt domains to exclude from snapshot",
)
@click.option(
    "-s",
    "--snapshot-name",
    default=None,
    help="Snapshot name. Defaults to snap-<YYYYmmdd-HHMMSS>",
)
def snapshot_cmd(
    name: tp.List[str] | None,
    exclude_name: tp.List[str] | None,
    snapshot_name: str | None,
) -> None:
    if name and exclude_name:
        raise click.UsageError(
            "Cannot specify both --name and --no/--exclude-name options at the same time."
        )

    snapshot_name = snapshot_name or f"snap-{time.strftime('%Y%m%d-%H%M%S')}"
    domains = domains_for_backup(name, exclude_name, raise_on_domain_absence=True)

    snapshots = set()
    for domain in sorted(domains):
        for zvol in libvirt.get_domain_zvols(domain):
            click.secho(f"{domain}: {zvol}@{snapshot_name}")
            snapshots.add(f"{zvol}@{snapshot_name}")

    if not snapshots:
        click.secho("No zvol disks found", fg="yellow")
        return

    # A single `zfs snapshot` call creates all snapshots atomically
    subprocess.check_call(["sudo", "zfs", "snapshot", *sorted(snapshots)])
    click.secho(f"Created {len(snapshots)} snapshots", fg="green")


def _list_zfs_snapshots() -> list[str]:
    out = subprocess.check_output(
        ["sudo", "zfs", "list", "-H", "-t", "snapshot", "-o", "name"]
    )
    return sorted(out.decode().splitlines())


@click.command("snapshot-list", help="List all ZFS snapshots on the local hypervisor")
def snapshot_list_cmd() -> None:
    snapshots = _list_zfs_snapshots()
    if not snapshots:
        click.secho("No ZFS snapshots found", fg="yellow")
        return
    for snapshot in snapshots:
        click.echo(snapshot)


@click.command("snapshot-delete", help="Delete ZFS snapshots on the local hypervisor")
@click.argument("snapshots", nargs=-1)
@click.option("--all", "delete_all", is_flag=True, help="Delete all ZFS snapshots")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
def snapshot_delete_cmd(
    snapshots: tuple[str, ...], delete_all: bool, yes: bool
) -> None:
    if bool(snapshots) == delete_all:
        raise click.UsageError("Specify full snapshot names or --all, but not both.")

    existing = _list_zfs_snapshots()
    if delete_all:
        selected = existing
    else:
        missing = sorted(set(snapshots) - set(existing))
        if missing:
            raise click.UsageError(f"Snapshots not found: {', '.join(missing)}")
        selected = sorted(set(snapshots))

    if not selected:
        click.secho("No ZFS snapshots found", fg="yellow")
        return
    for snapshot in selected:
        click.echo(snapshot)
    if not yes:
        click.confirm(f"Delete {len(selected)} ZFS snapshots?", abort=True)

    for snapshot in selected:
        subprocess.check_call(["sudo", "zfs", "destroy", snapshot])
        click.secho(f"{snapshot}: deleted", fg="green")


@click.command(
    "snapshot-restore", help="Restore libvirt domain disks from ZFS snapshots"
)
@click.argument("snapshot_name")
@click.option(
    "-n",
    "--name",
    default=None,
    multiple=True,
    help="Name of the libvirt domain, if not provided, all will be restored",
)
@click.option(
    "--no",
    "--exclude-name",
    "exclude_name",
    multiple=True,
    help="Name or pattern of libvirt domains to exclude from restore",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation",
)
def snapshot_restore_cmd(
    snapshot_name: str,
    name: tp.List[str] | None,
    exclude_name: tp.List[str] | None,
    yes: bool,
) -> None:
    if name and exclude_name:
        raise click.UsageError(
            "Cannot specify both --name and --no/--exclude-name options at the same time."
        )

    domains = domains_for_backup(name, exclude_name, raise_on_domain_absence=True)
    domain_zvols = {d: libvirt.get_domain_zvols(d) for d in sorted(domains)}
    domain_zvols = {d: zvols for d, zvols in domain_zvols.items() if zvols}

    if not domain_zvols:
        click.secho("No zvol disks found", fg="yellow")
        return

    # Check all snapshots exist before touching any domain
    out = subprocess.check_output(
        ["sudo", "zfs", "list", "-H", "-t", "snapshot", "-o", "name"]
    )
    existing = set(out.decode().split())
    missing = [
        f"{zvol}@{snapshot_name}"
        for zvols in domain_zvols.values()
        for zvol in zvols
        if f"{zvol}@{snapshot_name}" not in existing
    ]
    if missing:
        raise click.UsageError(f"Snapshots not found: {', '.join(missing)}")

    # Reject blocked rollbacks before stopping or changing any domain.
    for zvol in sorted({zvol for zvols in domain_zvols.values() for zvol in zvols}):
        out = subprocess.check_output(
            [
                "sudo",
                "zfs",
                "list",
                "-H",
                "-t",
                "snapshot",
                "-o",
                "name",
                "-s",
                "createtxg",
                "-d",
                "1",
                zvol,
            ]
        )
        snapshots = out.decode().split()
        if not snapshots or snapshots[-1] != f"{zvol}@{snapshot_name}":
            raise click.UsageError(
                f"Snapshot {zvol}@{snapshot_name} is not the newest snapshot"
            )

    for domain, zvols in domain_zvols.items():
        click.secho(f"{domain}: {', '.join(zvols)}")

    if not yes:
        click.confirm(
            "Running domains will be stopped and their disks rolled back "
            f"to '{snapshot_name}'. Continue?",
            abort=True,
        )

    for domain, zvols in domain_zvols.items():
        active = libvirt.is_active_domain(domain)
        if active:
            subprocess.check_call(
                ["sudo", "virsh", "destroy", domain], stdout=subprocess.DEVNULL
            )

        for zvol in zvols:
            subprocess.check_call(
                ["sudo", "zfs", "rollback", f"{zvol}@{snapshot_name}"]
            )

        if active:
            subprocess.check_call(
                ["sudo", "virsh", "start", domain], stdout=subprocess.DEVNULL
            )

        click.secho(f"{domain}: restored", fg="green")


def _start_validation_type(start: str | None) -> time.struct_time | None:
    if start is None:
        return None

    try:
        return time.strptime(start, "%H:%M:%S")
    except ValueError:
        raise click.UsageError("Invalid '--start' format. Use HH:MM:SS, e.g., 16:00:00")


@click.group(
    "backup", invoke_without_command=True, help="Backup the current installation"
)
@click.option(
    "--config",
    default=None,
    type=click.Path(),
    help="Path to the backuper configuration file",
)
@click.option(
    "-n",
    "--name",
    default=None,
    multiple=True,
    help="Name of the libvirt domain, if not provided, all will be backed up",
)
@click.option(
    "-d",
    "--backup-dir",
    default=".",
    type=click.Path(),
    help="Directory where backups will be stored",
)
@click.option(
    "-p",
    "--period",
    default=BackupPeriod.D1.value,
    type=click.Choice([p.value for p in BackupPeriod]),
    show_default=True,
    help="the regularity of backups",
)
@click.option(
    "-o",
    "--offset",
    default=None,
    type=click.Choice([p.value for p in BackupPeriod]),
    show_default=True,
    help=(
        "The time offset of the first backup. If not provided, "
        "the same value as the period will be used"
    ),
)
@click.option(
    "--start",
    default=None,
    type=_start_validation_type,
    help=(
        "Time of day to start backup in format HH:MM:SS. "
        "Cannot be used together with --offset. If provided, "
        "period must be >= 1d."
    ),
)
@click.option(
    "--oneshot",
    show_default=True,
    is_flag=True,
    help="Do a backup once and exit",
)
@click.option(
    "-c",
    "--compress",
    show_default=True,
    is_flag=True,
    help="Compress the backup.",
)
@click.option(
    "-e",
    "--encrypt",
    show_default=True,
    is_flag=True,
    help=(
        "Encrypt the backup. Works only with the compress flag. "
        "Use environment variable to specify the encryption key "
        "and the initialization vector: "
        "GEN_DEV_BACKUP_KEY and GEN_DEV_BACKUP_IV"
    ),
)
@click.option(
    "-s",
    "--min-free-space",
    default=50,
    type=int,
    show_default=True,
    help=(
        "Free disk space shouldn't be lower than this threshold. "
        "If the space becomes lower, the backup process is stopped. "
        "The value is in GB."
    ),
)
@click.option(
    "-r",
    "--rotate",
    default=5,
    type=int,
    show_default=True,
    help=(
        "Maximum number of backups to keep. The oldest backups are deleted. "
        "`0` means no rotation."
    ),
)
@click.option(
    "--no",
    "--exclude-name",
    "exclude_name",
    multiple=True,
    help="Name or pattern of libvirt domains to exclude from backup",
)
def backup_cmd(
    config: str | None,
    name: tp.List[str] | None,
    exclude_name: tp.List[str] | None,
    backup_dir: str,
    period: str,
    offset: str | None,
    start: time.struct_time | None,
    oneshot: bool,
    compress: bool,
    encrypt: bool,
    min_free_space: int,
    rotate: int,
) -> None:
    ctx = click.get_current_context(silent=True)
    if ctx is not None and ctx.invoked_subcommand is not None:
        if name or exclude_name:
            raise click.UsageError("Pass domain filters after the snapshot subcommand.")
        return

    period = BackupPeriod(period)
    if offset:
        offset = BackupPeriod(offset)

    # Forbid using both include and exclude options
    if name and exclude_name:
        raise click.UsageError(
            "Cannot specify both --name and --no/--exclude-name options at the same time."
        )

    # Default local backuper if no config is provided
    if config is None:
        backuper = backup_local.LocalQcowBackuper(
            backup_dir=backup_dir,
            min_free_disk_space_gb=min_free_space,
        )
    else:
        backuper = utils.load_driver(config)

    # Need to specify encryption key and initialization vector via
    # environment variables.
    if encrypt:
        try:
            backup_base.EncryptionCreds.validate_env()
        except ValueError:
            raise click.UsageError(
                (
                    "Define environment variables GEN_DEV_BACKUP_KEY "
                    "and GEN_DEV_BACKUP_IV. "
                    "Key and IV must be greater or equal than "
                    f"{backup_base.EncryptionCreds.MIN_LEN} bytes and less "
                    f"or equal to {backup_base.EncryptionCreds.LEN} bytes."
                )
            )

        encryption = backup_base.EncryptionCreds.from_env()
    else:
        encryption = None

    # Do a single backup and exit
    if oneshot:
        domains = domains_for_backup(name, exclude_name, raise_on_domain_absence=True)
        backuper.backup(domains, compress, encryption)
        return

    # Do periodic backups
    click.secho(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # The `start` option validation
    if start is None:
        # Default behavior: use offset (or period if offset not provided)
        offset = offset or period
        ts = time.time() + offset.timeout
        click.secho(
            f"Next backup at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
        )
        time.sleep(offset.timeout)
    else:
        # Validate mutually exclusive options: --start and --offset
        if offset is not None:
            raise click.UsageError(
                "Options '--start' and '--offset' cannot be used together. "
                "Choose one. By default, --offset is used."
            )

        # If --start is specified, period must be at least daily
        if period.timeout < BackupPeriod.D1.timeout:
            raise click.UsageError(
                "The '--start' option requires the period to be at least 1 day (1d)."
            )

        start_sec = start.tm_hour * 3600 + start.tm_min * 60 + start.tm_sec
        now_ts = time.time()
        now = time.localtime(now_ts)
        now_sec = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec

        if now_sec < start_sec:
            delta = start_sec - now_sec
        else:
            delta = 24 * 3600 - now_sec + start_sec

        ts = now_ts + delta
        click.secho(
            f"Next backup at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
        )
        time.sleep(delta)

    # Next runs happen every 'period' seconds from the aligned start
    next_ts = time.time() + period.timeout

    # Do periodic backups
    while True:
        # Need to refresh the list of domains since it could have changed
        domains = domains_for_backup(name, exclude_name)

        click.secho(f"Backup started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        backuper.backup(domains, compress, encryption)
        click.secho(
            "Next backup at: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_ts))}"
        )

        # Rotate old backups
        backuper.rotate(rotate)

        timeout = next_ts - time.time()
        timeout = 0 if timeout < 0 else timeout
        next_ts += period.timeout

        time.sleep(timeout)


@click.command("backup-decrypt", help="Decrypt a backup file")
@click.argument("path", type=click.Path(exists=True))
def backup_decrypt_cmd(path: str) -> None:
    # Need to specify encryption key and initialization vector via
    # environment variables.

    try:
        backup_base.EncryptionCreds.validate_env()
    except ValueError:
        raise click.UsageError(
            (
                "Define environment variables GEN_DEV_BACKUP_KEY "
                "and GEN_DEV_BACKUP_IV. "
                "Key and IV must be greater or equal than "
                f"{backup_base.EncryptionCreds.MIN_LEN} bytes and less or "
                f"equal to {backup_base.EncryptionCreds.LEN} bytes."
            )
        )

    encryption = backup_base.EncryptionCreds.from_env()

    if os.path.isdir(path):
        for file in os.listdir(path):
            _path = os.path.join(path, file)
            utils.decrypt_file(
                _path,
                encryption.key,
                encryption.iv,
            )
            click.secho(f"The {_path} file has been decrypted.", fg="green")
        return

    utils.decrypt_file(
        path,
        encryption.key,
        encryption.iv,
    )
    click.secho(f"The {path} file has been decrypted.", fg="green")


backup_cmd.add_command(snapshot_cmd)
backup_cmd.add_command(snapshot_list_cmd)
backup_cmd.add_command(snapshot_delete_cmd)
backup_cmd.add_command(snapshot_restore_cmd)
