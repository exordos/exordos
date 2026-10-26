
# exordos_iam_idps_update

Update idp

## Usage

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos iam idps update [OPTIONS] UUID                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                            
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the idp

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the idp

* `iam_client`:
    * Type: uuid
    * Default: `none`
    * Usage: `-i
--iam-client`

  Uuid of iam_client

* `scope`:
    * Type: text
    * Default: `none`
    * Usage: `--scope`

  scope

* `nonce_required`:
    * Type: boolean
    * Default: `none`
    * Usage: `--nonce-required`

  Whether nonce is required

* `callback`:
    * Type: text
    * Default: `none`
    * Usage: `--callback`

  JSON string for callbacks

* `clear_tags`:
    * Type: boolean
    * Default: `false`
    * Usage: `--clear-tags`

  Remove all tags.

* `tags`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--tag`

  Set the complete tag list. Repeat for each tag.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                            
 Usage: exordos iam idps update [OPTIONS] UUID                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                            
 Update idp                                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name                                -n  TEXT  Name of the idp                                                                                                                                                                                                                                          │
│ --description                         -D  TEXT  Description of the idp                                                                                                                                                                                                                                   │
│ --iam-client                          -i  UUID  Uuid of iam_client                                                                                                                                                                                                                                       │
│ --scope                                   TEXT  scope                                                                                                                                                                                                                                                    │
│ --nonce-required/--no-nonce-required            Whether nonce is required                                                                                                                                                                                                                                │
│ --callback                                TEXT  JSON string for callbacks                                                                                                                                                                                                                                │
│ --clear-tags                                    Remove all tags.                                                                                                                                                                                                                                         │
│ --tag                                     TEXT  Set the complete tag list. Repeat for each tag.                                                                                                                                                                                                          │
│ --help                                          Show this message and exit.                                                                                                                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
