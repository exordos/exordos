
# exordos_limits_add

Add a new limit

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos limits add [OPTIONS]                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the limit

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the limit

* `resource_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--resource-name`

  Resource name of the limit

* `field_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-f
--field-name`

  Resource field name of the limit

* `limit` (REQUIRED):
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos limits add [OPTIONS]                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Add a new limit                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid           -u  UUID     UUID of the limit                                                                                                                                                                                                                                                      │
│ *  --project-id     -p  UUID     Name of the project in which to deploy the limit [required]                                                                                                                                                                                                            │
│ *  --resource-name  -r  TEXT     Resource name of the limit [required]                                                                                                                                                                                                                                  │
│    --field-name     -f  TEXT     Resource field name of the limit                                                                                                                                                                                                                                       │
│ *  --limit          -l  INTEGER  [required]                                                                                                                                                                                                                                                             │
│    --help                        Show this message and exit.                                                                                                                                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
