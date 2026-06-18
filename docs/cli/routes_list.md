
# routes_list

List routes

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes list [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
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

  Watch the list of routes

* `interval`:
    * Type: float range
    * Default: `0.5`
    * Usage: `--interval`

  Refresh interval in seconds.

* `lb_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--lb-uuid`

* `vhost_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--vhost-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes list [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 List routes                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --filters     -f  TEXT                    Additional filters to pass to the api. The format is 'key=value'. For example: --f parent=11111111-1111-1111-1111-11111111111 --filters status=NEW                                                                                                         │
│    --output      -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                       │
│    --watch       -w                          Watch the list of routes                                                                                                                                                                                                                                   │
│    --interval        FLOAT RANGE [x>=0.1]    Refresh interval in seconds.                                                                                                                                                                                                                               │
│ *  --lb-uuid     -d  TEXT                    [required]                                                                                                                                                                                                                                                 │
│ *  --vhost-uuid  -v  TEXT                    [required]                                                                                                                                                                                                                                                 │
│    --help                                    Show this message and exit.                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
