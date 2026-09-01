
# exordos_repo_update

Update repository

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo update [OPTIONS] UUID                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
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

  UUID of the project in which to deploy the repository

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the repository

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the repository

* `status`:
    * Type: choice
    * Default: `none`
    * Usage: `--status`

  Status of the repository

* `priority`:
    * Type: integer
    * Default: `none`
    * Usage: `--priority`

  Priority of the repository (0-4096)

* `refresh_rate`:
    * Type: integer
    * Default: `none`
    * Usage: `--refresh-rate`

  Refresh rate of the repository in seconds

* `sync_mode`:
    * Type: choice
    * Default: `none`
    * Usage: `--sync-mode`

  Sync mode of the repository

* `repo_url`:
    * Type: text
    * Default: `none`
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo update [OPTIONS] UUID                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
 Update repository                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --project-id     -p  UUID                                     UUID of the project in which to deploy the repository                                                                                                                                                                                     │
│ --name           -n  TEXT                                     Name of the repository                                                                                                                                                                                                                    │
│ --description    -D  TEXT                                     Description of the repository                                                                                                                                                                                                             │
│ --status             [NEW|ACTIVE|IN_PROGRESS|DISABLED|ERROR]  Status of the repository                                                                                                                                                                                                                  │
│ --priority           INTEGER                                  Priority of the repository (0-4096)                                                                                                                                                                                                       │
│ --refresh-rate       INTEGER                                  Refresh rate of the repository in seconds                                                                                                                                                                                                 │
│ --sync-mode          [copy|lazy]                              Sync mode of the repository                                                                                                                                                                                                               │
│ --repo-url           TEXT                                     URL of the repository. Example: https://repo.exordos.com/exordos-elements/                                                                                                                                                                │
│ --repo-user          TEXT                                     Username for the repository                                                                                                                                                                                                               │
│ --repo-password      TEXT                                     Password for the repository                                                                                                                                                                                                               │
│ --help                                                        Show this message and exit.                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
