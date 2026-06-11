
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
    * Usage: `--avail-cores`

* `avail_ram`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--avail-ram`

* `cores_ratio`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--cores-ratio`

* `ram_ratio`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--ram-ratio`

* `machine_type`:
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `-m
--machine-type`

* `driver_spec`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--driver-spec`

  Driver Specification. The format is 'key=value'. For example: --driver-spec a=b --driver-spec e=f

* `driver_spec_full`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--driver-spec-full`

  Full Driver Specification. The format is 'key=value'. For example: --driver-spec-full a=b --driver-spec-full e=f

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
│ --name              -n  TEXT     Name of the hypervisor                                                                                                                                                                                                                                                 │
│ --description       -D  TEXT     Description of the hypervisor                                                                                                                                                                                                                                          │
│ --avail-cores           INTEGER                                                                                                                                                                                                                                                                         │
│ --avail-ram             INTEGER                                                                                                                                                                                                                                                                         │
│ --cores-ratio           FLOAT                                                                                                                                                                                                                                                                           │
│ --ram-ratio             FLOAT                                                                                                                                                                                                                                                                           │
│ --machine-type      -m  [vm|hw]                                                                                                                                                                                                                                                                         │
│ --driver-spec           TEXT     Driver Specification. The format is 'key=value'. For example: --driver-spec a=b --driver-spec e=f                                                                                                                                                                      │
│ --driver-spec-full      TEXT     Full Driver Specification. The format is 'key=value'. For example: --driver-spec-full a=b --driver-spec-full e=f                                                                                                                                                       │
│ --help                           Show this message and exit.                                                                                                                                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
