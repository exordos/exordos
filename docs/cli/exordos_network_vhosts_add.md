
# exordos_network_vhosts_add

Add a new vhost

## Usage

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network vhosts add [OPTIONS]                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                            
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the vhost

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project UUID

* `lb_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--lb-uuid`

  Load balancer UUID

* `name`:
    * Type: text
    * Default: ``
    * Usage: `-n
--name`

  Name of the vhost

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description

* `protocol`:
    * Type: choice
    * Default: `http`
    * Usage: `--protocol`

  Protocol of the vhost

* `port`:
    * Type: integer range
    * Default: `80`
    * Usage: `--port`

* `domains`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--domain`

  Domain served by the vhost (required for http/https), may be repeated

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

* `disabled`:
    * Type: boolean
    * Default: `false`
    * Usage: `--disabled`

  Create disabled vhost

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network vhosts add [OPTIONS]                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                            
 Add a new vhost                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid                 -u  UUID                          UUID of the vhost                                                                                                                                                                                                                            │
│ *  --project-id           -p  UUID                          Project UUID [required]                                                                                                                                                                                                                      │
│ *  --lb-uuid                  UUID                          Load balancer UUID [required]                                                                                                                                                                                                                │
│    --name                 -n  TEXT                          Name of the vhost                                                                                                                                                                                                                            │
│    --description          -D  TEXT                          Description                                                                                                                                                                                                                                  │
│    --protocol                 [http|https|tcp|udp]          Protocol of the vhost [default: http]                                                                                                                                                                                                        │
│    --port                     INTEGER RANGE [80<=x<=65535]  [default: 80]                                                                                                                                                                                                                                │
│    --domain                   TEXT                          Domain served by the vhost (required for http/https), may be repeated                                                                                                                                                                        │
│    --cert                     FILENAME                      PEM certificate file                                                                                                                                                                                                                         │
│    --key                      FILENAME                      PEM private key file                                                                                                                                                                                                                         │
│    --proxy-protocol-from      TEXT                          CIDR allowed to send PROXY protocol headers, e.g. 10.0.0.1/32                                                                                                                                                                                │
│    --disabled                                               Create disabled vhost                                                                                                                                                                                                                        │
│    --help                                                   Show this message and exit.                                                                                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
