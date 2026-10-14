
# exordos_vs_values_update

Update value

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos vs values update [OPTIONS] UUID                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the value

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the value

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the value

* `value`:
    * Type: text
    * Default: `none`
    * Usage: `-V
--value`

  value

* `variable`:
    * Type: text
    * Default: `none`
    * Usage: `-v
--variable`

  uuid of the variable

* `clear_tags`:
    * Type: boolean
    * Default: `false`
    * Usage: `--clear-tags`

  Remove all tags.

* `tags`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--tag`

  Set the complete tag list. Repeat for each tag.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos vs values update [OPTIONS] UUID                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
 Update value                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID  Name of the project in which to deploy the value                                                                                                                                                                                                                               │
│ --name         -n  TEXT  Name of the value                                                                                                                                                                                                                                                              │
│ --description  -D  TEXT  Description of the value                                                                                                                                                                                                                                                       │
│ --value        -V  TEXT  value                                                                                                                                                                                                                                                                          │
│ --variable     -v  TEXT  uuid of the variable                                                                                                                                                                                                                                                           │
│ --clear-tags  Remove all tags.                                                                                                                                                                                                                                                                          │
│ --tag  TEXT  Set the complete tag list. Repeat for each tag.                                                                                                                                                                                                                                            │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
