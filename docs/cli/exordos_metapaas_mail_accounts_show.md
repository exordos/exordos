
# exordos_metapaas_mail_accounts_show

Show account

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail accounts show [OPTIONS] UUID                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
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

* `instance_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--instance-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail accounts show [OPTIONS] UUID                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
 Show account                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output         -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                    │
│ *  --instance-uuid      UUID                    [required]                                                                                                                                                                                                                                              │
│    --help                                       Show this message and exit.                                                                                                                                                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
