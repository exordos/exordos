
# exordos_dns_domains_update

Update domain

## Usage

```console

 Usage: exordos dns domains update [OPTIONS] UUID

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

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the domain

* `sync_to_ecosystem`:
    * Type: boolean
    * Default: `false`
    * Usage: `-s
--sync-to-ecosystem`

  Sync the domain to the ecosystem

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

 Usage: exordos dns domains update [OPTIONS] UUID

 Update domain

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output             -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                            │
│ --name               -n  TEXT                    Name of the domain                                                                                                                                                                                                                                      │
│ --sync-to-ecosystem  -s                          Sync the domain to the ecosystem                                                                                                                                                                                                                        │
│ --clear-tags                                     Remove all tags.                                                                                                                                                                                                                                        │
│ --tag                    TEXT                    Set the complete tag list. Repeat for each tag.                                                                                                                                                                                                         │
│ --help                                           Show this message and exit.                                                                                                                                                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
