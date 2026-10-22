
# exordos_storages_pools_show

Show storage pool

## Usage

```console

 Usage: exordos storages pools show [OPTIONS] UUID

```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  the output format, defaults to table

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos storages pools show [OPTIONS] UUID

 Show storage pool

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --output  -o  [json|html|table|yaml]  the output format, defaults to table   │
│ --help                                Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯
```
