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
import subprocess
import time
import typing as tp

import rich_click as click

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
