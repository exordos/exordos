
# exordos_network_subnets_add

Add a new subnet to a network

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network subnets add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the subnet

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the subnet

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

* `network` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-N
--network`

  Network the subnet belongs to (UUID or name)

* `cidr` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-c
--cidr`

  CIDR, e.g. 10.100.0.0/24

* `dhcp`:
    * Type: boolean
    * Default: `true`
    * Usage: `--dhcp`

  Serve the guests of this subnet from the host-local DHCP responder

* `ip_range`:
    * Type: text
    * Default: `none`
    * Usage: `--ip-range`

  Allocation range <first>-<last>, e.g. 10.100.0.20-10.100.0.200

* `router_specs`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--router`

  Route handed out over DHCP: <destination_cidr>=<next_hop>

* `dns_servers`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-s
--dns-server`

  Resolver handed out over DHCP (repeatable)

* `pool_only`:
    * Type: boolean
    * Default: `false`
    * Usage: `--pool-only`

  Hand out addresses only — never place nodes in this subnet

* `shared_pool`:
    * Type: boolean
    * Default: `false`
    * Usage: `--shared-pool`

  Let projects that do not own this subnet take addresses out of it — what an ingress pool of floating addresses is for. Narrower than publishing the whole network, which opens every subnet of it

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network subnets add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```
