
# exordos_repo_elements_list

List repo elements

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo elements list [OPTIONS]                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
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

  Watch the list of repo elements

* `interval`:
    * Type: float range
    * Default: `0.5`
    * Usage: `--interval`

  Refresh interval in seconds.

* `dev`:
    * Type: boolean
    * Default: `false`
    * Usage: `--dev`

  Show all versions including dev

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo elements list [OPTIONS]                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 List repo elements                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --filters   -f  TEXT                    Additional filters to pass to the api. The format is 'key=value'. For example: --f parent=11111111-1111-1111-1111-11111111111 --filters status=NEW                                                                                                              │
│ --fields        TEXT                    fields to show, defaults to all, for example: --fields name --fields status                                                                                                                                                                                     │
│ --output    -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                            │
│ --watch     -w                          Watch the list of repo elements                                                                                                                                                                                                                                 │
│ --interval      FLOAT RANGE [x>=0.1]    Refresh interval in seconds.                                                                                                                                                                                                                                    │
│ --dev                                   Show all versions including dev                                                                                                                                                                                                                                 │
│ --help                                  Show this message and exit.                                                                                                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
