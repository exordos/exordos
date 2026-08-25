
# exordos_dns_records_add

Add a new record

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dns records add [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the record

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to deploy the record

* `record_type` (REQUIRED):
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `--record-type`

* `ttl`:
    * Type: integer
    * Default: `3600`
    * Usage: `--ttl`

* `prio`:
    * Type: integer
    * Default: `none`
    * Usage: `--prio`

* `disabled`:
    * Type: boolean
    * Default: `false`
    * Usage: `--disabled`

* `record`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--record`

* `domain_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--domain-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dns records add [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Add a new record                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID            UUID of the record                                                                                                                                                                                                                                                │
│ *  --project-id   -p  UUID            UUID of the project in which to deploy the record [required]                                                                                                                                                                                                      │
│ *  --record-type      [a|ns|soa|txt]  [required]                                                                                                                                                                                                                                                        │
│    --ttl              INTEGER                                                                                                                                                                                                                                                                           │
│    --prio             INTEGER                                                                                                                                                                                                                                                                           │
│    --disabled                                                                                                                                                                                                                                                                                           │
│    --record           TEXT                                                                                                                                                                                                                                                                              │
│ *  --domain-uuid  -d  TEXT            [required]                                                                                                                                                                                                                                                        │
│    --help                             Show this message and exit.                                                                                                                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
