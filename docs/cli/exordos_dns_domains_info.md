# exordos_dns_domains_info

Show domain details with DNS records

## Usage

```console

 Usage: exordos dns domains info [OPTIONS] UUID

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

 Usage: exordos dns domains info [OPTIONS] UUID

 Show domain details with DNS records

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --output  -o  [json|html|table|yaml]  the output format, defaults to table   │
│ --help                                Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯
```
