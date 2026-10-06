# exordos_iam_permissions_tags

Replace or clear tags on permission

## Usage

```console

 Usage: exordos iam permissions tags [OPTIONS] UUID

```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `tags`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--tag`

  Replace all tags with these values. Repeat for each tag.

* `clear`:
    * Type: boolean
    * Default: `false`
    * Usage: `--clear`

  Remove all tags.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos iam permissions tags [OPTIONS] UUID

 Replace or clear tags on permission

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --tag    TEXT  Replace all tags with these values. Repeat for each tag.      │
│ --clear        Remove all tags.                                              │
│ --help         Show this message and exit.                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```
