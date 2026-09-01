
# exordos_iam_organization_members_show

Show organization_member

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam organization_members show [OPTIONS] UUID                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
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

* `organization_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--organization-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam organization_members show [OPTIONS] UUID                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 Show organization_member                                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output             -o  [json|html|table|yaml]  the output format, defaults to table                                                                                                                                                                                                                │
│ *  --organization-uuid      UUID                    [required]                                                                                                                                                                                                                                          │
│    --help                                           Show this message and exit.                                                                                                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
