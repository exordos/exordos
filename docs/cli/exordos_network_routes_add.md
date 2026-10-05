
# exordos_network_routes_add

Add a new route

## Usage

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network routes add [OPTIONS]                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                            
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the route

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

* `vhost_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--vhost-uuid`

  Vhost UUID

* `name`:
    * Type: text
    * Default: ``
    * Usage: `-n
--name`

  Name of the route

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description

* `disabled`:
    * Type: boolean
    * Default: `false`
    * Usage: `--disabled`

  Create disabled route

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
                                                                                                                                                                                                                                                                                                            
 Usage: exordos network routes add [OPTIONS]                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                            
 Add a new route                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid              -u  UUID                      UUID of the route                                                                                                                                                                                                                                   │
│ *  --project-id        -p  UUID                      Project UUID [required]                                                                                                                                                                                                                             │
│ *  --lb-uuid               UUID                      Load balancer UUID [required]                                                                                                                                                                                                                       │
│ *  --vhost-uuid            UUID                      Vhost UUID [required]                                                                                                                                                                                                                               │
│    --name              -n  TEXT                      Name of the route                                                                                                                                                                                                                                   │
│    --description       -D  TEXT                      Description                                                                                                                                                                                                                                         │
│    --disabled                                        Create disabled route                                                                                                                                                                                                                               │
│    --condition             TEXT                      Full condition as a JSON string, other condition options are ignored                                                                                                                                                                                │
│    --kind                  [prefix|exact|regex|raw]  Condition kind, 'raw' is for tcp/udp vhosts [default: prefix]                                                                                                                                                                                       │
│    --value                 TEXT                      Path to match (ignored for 'raw' kind) [default: /]                                                                                                                                                                                                 │
│    --pool                  UUID                      Backend pool UUID                                                                                                                                                                                                                                   │
│    --backend-protocol      [http|https]              Protocol used to reach the backend pool [default: http]                                                                                                                                                                                             │
│    --allowed-ip            TEXT                      CIDR allowed to access the route, may be repeated                                                                                                                                                                                                   │
│    --help                                            Show this message and exit.                                                                                                                                                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
