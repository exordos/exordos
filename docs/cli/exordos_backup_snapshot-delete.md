
# exordos_backup_snapshot-delete

Delete ZFS snapshots on the local hypervisor

## Usage

```console

 Usage: exordos backup snapshot-delete [OPTIONS] [SNAPSHOTS]...

```

## Options

* `snapshots`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `snapshots`

* `delete_all`:
    * Type: boolean
    * Default: `false`
    * Usage: `--all`

  Delete all ZFS snapshots

* `yes`:
    * Type: boolean
    * Default: `false`
    * Usage: `-y
--yes`

  Do not ask for confirmation

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos backup snapshot-delete [OPTIONS] [SNAPSHOTS]...

 Delete ZFS snapshots on the local hypervisor

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --all       Delete all ZFS snapshots                                         │
│ --yes   -y  Do not ask for confirmation                                      │
│ --help      Show this message and exit.                                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
