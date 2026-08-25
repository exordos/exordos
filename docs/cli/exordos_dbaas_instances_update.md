
# exordos_dbaas_instances_update

Update instance

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dbaas instances update [OPTIONS] UUID                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the instance

* `description`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--description`

  Description of the instance

* `cpu`:
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--cpu`

  Number of CPU cores per node

* `ram`:
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--ram`

  RAM per node in MB

* `disk_size`:
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--disk-size`

  Disk size per node in GB, shrink is not supported

* `nodes_number`:
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--nodes-number`

  Number of nodes in the cluster

* `sync_replica_number`:
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--sync-replica-number`

  Number of synchronous replicas

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dbaas instances update [OPTIONS] UUID                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
 Update instance                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name                 -n  TEXT                                Name of the instance                                                                                                                                                                                                                     │
│ --description              TEXT                                Description of the instance                                                                                                                                                                                                              │
│ --cpu                      INTEGER RANGE [1<=x<=128]           Number of CPU cores per node                                                                                                                                                                                                             │
│ --ram                      INTEGER RANGE [512<=x<=1073741824]  RAM per node in MB                                                                                                                                                                                                                       │
│ --disk-size                INTEGER RANGE [8<=x<=1073741824]    Disk size per node in GB, shrink is not supported                                                                                                                                                                                        │
│ --nodes-number             INTEGER RANGE [1<=x<=16]            Number of nodes in the cluster                                                                                                                                                                                                           │
│ --sync-replica-number      INTEGER RANGE [0<=x<=15]            Number of synchronous replicas                                                                                                                                                                                                           │
│ --help                                                         Show this message and exit.                                                                                                                                                                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
