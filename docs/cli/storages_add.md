
# storages_add

Add a new storage cluster

## Usage

```console
                                                                                
 Usage: exordos storages add [OPTIONS]                                          
                                                                                
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the storage cluster

* `name`:
    * Type: text
    * Default: `storage`
    * Usage: `-n
--name`

  Name of the storage cluster

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the storage cluster

* `driver_spec`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--driver-spec`

  Driver specification key/value pairs, e.g. --driver-spec kind=rawstor --driver-spec location=file:///var/lib/rawstor --driver-spec ost_endpoint=ost://10.0.0.5:7777 --driver-spec speed=HOT --driver-spec ephemeral=false

* `storage_pools`:
    * Type: text
    * Default: `none`
    * Usage: `--storage-pools`

  Storage pools as a JSON list, for a cluster with more than the single "default" pool `storages init` creates, e.g. '[{"kind": "thin_storage_pool", "pool_type": "rawstor", "name": "default", "speed": "HOT", "ephemeral": false, "capacity_usable": 100}]'

* `location`:
    * Type: text
    * Default: `none`
    * Usage: `--location`

  Local OST backing store URI

* `endpoint`:
    * Type: text
    * Default: `none`
    * Usage: `--endpoint`

  Advertised OST URI (ost://host:port)

* `mds_port`:
    * Type: integer range
    * Default: `none`
    * Usage: `--mds-port`

  Core MDS port; first storage defaults to 7776

* `speed`:
    * Type: choice
    * Default: `hot`
    * Usage: `--speed`

* `ephemeral`:
    * Type: boolean
    * Default: `false`
    * Usage: `--ephemeral`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: exordos storages add [OPTIONS]                                          
                                                                                
 Add a new storage cluster                                                      
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --uuid                   -u  UUID                    UUID of the storage     │
│                                                      cluster                 │
│ --name                   -n  TEXT                    Name of the storage     │
│                                                      cluster                 │
│ --description            -D  TEXT                    Description of the      │
│                                                      storage cluster         │
│ --driver-spec                TEXT                    Driver specification    │
│                                                      key/value pairs, e.g.   │
│                                                      --driver-spec           │
│                                                      kind=rawstor            │
│                                                      --driver-spec           │
│                                                      location=file:///var/li │
│                                                      b/rawstor --driver-spec │
│                                                      ost_endpoint=ost://10.0 │
│                                                      .0.5:7777 --driver-spec │
│                                                      speed=HOT --driver-spec │
│                                                      ephemeral=false         │
│ --storage-pools              TEXT                    Storage pools as a JSON │
│                                                      list, for a cluster     │
│                                                      with more than the      │
│                                                      single "default" pool   │
│                                                      `storages init`         │
│                                                      creates, e.g.           │
│                                                      '[{"kind":              │
│                                                      "thin_storage_pool",    │
│                                                      "pool_type": "rawstor", │
│                                                      "name": "default",      │
│                                                      "speed": "HOT",         │
│                                                      "ephemeral": false,     │
│                                                      "capacity_usable":      │
│                                                      100}]'                  │
│ --location                   TEXT                    Local OST backing store │
│                                                      URI                     │
│ --endpoint                   TEXT                    Advertised OST URI      │
│                                                      (ost://host:port)       │
│ --mds-port                   INTEGER RANGE           Core MDS port; first    │
│                              [1<=x<=65535]           storage defaults to     │
│                                                      7776                    │
│ --speed                      [cold|warm|hot]                                 │
│ --ephemeral/--no-epheme                                                      │
│ ral                                                                          │
│ --help                                               Show this message and   │
│                                                      exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```
