
# exordos_network_nfs_set

Change what a network function answers with

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network nfs set [OPTIONS] NF                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `nf` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `nf`

* `rule_specs`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--rule`

  splitter: the allow-list, as <ingress|egress>:<tcp|udp|icmp|any>[:<port>][@<remote_cidr>|@<identity-group-uuid>] (repeatable; replaces the whole list)

* `forwarders`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--forwarder`

  dns: an upstream resolver of this network (repeatable, replaces)

* `zone_suffix`:
    * Type: text
    * Default: `none`
    * Usage: `--zone-suffix`

  dns: the internal zone's suffix

* `platform_names`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--platform-name`

  dns: a name of the installation itself (repeatable, replaces)

* `filename`:
    * Type: text
    * Default: `none`
    * Usage: `--filename`

  dhcp: the netboot script to chain to

* `lease_seconds`:
    * Type: integer
    * Default: `none`
    * Usage: `--lease-seconds`

  dhcp: how long a lease is held

* `address`:
    * Type: text
    * Default: `none`
    * Usage: `-a
--address`

  fip: the address object (UUID) or a literal IP

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network nfs set [OPTIONS] NF                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```
