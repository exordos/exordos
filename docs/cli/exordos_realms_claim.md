
# exordos_realms_claim

Claim a warm realm from the pool

## Usage

```console

 Usage: exordos realms claim [OPTIONS]

```

## Options

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name to give the claimed realm

* `description`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--description`

* `node_cores`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--node-cores`

  CPU cores of the realm to claim

* `node_ram`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--node-ram`

  RAM in MB of the realm to claim

* `node_root_disk_size`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--node-root-disk-size`

  Root disk size in GB of the realm to claim

* `ttl_hours`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--ttl-hours`

  Delete the realm automatically this many hours from now

* `ssh_public_key`:
    * Type: file
    * Default: `sentinel.unset`
    * Usage: `--ssh-public-key`

  Path to the ssh public key

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  the output format, defaults to table

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos realms claim [OPTIONS]

 Claim a warm realm from the pool

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --name                 -n  TEXT                    Name to give the claimed realm [required]                                                                                                                                                                                                          │
│    --description              TEXT                                                                                                                                                                                                                                                                       │
│    --node-cores               INTEGER                 CPU cores of the realm to claim                                                                                                                                                                                                                    │
│    --node-ram                 INTEGER                 RAM in MB of the realm to claim                                                                                                                                                                                                                    │
│    --node-root-disk-size      INTEGER                 Root disk size in GB of the realm to claim                                                                                                                                                                                                         │
│    --ttl-hours                FLOAT                   Delete the realm automatically this many hours from now                                                                                                                                                                                            │
│    --ssh-public-key           FILE                    Path to the ssh public key                                                                                                                                                                                                                         │
│    --output               -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                               │
│    --help                                             Show this message and exit.                                                                                                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
