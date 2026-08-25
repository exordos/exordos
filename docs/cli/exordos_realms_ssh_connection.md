
# exordos_realms_ssh_connection

Show realm ssh connection info

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos realms ssh_connection [OPTIONS] NAME_UUID                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
```

## Options

* `name_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `name_uuid`

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos realms ssh_connection [OPTIONS] NAME_UUID                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Show realm ssh connection info                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output  -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                              │
│ --help                                Show this message and exit.                                                                                                                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
