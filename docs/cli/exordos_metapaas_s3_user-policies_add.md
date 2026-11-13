
# exordos_metapaas_s3_user-policies_add

Attach a policy to a user

## Usage

```console

 Usage: exordos metapaas s3 user-policies add [OPTIONS]

```

## Options

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object (an array for bulk creation).

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the policy attachment

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to create the policy attachment

* `instance_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--instance-uuid`

  UUID of the instance the user and the policy belong to

* `user_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--user-uuid`

  UUID of the user to attach the policy to

* `policy` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--policy`

  UUID or name of the policy to attach

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos metapaas s3 user-policies add [OPTIONS]

 Attach a policy to a user

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output         -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                             │
│    --uuid           -u  UUID                    UUID of the policy attachment                                                                                                                                                                                                                            │
│ *  --project-id     -p  UUID                    UUID of the project in which to create the policy attachment [required]                                                                                                                                                                                  │
│ *  --instance-uuid  -i  TEXT                    UUID of the instance the user and the policy belong to [required]                                                                                                                                                                                        │
│ *  --user-uuid          TEXT                    UUID of the user to attach the policy to [required]                                                                                                                                                                                                      │
│ *  --policy             TEXT                    UUID or name of the policy to attach [required]                                                                                                                                                                                                          │
│    --help                                       Show this message and exit.                                                                                                                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
