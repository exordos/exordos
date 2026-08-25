
# exordos_dbaas_databases_add

Add a new database

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dbaas databases add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the database

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to create the database

* `instance_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--instance-uuid`

  UUID of the instance to create the database in

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the database

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `--description`

  Description of the database

* `owner` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--owner`

  UUID or name of the user owning the database

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dbaas databases add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 Add a new database                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid           -u  UUID  UUID of the database                                                                                                                                                                                                                                                      │
│ *  --project-id     -p  UUID  UUID of the project in which to create the database [required]                                                                                                                                                                                                            │
│ *  --instance-uuid  -i  TEXT  UUID of the instance to create the database in [required]                                                                                                                                                                                                                 │
│ *  --name           -n  TEXT  Name of the database [required]                                                                                                                                                                                                                                           │
│    --description        TEXT  Description of the database                                                                                                                                                                                                                                               │
│ *  --owner              TEXT  UUID or name of the user owning the database [required]                                                                                                                                                                                                                   │
│    --help                     Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
