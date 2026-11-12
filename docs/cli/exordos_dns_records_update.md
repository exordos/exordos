
# exordos_dns_records_update

Update record

## Usage

```console

 Usage: exordos dns records update [OPTIONS] UUID

```

## Options

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object (an array for bulk creation).

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `record_type`:
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `--record-type`

* `ttl`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--ttl`

* `prio`:
    * Type: integer
    * Default: `sentinel.unset`
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

 Usage: exordos dns records update [OPTIONS] UUID

 Update record

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output       -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                               │
│    --record-type      [a|ns|soa|txt]                                                                                                                                                                                                                                                                     │
│    --ttl              INTEGER                                                                                                                                                                                                                                                                            │
│    --prio             INTEGER                                                                                                                                                                                                                                                                            │
│    --disabled                                                                                                                                                                                                                                                                                            │
│    --record           TEXT                                                                                                                                                                                                                                                                               │
│ *  --domain-uuid  -d  TEXT                    [required]                                                                                                                                                                                                                                                 │
│    --help                                     Show this message and exit.                                                                                                                                                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
