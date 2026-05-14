
# imports_show

Show import

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos em imports show [OPTIONS] NAME_UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```

## Options

* `element`:
    * Type: text
    * Default: `none`
    * Usage: `-e
--element`

  Name or uuid of the element

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos em imports show [OPTIONS] NAME_UUID                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
 Show import                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --element  -e  TEXT                    Name or uuid of the element                                                                                                                                                                                                                                      │
│ --output   -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                             │
│ --help                                 Show this message and exit.                                                                                                                                                                                                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
