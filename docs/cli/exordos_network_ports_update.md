
# exordos_network_ports_update

Update a port's requested addresses and toggles

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


* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos network ports update [OPTIONS] PORT

```
