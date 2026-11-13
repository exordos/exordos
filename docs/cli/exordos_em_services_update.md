
# exordos_em_services_update

Update service

## Usage

```console

 Usage: exordos em services update [OPTIONS] UUID

```

## Options

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object (an array for bulk creation).

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the service

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the service

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the service

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

 Usage: exordos em services update [OPTIONS] UUID

 Update service

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output       -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                                  │
│ --project-id   -p  UUID                    Name of the project in which to deploy the service                                                                                                                                                                                                            │
│ --name         -n  TEXT                    Name of the service                                                                                                                                                                                                                                           │
│ --description  -D  TEXT                    Description of the service                                                                                                                                                                                                                                    │
│ --clear-tags                               Remove all tags.                                                                                                                                                                                                                                              │
│ --tag              TEXT                    Set the complete tag list. Repeat for each tag.                                                                                                                                                                                                               │
│ --help                                     Show this message and exit.                                                                                                                                                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
