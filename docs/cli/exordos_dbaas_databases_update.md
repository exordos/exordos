
# exordos_dbaas_databases_update

Update database

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dbaas databases update [OPTIONS] UUID                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `instance_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--instance-uuid`

  UUID of the instance the database belongs to

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the database

* `description`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--description`

  Description of the database

* `owner`:
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dbaas databases update [OPTIONS] UUID                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
 Update database                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --instance-uuid  -i  TEXT  UUID of the instance the database belongs to [required]                                                                                                                                                                                                                   │
│    --name           -n  TEXT  Name of the database                                                                                                                                                                                                                                                      │
│    --description        TEXT  Description of the database                                                                                                                                                                                                                                               │
│    --owner              TEXT  UUID or name of the user owning the database                                                                                                                                                                                                                              │
│    --help                     Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
