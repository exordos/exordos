
# exordos_network_vhosts_show

Show vhost

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network vhosts show [OPTIONS] UUID                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network vhosts show [OPTIONS] UUID                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
 Show vhost                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output   -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                          │
│ *  --lb-uuid      UUID                    [required]                                                                                                                                                                                                                                                    │
│    --help                                 Show this message and exit.                                                                                                                                                                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
