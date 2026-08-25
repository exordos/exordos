
# exordos_dns_records_show

Show record

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dns records show [OPTIONS] UUID                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
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

* `domain_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--domain-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dns records show [OPTIONS] UUID                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
 Show record                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output       -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                      │
│ *  --domain-uuid      UUID                    [required]                                                                                                                                                                                                                                                │
│    --help                                     Show this message and exit.                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
