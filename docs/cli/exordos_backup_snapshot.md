
# exordos_backup_snapshot

Create ZFS snapshots of libvirt domain disks

## Usage

```console

 Usage: exordos backup snapshot [OPTIONS]

```

## Options

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the libvirt domain, if not provided, all will be snapshotted

* `exclude_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--no
--exclude-name`

  Name or pattern of libvirt domains to exclude from snapshot

* `snapshot_name`:
    * Type: text
    * Default: `none`
    * Usage: `-s
--snapshot-name`

  Snapshot name. Defaults to snap-<YYYYmmdd-HHMMSS>

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos backup snapshot [OPTIONS]

 Create ZFS snapshots of libvirt domain disks

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --name               -n  TEXT  Name of the libvirt domain, if not provided,  │
│                                all will be snapshotted                       │
│ --no,--exclude-name      TEXT  Name or pattern of libvirt domains to exclude │
│                                from snapshot                                 │
│ --snapshot-name      -s  TEXT  Snapshot name. Defaults to                    │
│                                snap-<YYYYmmdd-HHMMSS>                        │
│ --help                         Show this message and exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```
