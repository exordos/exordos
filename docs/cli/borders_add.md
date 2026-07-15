
# borders_add

Add a new border (NAT gateway)

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network borders add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the border

* `name`:
    * Type: text
    * Default: `border`
    * Usage: `-n
--name`

  Name of the border

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project UUID

* `node`:
    * Type: uuid
    * Default: `none`
    * Usage: `--node`

  Target compute node (border_node); wins over --kind

* `kind`:
    * Type: choice
    * Default: `core_agent`
    * Usage: `-k
--kind`

  core_agent: the core node's agent; core: a dedicated VM gateway

* `cpu`:
    * Type: integer
    * Default: `1`
    * Usage: `--cpu`

  VM vCPUs (kind=core)

* `ram`:
    * Type: integer
    * Default: `512`
    * Usage: `--ram`

  VM RAM MB (kind=core)

* `disk_size`:
    * Type: integer
    * Default: `10`
    * Usage: `--disk-size`

  VM disk GB (kind=core)

* `snat_specs`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-s
--snat`

  SNAT rule: <source_cidr> (masquerade) or <source_cidr>=<snat_to>

* `forward_specs`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-f
--forward`

  DNAT forward: <tcp|udp>:<listen_port>:<to_host>:<to_port>[@<public_ip>]

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network borders add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```
