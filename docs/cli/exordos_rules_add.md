
# exordos_rules_add

Add a new rule

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos rules add [OPTIONS]                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the rule

* `project_id`:
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the rule

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the rule

* `operator`:
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `-o
--operator`

* `action`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--action`

* `condition`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--condition`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos rules add [OPTIONS]                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
 Add a new rule                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --uuid         -u  UUID      UUID of the rule                                                                                                                                                                                                                                                           │
│ --project-id   -p  UUID      UUID of the project                                                                                                                                                                                                                                                        │
│ --name         -n  TEXT      Name of the rule                                                                                                                                                                                                                                                           │
│ --description  -D  TEXT      Description of the rule                                                                                                                                                                                                                                                    │
│ --operator     -o  [OR|AND]                                                                                                                                                                                                                                                                             │
│ --action           TEXT                                                                                                                                                                                                                                                                                 │
│ --condition        TEXT                                                                                                                                                                                                                                                                                 │
│ --help                       Show this message and exit.                                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
