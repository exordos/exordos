
# hypervisors_update

Update hypervisor

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute hypervisors update [OPTIONS] UUID                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the hypervisor

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the hypervisor

* `avail_cores`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--avail_cores`

* `avail_ram`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--avail_ram`

* `cores_ratio`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--cores_ratio`

* `ram_ratio`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--ram_ratio`

* `machine_type`:
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `-m
--machine_type`

* `driver_spec`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--driver_spec`

  Additional filters to pass to the api. The format is 'key=value'. For example: -d a=b -d c=d --driver_spec e=f

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute hypervisors update [OPTIONS] UUID                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Update hypervisor                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name          -n  TEXT     Name of the hypervisor                                                                                                                                                                                                                                                     │
│ --description   -D  TEXT     Description of the hypervisor                                                                                                                                                                                                                                              │
│ --avail_cores       INTEGER                                                                                                                                                                                                                                                                             │
│ --avail_ram         INTEGER                                                                                                                                                                                                                                                                             │
│ --cores_ratio       FLOAT                                                                                                                                                                                                                                                                               │
│ --ram_ratio         FLOAT                                                                                                                                                                                                                                                                               │
│ --machine_type  -m  [vm|hw]                                                                                                                                                                                                                                                                             │
│ --driver_spec   -d  TEXT     Additional filters to pass to the api. The format is 'key=value'. For example: -d a=b -d c=d --driver_spec e=f                                                                                                                                                             │
│ --help                       Show this message and exit.                                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
