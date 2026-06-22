
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

* `vhost_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--vhost-uuid`

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes show [OPTIONS] UUID                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
 Show route                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output      -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                       │
│ *  --vhost-uuid      UUID                    [required]                                                                                                                                                                                                                                                 │
│ *  --lb-uuid         UUID                    [required]                                                                                                                                                                                                                                                 │
│    --help                                    Show this message and exit.                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
