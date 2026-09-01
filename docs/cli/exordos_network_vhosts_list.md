
# exordos_network_vhosts_list

List vhosts

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network vhosts list [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `filters`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-f
--filters`

  Additional filters to pass to the api. The format is 'key=value'. For example: --f parent=11111111-1111-1111-1111-11111111111 --filters status=NEW

* `fields`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--fields`

  fields to show, defaults to all, for example: --fields name --fields status

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

  Watch the list of vhosts

* `interval`:
    * Type: float range
    * Default: `0.5`
    * Usage: `--interval`

  Refresh interval in seconds.

* `lb_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--lb-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network vhosts list [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 List vhosts                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --filters   -f  TEXT                    Additional filters to pass to the api. The format is 'key=value'. For example: --f parent=11111111-1111-1111-1111-11111111111 --filters status=NEW                                                                                                           │
│    --fields        TEXT                    fields to show, defaults to all, for example: --fields name --fields status                                                                                                                                                                                  │
│    --output    -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                         │
│    --watch     -w                          Watch the list of vhosts                                                                                                                                                                                                                                     │
│    --interval      FLOAT RANGE [x>=0.1]    Refresh interval in seconds.                                                                                                                                                                                                                                 │
│ *  --lb-uuid       UUID                    [required]                                                                                                                                                                                                                                                   │
│    --help                                  Show this message and exit.                                                                                                                                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
