
# exordos_network_ports_add

Add a port (a NIC on a subnet) to a node

## Usage

```console

 Usage: exordos network ports add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the port

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name (also its DNS name)

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

* `subnet` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-s
--subnet`

  Subnet (UUID or name)

* `node` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-N
--node`

  Node (UUID or name)

* `port_security`:
    * Type: boolean
    * Default: `true`
    * Usage: `--port-security`

  Allow only the port's own source MAC/IP

* `target_mac`:
    * Type: text
    * Default: `none`
    * Usage: `--mac`

  Requested MAC address

* `target_ipv4`:
    * Type: text
    * Default: `none`
    * Usage: `--ipv4`

  Requested IPv4 address

* `dhcp`:
    * Type: boolean
    * Default: `none`
    * Usage: `--dhcp`

  Override subnet DHCP

* `dns`:
    * Type: boolean
    * Default: `none`
    * Usage: `--dns`

  Serve host-local DNS

* `network_identity`:
    * Type: boolean
    * Default: `none`
    * Usage: `--network-identity`

  Belong to the network's default identity group

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos network ports add [OPTIONS]

```
