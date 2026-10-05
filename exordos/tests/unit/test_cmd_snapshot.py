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
from unittest.mock import patch

from click.testing import CliRunner
import pytest
import rich_click as click

from exordos.cmd.backup.commands import snapshot_cmd
from exordos.cmd.backup.commands import snapshot_restore_cmd
from exordos.infra.libvirt import libvirt

DOMAIN_XML = """
<domain>
  <devices>
    <disk type='block' device='disk'>
      <source dev='/dev/zvol/rpool/disks/871e0ce8' index='2'/>
    </disk>
    <disk type='block' device='disk'>
      <source dev='/dev/zvol/rpool/disks/8d9d984b' index='1'/>
    </disk>
    <disk type='file' device='disk'>
      <source file='/var/lib/libvirt/images/vm.qcow2'/>
    </disk>
  </devices>
</domain>
"""


class TestGetDomainZvols:
    def test_get_domain_zvols_returns_zvol_datasets(self) -> None:
        with patch(
            "exordos.infra.libvirt.libvirt.subprocess.check_output",
            return_value=DOMAIN_XML.encode(),
        ):
            zvols = libvirt.get_domain_zvols("vm1")

        assert zvols == ["rpool/disks/871e0ce8", "rpool/disks/8d9d984b"]


class TestCmdSnapshot:
    def test_snapshot_cmd_creates_all_snapshots_in_one_call(self) -> None:
        zvols = {"vm1": ["rpool/disks/a", "rpool/disks/b"], "vm2": ["rpool/disks/c"]}

        with (
            patch(
                "exordos.cmd.backup.commands._domains_for_backup",
                return_value=["vm2", "vm1"],
            ) as domains_for_backup,
            patch(
                "exordos.cmd.backup.commands.libvirt.get_domain_zvols",
                side_effect=zvols.__getitem__,
            ),
            patch("exordos.cmd.backup.commands.subprocess.check_call") as check_call,
        ):
            snapshot_cmd.callback(name=(), exclude_name=(), snapshot_name="snap1")

        domains_for_backup.assert_called_once_with((), (), raise_on_domain_absence=True)
        check_call.assert_called_once_with(
            [
                "sudo",
                "zfs",
                "snapshot",
                "rpool/disks/a@snap1",
                "rpool/disks/b@snap1",
                "rpool/disks/c@snap1",
            ]
        )

    def test_snapshot_cmd_skips_when_no_zvols(self) -> None:
        with (
            patch(
                "exordos.cmd.backup.commands._domains_for_backup",
                return_value=["vm1"],
            ),
            patch(
                "exordos.cmd.backup.commands.libvirt.get_domain_zvols",
                return_value=[],
            ),
            patch("exordos.cmd.backup.commands.subprocess.check_call") as check_call,
        ):
            snapshot_cmd.callback(name=(), exclude_name=(), snapshot_name=None)

        check_call.assert_not_called()

    def test_snapshot_cmd_name_and_exclude_name_conflict(self) -> None:
        with pytest.raises(click.UsageError):
            snapshot_cmd.callback(
                name=("vm1",), exclude_name=("vm2",), snapshot_name=None
            )


class TestCmdSnapshotRestore:
    ZVOLS = {"vm1": ["rpool/disks/a", "rpool/disks/b"], "vm2": ["rpool/disks/c"]}
    SNAPSHOTS = b"rpool/disks/a@snap1\nrpool/disks/b@snap1\nrpool/disks/c@snap1\n"

    def _patches(self, snapshots: bytes = SNAPSHOTS):
        return (
            patch(
                "exordos.cmd.backup.commands._domains_for_backup",
                return_value=["vm2", "vm1"],
            ),
            patch(
                "exordos.cmd.backup.commands.libvirt.get_domain_zvols",
                side_effect=self.ZVOLS.__getitem__,
            ),
            patch(
                "exordos.cmd.backup.commands.libvirt.is_active_domain",
                side_effect=lambda d: d == "vm1",
            ),
            patch(
                "exordos.cmd.backup.commands.subprocess.check_output",
                return_value=snapshots,
            ),
            patch("exordos.cmd.backup.commands.subprocess.check_call"),
        )

    def test_snapshot_restore_cmd_stops_rolls_back_and_starts_active(self) -> None:
        p_domains, p_zvols, p_active, p_output, p_call = self._patches()
        with p_domains, p_zvols, p_active, p_output, p_call as check_call:
            snapshot_restore_cmd.callback(
                snapshot_name="snap1", name=(), exclude_name=(), yes=True
            )

        cmds = [c.args[0] for c in check_call.call_args_list]
        assert cmds == [
            ["sudo", "virsh", "destroy", "vm1"],
            ["sudo", "zfs", "rollback", "rpool/disks/a@snap1"],
            ["sudo", "zfs", "rollback", "rpool/disks/b@snap1"],
            ["sudo", "virsh", "start", "vm1"],
            ["sudo", "zfs", "rollback", "rpool/disks/c@snap1"],
        ]

    def test_snapshot_restore_cmd_missing_snapshot_changes_nothing(self) -> None:
        p_domains, p_zvols, p_active, p_output, p_call = self._patches(
            snapshots=b"rpool/disks/a@snap1\n"
        )
        with p_domains, p_zvols, p_active, p_output, p_call as check_call:
            with pytest.raises(click.UsageError, match="rpool/disks/b@snap1"):
                snapshot_restore_cmd.callback(
                    snapshot_name="snap1", name=(), exclude_name=(), yes=True
                )

        check_call.assert_not_called()

    def test_snapshot_restore_cmd_aborts_without_confirmation(self) -> None:
        p_domains, p_zvols, p_active, p_output, p_call = self._patches()
        with (
            p_domains,
            p_zvols,
            p_active,
            p_output,
            p_call as check_call,
            patch(
                "exordos.cmd.backup.commands.click.confirm",
                side_effect=click.exceptions.Abort,
            ) as confirm,
        ):
            with pytest.raises(click.exceptions.Abort):
                snapshot_restore_cmd.callback(
                    snapshot_name="snap1", name=(), exclude_name=(), yes=False
                )

        confirm.assert_called_once()
        check_call.assert_not_called()

    def test_snapshot_restore_cmd_name_and_exclude_name_conflict(self) -> None:
        with pytest.raises(click.UsageError):
            snapshot_restore_cmd.callback(
                snapshot_name="snap1", name=("vm1",), exclude_name=("vm2",), yes=True
            )


@pytest.mark.parametrize(
    "command", ["snapshot", "snapshot-list", "snapshot-delete", "snapshot-restore"]
)
def test_snapshot_commands_registered_under_backup(command):
    from exordos.cmd.cli import exordos
    from exordos.cmd.compute.hypervisors.commands import hypervisors_group

    assert command in exordos.commands["backup"].commands
    assert command not in hypervisors_group.commands


def test_snapshot_list_via_backup_does_not_start_backuper():
    from exordos.cmd.cli import exordos

    with (
        patch(
            "exordos.cmd.backup.commands.subprocess.check_output",
            return_value=b"pool/disk@snap1\n",
        ),
        patch("exordos.cmd.stand.commands.backup_local.LocalQcowBackuper") as backuper,
    ):
        result = CliRunner().invoke(exordos, ["backup", "snapshot-list"])

    assert result.exit_code == 0, result.output
    assert "pool/disk@snap1" in result.output
    backuper.assert_not_called()
