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
from pathlib import Path
import subprocess
from unittest.mock import patch

from click.testing import CliRunner
import pytest
import rich_click as click

from exordos.backup.s3 import S3QcowBackuper
from exordos.cmd.backup.commands import snapshot_cmd
from exordos.cmd.backup.commands import snapshot_export_cmd
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
                "exordos.cmd.backup.commands.domains_for_backup",
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
                "exordos.cmd.backup.commands.domains_for_backup",
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
                "exordos.cmd.backup.commands.domains_for_backup",
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
                side_effect=lambda args: (
                    snapshots
                    if "-s" not in args
                    else b"\n".join(
                        s
                        for s in snapshots.splitlines()
                        if s.startswith((args[-1] + "@").encode())
                    )
                ),
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

    @pytest.mark.parametrize("yes", [True, False])
    def test_snapshot_restore_cmd_newer_snapshot_changes_nothing(self, yes) -> None:
        patches = self._patches(self.SNAPSHOTS + b"rpool/disks/c@snap2\n")
        p_domains, p_zvols, p_active, p_output, p_call = patches
        with (
            p_domains,
            p_zvols,
            p_active as active,
            p_output as output,
            p_call as check_call,
            patch("exordos.cmd.backup.commands.click.confirm") as confirm,
        ):
            with pytest.raises(click.UsageError, match="not the newest snapshot"):
                snapshot_restore_cmd.callback(
                    snapshot_name="snap1", name=(), exclude_name=(), yes=yes
                )
        assert output.call_args_list[-1].args[0] == [
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
            "rpool/disks/c",
        ]
        active.assert_not_called()
        confirm.assert_not_called()
        check_call.assert_not_called()


@pytest.mark.parametrize("flag", ["--name", "--no", "--exclude-name"])
def test_snapshot_restore_cmd_rejects_parent_filters(flag):
    from exordos.cmd.cli import exordos

    with patch("exordos.cmd.backup.commands.domains_for_backup") as domains:
        result = CliRunner().invoke(
            exordos, ["backup", flag, "vm1", "snapshot-restore", "snap1", "-y"]
        )
    assert result.exit_code == 2
    assert "Pass domain filters after the snapshot subcommand" in result.output
    domains.assert_not_called()


@pytest.mark.parametrize(
    "command",
    [
        "snapshot",
        "snapshot-export",
        "snapshot-list",
        "snapshot-delete",
        "snapshot-restore",
    ],
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
        patch("exordos.cmd.backup.commands.backup_local.LocalQcowBackuper") as backuper,
    ):
        result = CliRunner().invoke(exordos, ["backup", "snapshot-list"])

    assert result.exit_code == 0, result.output
    assert "pool/disk@snap1" in result.output
    backuper.assert_not_called()


class TestCmdSnapshotExport:
    @pytest.fixture
    def exports(self):
        with (
            patch(
                "exordos.cmd.backup.commands.domains_for_backup", return_value=["vm1"]
            ),
            patch(
                "exordos.cmd.backup.commands.libvirt.get_domain_zvols",
                return_value=["pool/a", "pool/b", "pool/a"],
            ),
            patch(
                "exordos.cmd.backup.commands._list_zfs_snapshots",
                return_value=["pool/a@old", "pool/a@new", "pool/b@old", "pool/b@new"],
            ) as snapshots,
            patch("exordos.cmd.backup.commands.subprocess.check_call") as send,
        ):
            yield snapshots, send

    @pytest.mark.parametrize("base", [None, "old"])
    def test_snapshot_export_cmd_writes_full_or_incremental_streams(
        self, tmp_path, exports, base
    ):
        _, send = exports

        def write_stream(command, **kwargs):
            if "stdout" in kwargs:
                kwargs["stdout"].write(b"zfs stream")

        send.side_effect = write_stream
        args = ["new", "-n", "vm1", "-d", str(tmp_path)]
        if base:
            args += ["--base-snapshot", base]
        result = CliRunner().invoke(snapshot_export_cmd, args)
        assert result.exit_code == 0, result.output
        commands = []
        for disk in ["a", "b"]:
            command = ["sudo", "zfs", "send"]
            if base:
                command += ["-i", f"pool/{disk}@old"]
            commands.append(command + [f"pool/{disk}@new"])
            suffix = "--from-old" if base else ""
            assert (
                tmp_path / f"pool%2F{disk}@new{suffix}.zfs"
            ).read_bytes() == b"zfs stream"
        assert [c.args[0] for c in send.call_args_list] == [
            c[:3] + ["-n"] + c[3:] for c in commands
        ] + commands
        assert len(list(tmp_path.iterdir())) == 2

    @pytest.mark.parametrize("missing", ["pool/b@old", "pool/b@new"])
    def test_snapshot_export_cmd_missing_snapshot_exports_nothing(
        self, tmp_path, exports, missing
    ):
        snapshots, send = exports
        snapshots.return_value.remove(missing)
        result = CliRunner().invoke(
            snapshot_export_cmd, ["new", "--base-snapshot", "old", "-d", str(tmp_path)]
        )
        assert result.exit_code == 2
        assert missing in result.output
        send.assert_not_called()
        assert not list(tmp_path.iterdir())

    def test_snapshot_export_cmd_existing_file_exports_nothing(self, tmp_path, exports):
        _, send = exports
        path = tmp_path / "pool%2Fb@new.zfs"
        path.write_bytes(b"existing backup")
        result = CliRunner().invoke(snapshot_export_cmd, ["new", "-d", str(tmp_path)])
        assert result.exit_code == 2
        send.assert_not_called()
        assert path.read_bytes() == b"existing backup"

    def test_snapshot_export_cmd_invalid_base_exports_nothing(self, tmp_path, exports):
        _, send = exports
        send.side_effect = [None, subprocess.CalledProcessError(1, "zfs send")]
        result = CliRunner().invoke(
            snapshot_export_cmd, ["old", "--base-snapshot", "new", "-d", str(tmp_path)]
        )
        assert result.exit_code != 0
        assert not list(tmp_path.iterdir())
        assert all("-n" in c.args[0] for c in send.call_args_list)

    def test_snapshot_export_cmd_failed_send_removes_partial_file(
        self, tmp_path, exports
    ):
        _, send = exports

        def fail_send(command, **kwargs):
            if "stdout" in kwargs:
                kwargs["stdout"].write(b"partial stream")
                raise subprocess.CalledProcessError(1, command)

        send.side_effect = fail_send
        result = CliRunner().invoke(snapshot_export_cmd, ["new", "-d", str(tmp_path)])
        assert result.exit_code != 0
        assert not list(tmp_path.iterdir())

    def test_snapshot_export_cmd_no_disks_exports_nothing(self, tmp_path, exports):
        snapshots, send = exports
        with patch(
            "exordos.cmd.backup.commands.libvirt.get_domain_zvols", return_value=[]
        ):
            result = CliRunner().invoke(
                snapshot_export_cmd, ["new", "-d", str(tmp_path)]
            )
        assert result.exit_code == 0
        assert "No zvol disks found" in result.output
        snapshots.assert_not_called()
        send.assert_not_called()

    @pytest.mark.parametrize(
        "args",
        [
            ["new", "-n", "vm1", "--no", "vm2"],
            ["pool/a@new"],
            ["new", "--base-snapshot", "pool/a@old"],
        ],
    )
    def test_snapshot_export_cmd_invalid_options_exports_nothing(
        self, tmp_path, exports, args
    ):
        _, send = exports
        result = CliRunner().invoke(snapshot_export_cmd, args + ["-d", str(tmp_path)])
        assert result.exit_code == 2
        send.assert_not_called()

    @pytest.mark.parametrize("base", [None, "old"])
    @pytest.mark.parametrize("keep_local", [False, True])
    def test_snapshot_export_cmd_uploads_to_s3(
        self, tmp_path, exports, base, keep_local
    ):
        _, send = exports
        config = tmp_path / "s3.yaml"
        config.touch()
        output = tmp_path / "exports"
        backuper = S3QcowBackuper(
            "https://s3.example.test", "access", "secret", "host", "bucket"
        )
        received = []

        def write_stream(command, **kwargs):
            if "stdout" in kwargs:
                kwargs["stdout"].write(b"zfs stream")

        def upload(stream, bucket, key, size):
            stream.seek(0)
            received.append((bucket, key, size, stream.read()))

        send.side_effect = write_stream
        args = ["new", "--s3-config", str(config), "--s3-prefix", "/host/vm1/"]
        if base:
            args += ["--base-snapshot", base]
        if keep_local:
            args += ["-d", str(output)]
        with (
            patch(
                "exordos.cmd.backup.commands.utils.load_driver", return_value=backuper
            ) as load,
            patch("exordos.backup.s3.s3_client.S3BackupClient") as client,
        ):
            client.return_value.upload.side_effect = upload
            result = CliRunner().invoke(snapshot_export_cmd, args)
        assert result.exit_code == 0, result.output
        load.assert_called_once_with(str(config))
        suffix = "--from-old" if base else ""
        assert received == [
            ("bucket", f"host/vm1/pool%2F{disk}@new{suffix}.zfs", 10, b"zfs stream")
            for disk in ("a", "b")
        ]
        if keep_local:
            assert len(list(output.iterdir())) == 2
            assert all(p.read_bytes() == b"zfs stream" for p in output.iterdir())
        else:
            assert not output.exists()

    @pytest.mark.parametrize("keep_local", [False, True])
    def test_snapshot_export_cmd_failed_upload_cleans_temp_keeps_local(
        self, tmp_path, exports, keep_local
    ):
        _, send = exports
        config = tmp_path / "s3.yaml"
        config.touch()
        output = tmp_path / "exports"
        backuper = S3QcowBackuper(
            "https://s3.example.test", "access", "secret", "host", "bucket"
        )
        temporary_paths = []

        def write_stream(command, **kwargs):
            if "stdout" in kwargs:
                temporary_paths.append(Path(kwargs["stdout"].name))
                kwargs["stdout"].write(b"zfs stream")

        send.side_effect = write_stream
        args = ["new", "--s3-config", str(config)]
        if keep_local:
            args += ["-d", str(output)]
        with (
            patch(
                "exordos.cmd.backup.commands.utils.load_driver", return_value=backuper
            ),
            patch.object(
                backuper, "upload_snapshot", side_effect=RuntimeError("upload failed")
            ),
        ):
            result = CliRunner().invoke(snapshot_export_cmd, args)
        assert result.exit_code != 0
        assert str(result.exception) == "upload failed"
        assert len(temporary_paths) == 1
        assert not temporary_paths[0].exists()
        if keep_local:
            assert (output / "pool%2Fa@new.zfs").read_bytes() == b"zfs stream"
            assert len(list(output.iterdir())) == 1

    def test_snapshot_export_cmd_no_destination_exports_nothing(self, exports):
        _, send = exports
        result = CliRunner().invoke(snapshot_export_cmd, ["new"])
        assert result.exit_code == 2
        assert "Specify --backup-dir, --s3-config, or both" in result.output
        send.assert_not_called()

    def test_snapshot_export_cmd_wrong_s3_driver_exports_nothing(
        self, tmp_path, exports
    ):
        _, send = exports
        config = tmp_path / "local.yaml"
        config.touch()
        with patch(
            "exordos.cmd.backup.commands.utils.load_driver", return_value=object()
        ):
            result = CliRunner().invoke(
                snapshot_export_cmd, ["new", "--s3-config", str(config)]
            )
        assert result.exit_code == 2
        assert "must configure S3QcowBackuper" in result.output
        send.assert_not_called()

    def test_snapshot_export_cmd_failed_send_does_not_upload(self, tmp_path, exports):
        _, send = exports
        config = tmp_path / "s3.yaml"
        config.touch()
        backuper = S3QcowBackuper(
            "https://s3.example.test", "access", "secret", "host", "bucket"
        )
        send.side_effect = [None, None, subprocess.CalledProcessError(1, "zfs send")]
        with (
            patch(
                "exordos.cmd.backup.commands.utils.load_driver", return_value=backuper
            ),
            patch.object(backuper, "upload_snapshot") as upload,
        ):
            result = CliRunner().invoke(
                snapshot_export_cmd, ["new", "--s3-config", str(config)]
            )
        assert result.exit_code != 0
        upload.assert_not_called()
