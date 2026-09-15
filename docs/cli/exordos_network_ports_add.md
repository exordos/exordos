
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

  Subnet to attach to (UUID or name)

* `node` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-N
--node`

  Node the port belongs to (its machine gets the NIC)

* `mac`:
    * Type: text
    * Default: `none`
    * Usage: `--mac`

  MAC address (generated if omitted)

* `ipv4`:
    * Type: text
    * Default: `none`
    * Usage: `--ipv4`

  Fixed address (allocated from the subnet if omitted)

* `port_security`:
    * Type: boolean
    * Default: `true`
    * Usage: `--port-security`

  Anti-spoofing: only the port's own MAC/IP may be sourced

* `security_groups`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-g
--security-group`

  Security group to apply (UUID or name, repeatable)

* `identity_groups`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--identity-group`

  A group this port belongs to (UUID or name, repeatable); rules elsewhere admit it by that name. Its subnet's default group is always included, so joining one adds access rather than trading the subnet's away.

* `subnet_group`:
    * Type: boolean
    * Default: `none`
    * Usage: `--subnet-group`

  Belong to the subnet's default group as well (the default). --no-subnet-group leaves it: the port is then reachable only where a rule names a group it is actually in.

* `dhcp`:
    * Type: boolean
    * Default: `none`
    * Usage: `--dhcp`

  Override the subnet's DHCP setting for this port

* `dns`:
    * Type: boolean
    * Default: `none`
    * Usage: `--dns`

  Serve this port from the host-local resolver

* `public_address`:
    * Type: text
    * Default: `none`
    * Usage: `--public-address`

  Give the port a floating IP: an existing address object (UUID)

* `floating_from`:
    * Type: text
    * Default: `none`
    * Usage: `--floating-from`

  Give the port a floating IP taken out of this subnet

* `no_public`:
    * Type: boolean
    * Default: `false`
    * Usage: `--no-public`

  Take the port's floating IP away (the address stays allocated)

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network ports add [OPTIONS]                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
```
