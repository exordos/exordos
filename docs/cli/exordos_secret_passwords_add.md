# exordos_secret_passwords_add

Add a new password to the Exordos installation

## Usage

```console

 Usage: exordos secret passwords add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the password

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the password

* `name`:
    * Type: text
    * Default: `test_password`
    * Usage: `-n
--name`

  Name of the password

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the password

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

 Usage: exordos secret passwords add [OPTIONS]

 Add a new password to the Exordos installation

╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID  UUID of the password                             │
│ *  --project-id   -p  UUID  Name of the project in which to deploy the       │
│                             password [required]                              │
│    --name         -n  TEXT  Name of the password                             │
│    --description  -D  TEXT  Description of the password                      │
│    --tag              TEXT  Set the complete tag list. Repeat for each tag.  │
│    --help                   Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
