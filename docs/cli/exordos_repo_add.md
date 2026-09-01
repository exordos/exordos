
# exordos_repo_add

Add a new repository

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo add [OPTIONS]                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the repository

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to deploy the repository

* `name`:
    * Type: text
    * Default: ``
    * Usage: `-n
--name`

  Name of the repository

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the repository

* `priority`:
    * Type: integer
    * Default: `2048`
    * Usage: `--priority`

  Priority of the repository (0-4096)

* `refresh_rate`:
    * Type: integer
    * Default: `3600`
    * Usage: `--refresh-rate`

  Refresh rate of the repository in seconds

* `sync_mode`:
    * Type: choice
    * Default: `lazy`
    * Usage: `--sync-mode`

  Sync mode of the repository

* `repo_url` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--repo-url`

  URL of the repository. Example: <https://repo.exordos.com/exordos-elements/>

* `repo_user`:
    * Type: text
    * Default: `none`
    * Usage: `--repo-user`

  Username for the repository

* `repo_password`:
    * Type: text
    * Default: `none`
    * Usage: `--repo-password`

  Password for the repository

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo add [OPTIONS]                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
 Add a new repository                                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid           -u  UUID         UUID of the repository                                                                                                                                                                                                                                             │
│ *  --project-id     -p  UUID         UUID of the project in which to deploy the repository [required]                                                                                                                                                                                                   │
│    --name           -n  TEXT         Name of the repository                                                                                                                                                                                                                                             │
│    --description    -D  TEXT         Description of the repository                                                                                                                                                                                                                                      │
│    --priority           INTEGER      Priority of the repository (0-4096)                                                                                                                                                                                                                                │
│    --refresh-rate       INTEGER      Refresh rate of the repository in seconds                                                                                                                                                                                                                          │
│    --sync-mode          [copy|lazy]  Sync mode of the repository                                                                                                                                                                                                                                        │
│ *  --repo-url           TEXT         URL of the repository. Example: https://repo.exordos.com/exordos-elements/ [required]                                                                                                                                                                              │
│    --repo-user          TEXT         Username for the repository                                                                                                                                                                                                                                        │
│    --repo-password      TEXT         Password for the repository                                                                                                                                                                                                                                        │
│    --help                            Show this message and exit.                                                                                                                                                                                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
