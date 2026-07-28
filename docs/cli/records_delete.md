
# records_delete

Delete record

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dns records delete [OPTIONS] UUID...                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `y`:
    * Type: boolean
    * Default: `false`
    * Usage: `--yes
-y`

  Automatically answer yes for all questions

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos dns records delete [OPTIONS] UUID...                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Delete record                                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --yes          -y        Automatically answer yes for all questions                                                                                                                                                                                                                                  │
│ *  --domain-uuid      UUID  [required]                                                                                                                                                                                                                                                                  │
│    --help                   Show this message and exit.                                                                                                                                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
