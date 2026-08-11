
# users_reset_password

Reset password of the user

## Usage

```console
                                                                                
 Usage: exordos iam users reset_password [OPTIONS] USER                         
                                                                                
```

## Options

* `user` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `user`

  user UUID

* `code`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-c
--code`

  Verification code for the user

* `new_password`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--new-password`

  New password of the user. If not provided, will be asked interactively

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: exordos iam users reset_password [OPTIONS] USER                         
                                                                                
```
