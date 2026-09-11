
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

  Driver specification key/value pairs, e.g. --driver-spec kind=rawstor --driver-spec location=file:///var/lib/rawstor --driver-spec endpoint=ost://10.0.0.5:7777 --driver-spec speed=HOT --driver-spec ephemeral=false


* `storage_pools`: 
  * Type: text 
  * Default: `none`
  * Usage: `--storage-pools`

  Storage pools as a JSON list, for a cluster with more than the single "default" pool `storages init` creates, e.g. '[{"name": "default", "speed": "HOT", "ephemeral": false, "capacity_usable": 100}]'


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
│ --uuid           -u  UUID  UUID of the storage cluster                       │
│ --name           -n  TEXT  Name of the storage cluster                       │
│ --description    -D  TEXT  Description of the storage cluster                │
│ --driver-spec        TEXT  Driver specification key/value pairs, e.g.        │
│                            --driver-spec kind=rawstor --driver-spec          │
│                            location=file:///var/lib/rawstor --driver-spec    │
│                            endpoint=ost://10.0.0.5:7777 --driver-spec        │
│                            speed=HOT --driver-spec ephemeral=false           │
│ --storage-pools      TEXT  Storage pools as a JSON list, for a cluster with  │
│                            more than the single "default" pool `storages     │
│                            init` creates, e.g. '[{"name": "default",         │
│                            "speed": "HOT", "ephemeral": false,               │
│                            "capacity_usable": 100}]'                         │
│ --help                     Show this message and exit.                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

