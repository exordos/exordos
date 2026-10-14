
# exordos_iam_tokens_add

Issue a new token. The signed token is in the answer to this command and nowhere else: copy it now, a read never returns it

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

* `user`:
    * Type: uuid
    * Default: `none`
    * Usage: `--user`

  UUID of the user the token authenticates. Defaults to the account running the command; naming another user takes the iam.token.create_all permission

* `iam_client`:
    * Type: uuid
    * Default: `00000000-0000-0000-0000-000000000000`
    * Usage: `--iam-client`

  UUID of the IAM client that signs the token

* `scope`:
    * Type: text
    * Default: `none`
    * Usage: `-s
--scope`

  Scope of the token, e.g. 'project:<uuid>'

* `days`:
    * Type: integer range
    * Default: `30`
    * Usage: `-d
--days`

  How many days the token lives before it is spent

* `no_expire`:
    * Type: boolean
    * Default: `false`
    * Usage: `--no-expire`

  Keep the token alive instead: the platform renews it before it expires, for as long as the token exists

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam tokens add [OPTIONS]                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
 Issue a new token. The signed token is in the answer to this command and nowhere else: copy it now, a read never returns it                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --uuid        -u  UUID                  UUID of the token                                                                                                                                                                                                                                               │
│ --user            UUID                  UUID of the user the token authenticates. Defaults to the account running the command; naming another user takes the iam.token.create_all permission                                                                                                            │
│ --iam-client      UUID                  UUID of the IAM client that signs the token [default: 00000000-0000-0000-0000-000000000000]                                                                                                                                                                     │
│ --scope       -s  TEXT                  Scope of the token, e.g. 'project:<uuid>'                                                                                                                                                                                                                       │
│ --days        -d  INTEGER RANGE [x>=1]  How many days the token lives before it is spent [default: 30]                                                                                                                                                                                                  │
│ --no-expire                             Keep the token alive instead: the platform renews it before it expires, for as long as the token exists                                                                                                                                                         │
│ --help                                  Show this message and exit.                                                                                                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
