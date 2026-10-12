# Backups

The `backup` command is used to backup the current installation.

The basic syntax of the `backup` command is as follows:

```bash
exordos backup -d /path/to/backup/directory
```

This will backup the current installation to the specified directory. The command will create a subdirectory for each domain and copy its disks to the specified directory. The backup will repeat every 24 hours by default.

To configure period of backup, run the following command:

```bash
exordos backup -d /path/to/backup/directory -p 1h
```

To do a backup once and exit:

```bash
exordos backup -d /path/to/backup/directory -oneshot
```

## Basic Backup

Run backup periodically of all libvirt domains and store it in the current directory:

```bash
exordos backup
```

## Backup Specific Domain

Run backup periodically of a specific libvirt domain and store it in the current directory:

```bash
exordos backup -n domain-name
```

## Exclude Specific Domains

Use `--exclude-name` (or `--no`) to skip specific domains or patterns. `--name` and `--exclude-name/--no` cannot be used together.

```bash
exordos backup --exclude-name domain-foo --exclude-name domain-bar --exclude-name "domain-stand-*"
```

## Custom Periodic Backup

Run backup periodically of all libvirt domains and store it in the current directory:

```bash
exordos backup -p 1h
```

Available periods are: `1m`, `5m`, `15m`, `30m`, `1h`, `3h`, `6h`, `12h`, `1d`, `3d`, `7d`

## OneShot Backup

Run backup of all libvirt domains once and store it in the current directory:

```bash
exordos backup -oneshot
```

## Compressed Backup

Run backup of all libvirt domains and store a compressed archive in the current directory:

```bash
exordos backup --compress
```

## Encrypted Backup

Run backup of all libvirt domains and store an encrypted archive in the current directory.

> NOTE: Works only with the `--compress` flag.

Set the environment variables `GEN_DEV_BACKUP_KEY` and `GEN_DEV_BACKUP_IV` to encrypt the backup. The key and IV must be greater or equal to 6 bytes and less or equal to 16 bytes.

```bash
export GEN_DEV_BACKUP_KEY=secret_key
export GEN_DEV_BACKUP_IV=secret_iv

exordos backup --compress --encrypt
```

For decryption, use the `exordos backup-decrypt` command:

```bash
exordos backup-decrypt backup.tar.gz.encrypted
```

## Restore backups

Let's consider a couple of scenarios to restore a particular machine from the backup. The backup can be as an entcrypted archive, archive or a directory. So the first step is to convert the backup to a directory:

Optional decryption of the backup

```bash
exordos backup-decrypt backup.tar.gz.encrypted
```

Optional decompression of the backup

```bash
tar -xzf backup.tar.gz
```

The backup directory can consist several subdirectories for each domain. Let's consider the following example:

```sh
.
├── a4cb5e6e-domain-foo
│   └── domain.xml
│   └── f5e1a096-1093-4d80-a21b-d453281360d5_a4cb5e6e-1ef0-450b-b28c-9638fe6e7eb9.qcow2
├── 444b5183-domain-bar
│   └── domain.xml
│   └── 005ff0d3-3945-46d0-8704-27c645dfe3ab_444b5183-a049-4415-86c2-c3c8262c1403.qcow2
```

- `domain.xml` is the domain configuration file
- `*.qcow2` is the disk image

The most frequent use case is to restore a specific domain from the backup. Let's consider we already have a running domain `foo` but with corrupted disk and want to restore it from the backup. We can use the following commands:

```bash
# Shut down the domain
virsh shutdown foo

# Determine current disk path
sudo virsh domblklist foo

# Replace the disk
cp backup/a4cb5e6e-domain-foo/f5e1a096-1093-4d80-a21b-d453281360d5_a4cb5e6e-1ef0-450b-b28c-9638fe6e7eb9.qcow2 /var/lib/libvirt/images/foo.qcow2

# Start the domain
virsh start foo
```

## Rotation

For the periodic backup, you can set the number of backups to keep (rotation number). The default value is 5. Use the `--rotate` option:

```bash
exordos backup --rotate 10
```

## Prevent disk overflow

Backups can take a lot of disk space and it can be a reason to crash the whole system if a disk will be full. To prevent such a situation you can set a threshold for disk space that should be free. If during a backup process this threshold will be reached, the backup process will stop. Use the `--min-free-space` option to set the threshold in GB.

```bash
exordos backup --min-free-space 50
```

## ZFS Snapshots

The `backup snapshot` command creates ZFS snapshots of all zvol disks attached to libvirt domains. All snapshots are created atomically by a single `zfs snapshot` call.

```bash
exordos backup snapshot
```

The snapshot name defaults to `snap-<YYYYmmdd-HHMMSS>`. Use `-s/--snapshot-name` to set it, and `-n/--name` or `--exclude-name/--no` to select domains:

```bash
exordos backup snapshot -s before-upgrade --exclude-name "*github-packer-runner-*"
```

Snapshots are crash-consistent.

### Restore from Snapshots

The `backup snapshot-restore` command rolls back zvol disks of libvirt domains to the given snapshot. It checks that all snapshots exist before changing anything, asks for confirmation (skip with `-y/--yes`), stops running domains, rolls back their disks and starts them again.

```bash
exordos backup snapshot-restore before-upgrade -n o1-a370f746-ecosystem-cp
```

`zfs rollback` refuses to roll back past newer snapshots of the same zvol; destroy them first if needed.

### Export Full and Incremental Backups

Create a snapshot, then export one ZFS stream per selected VM zvol:

```bash
exordos backup snapshot -n vm1 -s baseline
exordos backup snapshot-export baseline -n vm1 -d /backups
exordos backup snapshot -n vm1 -s next
exordos backup snapshot-export next -n vm1 --base-snapshot baseline -d /backups
```

Without `--base-snapshot`, the export uses `zfs send` for a full backup.
With it, the export uses `zfs send -i` for changes since the base snapshot.
Both snapshots must exist on every selected disk, and the base must precede
the target. The command validates all sends before exporting any disk.

Files are named `<encoded-dataset>@<snapshot>.zfs`, or
`<encoded-dataset>@<snapshot>--from-<base>.zfs` for incremental exports.
Dataset slashes are encoded as `%2F`. Existing local files are never overwritten,
and failed sends leave no partial stream file. Completed disk exports remain
if a later disk fails; multi-disk exports are not atomic.

Receive the full stream first, then each incremental stream in chain order:

```bash
sudo zfs receive backup/vm1-disk < '/backups/rpool%2Fdisks%2Fa@baseline.zfs'
sudo zfs receive backup/vm1-disk < '/backups/rpool%2Fdisks%2Fa@next--from-baseline.zfs'
```

The receiving dataset must be at the incremental stream's base snapshot.
Keep the full export and every increment needed to reconstruct the target.
These streams contain disk data; preserve the VM's libvirt XML separately.
Exports retain the crash consistency of the source snapshots.

### Export Snapshots to S3

Use `--s3-config` with the existing S3 backup driver configuration:

```yaml
driver:
  S3QcowBackuper:
    endpoint_url: https://s3.example.com
    access_key: YOUR_ACCESS_KEY
    secret_key: YOUR_SECRET_KEY
    host: hypervisor1
    bucket_name: vm-backups
    region: us-east-1
```

Create the bucket before exporting. Protect the configuration file because it
contains credentials. Set `--s3-prefix` to distinguish hosts or backup chains;
its default is `snapshots`. The driver's `host` setting is not added to the
export prefix automatically.

```bash
# Full export to S3 only
exordos backup snapshot-export baseline -n vm1 \
  --s3-config /path/to/s3.yaml --s3-prefix hypervisor1/vm1

# Incremental export to S3, retaining a local copy
exordos backup snapshot-export next -n vm1 --base-snapshot baseline \
  --s3-config /path/to/s3.yaml --s3-prefix hypervisor1/vm1 -d /backups
```

Each completed disk stream is uploaded under `<prefix>/<export-filename>`.
S3-only exports temporarily spool one disk stream to the system temporary
directory, so it needs enough free space for that stream. With `--backup-dir`,
that directory holds the temporary stream and the completed local copy.
Temporary files are removed on success or failure; local copies remain if an
upload fails. Uploads reuse the S3 client's retries, multipart support, and
object size verification. Existing S3 keys are replaced on repeated exports.
If a later disk fails, earlier completed uploads remain.

To restore, download each full and incremental stream from S3 and receive them
in chain order as described above.
