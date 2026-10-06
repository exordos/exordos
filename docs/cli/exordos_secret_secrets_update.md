# exordos_secret_secrets_update

Update secret

## Usage

```console

 Usage: exordos secret secrets update [OPTIONS] UUID

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

  Name of the project in which to deploy the secret

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the secret

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the secret

* `value`:
    * Type: text
    * Default: `none`
    * Usage: `-v
--value`

  New value of the secret

* `default_value`:
    * Type: text
    * Default: `none`
    * Usage: `-d
--default-value`

  New value of the secret to fall back on while the value is unset

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

 Usage: exordos secret secrets update [OPTIONS] UUID

 Update secret

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --project-id     -p  UUID  Name of the project in which to deploy the secret │
│ --name           -n  TEXT  Name of the secret                                │
│ --description    -D  TEXT  Description of the secret                         │
│ --value          -v  TEXT  New value of the secret                           │
│ --default-value  -d  TEXT  New value of the secret to fall back on while the │
│                            value is unset                                    │
│ --clear-tags               Remove all tags.                                  │
│ --tag                TEXT  Set the complete tag list. Repeat for each tag.   │
│ --help                     Show this message and exit.                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```
