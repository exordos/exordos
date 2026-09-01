
# exordos_limits_update

Update limit

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos limits update [OPTIONS] UUID                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  Uuid of the project

* `resource_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--resource-name`

  Resource name of the limit

* `limit`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `-l
--limit`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos limits update [OPTIONS] UUID                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 Update limit                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --project-id     -p  UUID     Uuid of the project                                                                                                                                                                                                                                                       │
│ --resource-name  -r  TEXT     Resource name of the limit                                                                                                                                                                                                                                                │
│ --limit          -l  INTEGER                                                                                                                                                                                                                                                                            │
│ --help                        Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
