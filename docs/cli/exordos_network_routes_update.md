
# exordos_network_routes_update

Update route. Passing --condition or --pool replaces the whole route condition

## Usage

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network routes update [OPTIONS] UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                            
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

* `vhost_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--vhost-uuid`

  Vhost UUID

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the route

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description

* `enabled`:
    * Type: boolean
    * Default: `none`
    * Usage: `--enabled`

  Enable or disable the route

* `condition`:
    * Type: text
    * Default: `none`
    * Usage: `--condition`

  Full condition as a JSON string, other condition options are ignored

* `kind`:
    * Type: choice
    * Default: `prefix`
    * Usage: `--kind`

  Condition kind, 'raw' is for tcp/udp vhosts

* `value`:
    * Type: text
    * Default: `/`
    * Usage: `--value`

  Path to match (ignored for 'raw' kind)

* `pool`:
    * Type: uuid
    * Default: `none`
    * Usage: `--pool`

  Backend pool UUID

* `backend_protocol`:
    * Type: choice
    * Default: `http`
    * Usage: `--backend-protocol`

  Protocol used to reach the backend pool

* `allowed_ips`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--allowed-ip`

  CIDR allowed to access the route, may be repeated

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network routes update [OPTIONS] UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                            
 Update route. Passing --condition or --pool replaces the whole route condition                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --lb-uuid                 UUID                      Load balancer UUID [required]                                                                                                                                                                                                                     │
│ *  --vhost-uuid              UUID                      Vhost UUID [required]                                                                                                                                                                                                                             │
│    --name                -n  TEXT                      Name of the route                                                                                                                                                                                                                                 │
│    --description         -D  TEXT                      Description                                                                                                                                                                                                                                       │
│    --enabled/--disabled                                Enable or disable the route                                                                                                                                                                                                                       │
│    --condition               TEXT                      Full condition as a JSON string, other condition options are ignored                                                                                                                                                                              │
│    --kind                    [prefix|exact|regex|raw]  Condition kind, 'raw' is for tcp/udp vhosts [default: prefix]                                                                                                                                                                                     │
│    --value                   TEXT                      Path to match (ignored for 'raw' kind) [default: /]                                                                                                                                                                                               │
│    --pool                    UUID                      Backend pool UUID                                                                                                                                                                                                                                 │
│    --backend-protocol        [http|https]              Protocol used to reach the backend pool [default: http]                                                                                                                                                                                           │
│    --allowed-ip              TEXT                      CIDR allowed to access the route, may be repeated                                                                                                                                                                                                 │
│    --help                                              Show this message and exit.                                                                                                                                                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
