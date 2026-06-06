
# records_list

List records

## Usage

```console
                                                                                                                                                               
 Usage: exordos dns records list [OPTIONS]                                                                                                                     
                                                                                                                                                               
```

## Options

* `filters`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-f
--filters`

  Additional filters to pass to the api. The format is 'key=value'. For example: --f parent=11111111-1111-1111-1111-11111111111 --filters status=NEW

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  the output format, defaults to table

* `watch`:
    * Type: boolean
    * Default: `false`
    * Usage: `-w
--watch`

  Watch the list of records

* `interval`:
    * Type: float range
    * Default: `0.5`
    * Usage: `--interval`

  Refresh interval in seconds.

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
                                                                                                                                                               
 Usage: exordos dns records list [OPTIONS]                                                                                                                     
                                                                                                                                                               
 List records                                                                                                                                                  
                                                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --filters      -f  TEXT                    Additional filters to pass to the api. The format is 'key=value'. For example: --f                            │
│                                               parent=11111111-1111-1111-1111-11111111111 --filters status=NEW                                               │
│    --output       -o  [json|html|table|yaml]  the output format, defaults to table                                                                          │
│    --watch        -w                          Watch the list of records                                                                                     │
│    --interval         FLOAT RANGE [x>=0.1]    Refresh interval in seconds.                                                                                  │
│ *  --domain-uuid  -d  TEXT                    [required]                                                                                                    │
│    --help                                     Show this message and exit.                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
