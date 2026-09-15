
# exordos_network_ports_update

Update a port's groups and toggles

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network ports update [OPTIONS] PORT                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```

## Options

* `port` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `port`

* `port_security`:
    * Type: boolean
    * Default: `none`
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network ports update [OPTIONS] PORT                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```
