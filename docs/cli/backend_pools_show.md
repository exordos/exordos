
# backend_pools_show

Show backend_pool

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network backend_pools show [OPTIONS] UUID                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network backend_pools show [OPTIONS] UUID                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Show backend_pool                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output   -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                          │
│ *  --lb-uuid      UUID                    [required]                                                                                                                                                                                                                                                    │
│    --help                                 Show this message and exit.                                                                                                                                                                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
