# exordos_snapshot-restore

Restore libvirt domain disks from ZFS snapshots

## Usage

```console
                                                                                
 Usage: exordos snapshot-restore [OPTIONS] SNAPSHOT_NAME                        
                                                                                
```

## Options

* `snapshot_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `snapshot_name`

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the libvirt domain, if not provided, all will be restored

* `exclude_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--no
--exclude-name`

  Name or pattern of libvirt domains to exclude from restore

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
                                                                                
 Usage: exordos snapshot-restore [OPTIONS] SNAPSHOT_NAME                        
                                                                                
 Restore libvirt domain disks from ZFS snapshots                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --name               -n  TEXT  Name of the libvirt domain, if not provided,  │
│                                all will be restored                          │
│ --no,--exclude-name      TEXT  Name or pattern of libvirt domains to exclude │
│                                from restore                                  │
│ --yes                -y        Do not ask for confirmation                   │
│ --help                         Show this message and exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```
