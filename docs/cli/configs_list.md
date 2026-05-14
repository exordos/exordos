
# configs_list

List configs

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos configs list [OPTIONS]                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
```

## Options

* `node`:
    * Type: uuid
    * Default: `none`
    * Usage: `-n
--node`

  Filter configs by node

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  the output format, defaults to table

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos configs list [OPTIONS]                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
 List configs                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --node    -n  UUID                    Filter configs by node                                                                                                                                                                                                                                            │
│ --output  -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                              │
│ --help                                Show this message and exit.                                                                                                                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
