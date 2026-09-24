
# exordos_metapaas_mail_accounts_add

Add a new account

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail accounts add [OPTIONS]                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the account

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to create the account

* `instance_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--instance-uuid`

  UUID of the mail instance to create the account in

* `username` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--username`

  SMTP login of the account, the local part of the address

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the account

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `--description`

  Description of the account

* `password`:
    * Type: text
    * Default: `none`
    * Usage: `--password`

  Password of the account, hashed by the API before it is stored

* `active`:
    * Type: boolean
    * Default: `none`
    * Usage: `--active`

  Whether the account is allowed to authenticate

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail accounts add [OPTIONS]                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Add a new account                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid                -u  UUID  UUID of the account                                                                                                                                                                                                                                                  │
│ *  --project-id          -p  UUID  UUID of the project in which to create the account [required]                                                                                                                                                                                                        │
│ *  --instance-uuid       -i  TEXT  UUID of the mail instance to create the account in [required]                                                                                                                                                                                                        │
│ *  --username                TEXT  SMTP login of the account, the local part of the address [required]                                                                                                                                                                                                  │
│    --name                -n  TEXT  Name of the account                                                                                                                                                                                                                                                  │
│    --description             TEXT  Description of the account                                                                                                                                                                                                                                           │
│    --password                TEXT  Password of the account, hashed by the API before it is stored                                                                                                                                                                                                       │
│    --active/--no-active            Whether the account is allowed to authenticate                                                                                                                                                                                                                       │
│    --help                          Show this message and exit.                                                                                                                                                                                                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
