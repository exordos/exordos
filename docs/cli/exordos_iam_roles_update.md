
# exordos_iam_roles_update

Update role

## Usage

```console

 Usage: exordos iam roles update [OPTIONS] UUID

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

  Name of the project in which to deploy the role

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the role

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the role

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos iam roles update [OPTIONS] UUID

 Update role

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output       -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                                  │
│ --project-id   -p  UUID                    Name of the project in which to deploy the role                                                                                                                                                                                                               │
│ --name         -n  TEXT                    Name of the role                                                                                                                                                                                                                                              │
│ --description  -D  TEXT                    Description of the role                                                                                                                                                                                                                                       │
│ --help                                     Show this message and exit.                                                                                                                                                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
