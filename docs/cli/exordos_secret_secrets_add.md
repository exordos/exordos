# exordos_secret_secrets_add

Add a new secret to the Exordos installation

## Usage

```console

 Usage: exordos secret secrets add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the secret

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the secret

* `name`:
    * Type: text
    * Default: `test_secret`
    * Usage: `-n
--name`

  Name of the secret

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the secret

* `value`:
    * Type: text
    * Default: `none`
    * Usage: `-v
--value`

  Value of the secret

* `default_value`:
    * Type: text
    * Default: `none`
    * Usage: `-d
--default-value`

  Value of the secret to fall back on while the value is unset

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

 Usage: exordos secret secrets add [OPTIONS]

 Add a new secret to the Exordos installation

╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid           -u  UUID  UUID of the secret                             │
│ *  --project-id     -p  UUID  Name of the project in which to deploy the     │
│                               secret [required]                              │
│    --name           -n  TEXT  Name of the secret                             │
│    --description    -D  TEXT  Description of the secret                      │
│    --value          -v  TEXT  Value of the secret                            │
│    --default-value  -d  TEXT  Value of the secret to fall back on while the  │
│                               value is unset                                 │
│    --tag                TEXT  Set the complete tag list. Repeat for each     │
│                               tag.                                           │
│    --help                     Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```
