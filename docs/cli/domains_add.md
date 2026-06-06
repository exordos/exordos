
# domains_add

Add a new domain

## Usage

```console
                                                                                                                                                               
 Usage: exordos dns domains add [OPTIONS]                                                                                                                      
                                                                                                                                                               
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the domain

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the domain

* `name`:
    * Type: text
    * Default: `example_domain`
    * Usage: `-n
--name`

  Name of the domain

* `sync_to_ecosystem`:
    * Type: boolean
    * Default: `false`
    * Usage: `-s
--sync-to-ecosystem`

  Sync the domain to the ecosystem

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                               
 Usage: exordos dns domains add [OPTIONS]                                                                                                                      
                                                                                                                                                               
 Add a new domain                                                                                                                                              
                                                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid               -u  UUID  UUID of the domain                                                                                                        │
│ *  --project-id         -p  UUID  Name of the project in which to deploy the domain [required]                                                              │
│    --name               -n  TEXT  Name of the domain                                                                                                        │
│    --sync-to-ecosystem  -s        Sync the domain to the ecosystem                                                                                          │
│    --help                         Show this message and exit.                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
