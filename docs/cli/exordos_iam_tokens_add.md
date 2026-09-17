
# exordos_iam_tokens_add

Add a new token to the Exordos installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam tokens add [OPTIONS]                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the token

* `user` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--user`

  UUID of the user the token authenticates

* `iam_client` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--iam-client`

  UUID of the IAM client that signs the token

* `scope`:
    * Type: text
    * Default: `none`
    * Usage: `-s
--scope`

  Scope of the token, e.g. 'project:<uuid>'

* `expiration_delta`:
    * Type: integer
    * Default: `none`
    * Usage: `-e
--expiration-delta`

  Lifetime in seconds, at least 60. The platform renews the token

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam tokens add [OPTIONS]                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
 Add a new token to the Exordos installation                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid              -u  UUID     UUID of the token                                                                                                                                                                                                                                                   │
│ *  --user                  UUID     UUID of the user the token authenticates [required]                                                                                                                                                                                                                 │
│ *  --iam-client            UUID     UUID of the IAM client that signs the token [required]                                                                                                                                                                                                              │
│    --scope             -s  TEXT     Scope of the token, e.g. 'project:<uuid>'                                                                                                                                                                                                                           │
│    --expiration-delta  -e  INTEGER  Lifetime in seconds, at least 60. The platform renews the token                                                                                                                                                                                                     │
│    --help                           Show this message and exit.                                                                                                                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
