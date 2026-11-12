
# exordos_iam_permissions_add

Add a new permission to the Exordos installation

## Usage

```console

 Usage: exordos iam permissions add [OPTIONS]

```

## Options

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object (an array for bulk creation).

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the permission

* `name`:
    * Type: text
    * Default: `test_permission`
    * Usage: `-n
--name`

  Name of the permission

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the permission

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

 Usage: exordos iam permissions add [OPTIONS]

 Add a new permission to the Exordos installation

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output       -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                                  │
│ --uuid         -u  UUID                    UUID of the permission                                                                                                                                                                                                                                        │
│ --name         -n  TEXT                    Name of the permission                                                                                                                                                                                                                                        │
│ --description  -D  TEXT                    Description of the permission                                                                                                                                                                                                                                 │
│ --tag              TEXT                    Set the complete tag list. Repeat for each tag.                                                                                                                                                                                                               │
│ --help                                     Show this message and exit.                                                                                                                                                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
