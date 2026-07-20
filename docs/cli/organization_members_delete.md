
# organization_members_delete

Delete organization_member

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam organization_members delete [OPTIONS] UUID                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam organization_members delete [OPTIONS] UUID                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
 Delete organization_member                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --yes                -y        Automatically answer yes for all questions                                                                                                                                                                                                                            │
│ *  --organization-uuid      UUID  [required]                                                                                                                                                                                                                                                            │
│    --help                         Show this message and exit.                                                                                                                                                                                                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
