
# exordos_iam_organization_members_add

Add a new organization_member to the Exordos installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam organization_members add [OPTIONS]                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the organization_member

* `organization_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-o
--organization-uuid`

  organization uuid

* `user` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--user`

  user uuid

* `role`:
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `-r
--role`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam organization_members add [OPTIONS]                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
 Add a new organization_member to the Exordos installation                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid               -u  UUID            UUID of the organization_member                                                                                                                                                                                                                             │
│ *  --organization-uuid  -o  UUID            organization uuid [required]                                                                                                                                                                                                                                │
│ *  --user                   UUID            user uuid [required]                                                                                                                                                                                                                                        │
│    --role               -r  [member|owner]                                                                                                                                                                                                                                                              │
│    --help                                   Show this message and exit.                                                                                                                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
