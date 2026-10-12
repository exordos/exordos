
# exordos_backup_snapshot-export

Export VM ZFS snapshots as backup streams

## Usage

```console

 Usage: exordos backup snapshot-export [OPTIONS] SNAPSHOT_NAME

```

## Options

* `snapshot_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `snapshot_name`

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Domain to export; defaults to all

* `exclude_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--no
--exclude-name`

  Domain name or pattern to exclude

* `backup_dir`:
    * Type: directory
    * Default: `none`
    * Usage: `-d
--backup-dir`

  Directory for ZFS stream files; required unless --s3-config is provided

* `s3_config`:
    * Type: file
    * Default: `none`
    * Usage: `--s3-config`

  S3QcowBackuper configuration for uploading exports to S3

* `s3_prefix`:
    * Type: text
    * Default: `snapshots`
    * Usage: `--s3-prefix`

  S3 object key prefix

* `base_snapshot`:
    * Type: text
    * Default: `none`
    * Usage: `--base-snapshot`

  Earlier snapshot name for an incremental export; omit for a full export

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos backup snapshot-export [OPTIONS] SNAPSHOT_NAME

 Export VM ZFS snapshots as backup streams

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --name               -n  TEXT       Domain to export; defaults to all        │
│ --no,--exclude-name      TEXT       Domain name or pattern to exclude        │
│ --backup-dir         -d  DIRECTORY  Directory for ZFS stream files; required │
│                                     unless --s3-config is provided           │
│ --s3-config              FILE       S3QcowBackuper configuration for         │
│                                     uploading exports to S3                  │
│ --s3-prefix              TEXT       S3 object key prefix [default:           │
│                                     snapshots]                               │
│ --base-snapshot          TEXT       Earlier snapshot name for an incremental │
│                                     export; omit for a full export           │
│ --help                              Show this message and exit.              │
╰──────────────────────────────────────────────────────────────────────────────╯
```
