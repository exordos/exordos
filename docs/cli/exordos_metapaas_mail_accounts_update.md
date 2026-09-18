
# exordos_metapaas_mail_accounts_update

Update account

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail accounts update [OPTIONS] UUID                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `instance_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--instance-uuid`

  UUID of the mail instance the account belongs to

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the account

* `description`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--description`

  Description of the account

* `password`:
    * Type: text
    * Default: `sentinel.unset`
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail accounts update [OPTIONS] UUID                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 Update account                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --instance-uuid       -i  TEXT  UUID of the mail instance the account belongs to [required]                                                                                                                                                                                                          │
│    --name                -n  TEXT  Name of the account                                                                                                                                                                                                                                                  │
│    --description             TEXT  Description of the account                                                                                                                                                                                                                                           │
│    --password                TEXT  Password of the account, hashed by the API before it is stored                                                                                                                                                                                                       │
│    --active/--no-active            Whether the account is allowed to authenticate                                                                                                                                                                                                                       │
│    --help                          Show this message and exit.                                                                                                                                                                                                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
