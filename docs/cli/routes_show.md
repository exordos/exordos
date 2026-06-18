
# routes_show

Show route

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes show [OPTIONS] UUID                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  the output format, defaults to table

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes show [OPTIONS] UUID                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
 Show route                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output      -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                       │
│ *  --lb-uuid     -d  TEXT                    [required]                                                                                                                                                                                                                                                 │
│ *  --vhost-uuid  -v  TEXT                    [required]                                                                                                                                                                                                                                                 │
│    --help                                    Show this message and exit.                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
