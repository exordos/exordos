
# exordos_secret_ssh_keys_show

Show ssh_key

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos secret ssh_keys show [OPTIONS] UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
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

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos secret ssh_keys show [OPTIONS] UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
 Show ssh_key                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output  -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                              │
│ --help                                Show this message and exit.                                                                                                                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
