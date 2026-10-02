
# exordos_network_vhosts_update

Update vhost

## Usage

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network vhosts update [OPTIONS] UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                            
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `lb_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--lb-uuid`

  Load balancer UUID

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the vhost

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description

* `port`:
    * Type: integer range
    * Default: `none`
    * Usage: `--port`

* `domains`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--domain`

  Domain served by the vhost, replaces the current list, may be repeated

* `cert`:
    * Type: filename
    * Default: `none`
    * Usage: `--cert`

  PEM certificate file

* `key`:
    * Type: filename
    * Default: `none`
    * Usage: `--key`

  PEM private key file

* `proxy_protocol_from`:
    * Type: text
    * Default: `none`
    * Usage: `--proxy-protocol-from`

  CIDR allowed to send PROXY protocol headers, e.g. 10.0.0.1/32

* `enabled`:
    * Type: boolean
    * Default: `none`
    * Usage: `--enabled`

  Enable or disable the vhost

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network vhosts update [OPTIONS] UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                            
 Update vhost                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --lb-uuid                  UUID                          Load balancer UUID [required]                                                                                                                                                                                                                │
│    --name                 -n  TEXT                          Name of the vhost                                                                                                                                                                                                                            │
│    --description          -D  TEXT                          Description                                                                                                                                                                                                                                  │
│    --port                     INTEGER RANGE [80<=x<=65535]                                                                                                                                                                                                                                               │
│    --domain                   TEXT                          Domain served by the vhost, replaces the current list, may be repeated                                                                                                                                                                       │
│    --cert                     FILENAME                      PEM certificate file                                                                                                                                                                                                                         │
│    --key                      FILENAME                      PEM private key file                                                                                                                                                                                                                         │
│    --proxy-protocol-from      TEXT                          CIDR allowed to send PROXY protocol headers, e.g. 10.0.0.1/32                                                                                                                                                                                │
│    --enabled/--disabled                                     Enable or disable the vhost                                                                                                                                                                                                                  │
│    --help                                                   Show this message and exit.                                                                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
