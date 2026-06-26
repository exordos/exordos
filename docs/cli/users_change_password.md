
# users_change_password

Change password of the user

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam users change_password [OPTIONS] USER                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
```

## Options

* `user` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `user`

  user UUID or username

* `old_password` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-o
--old-password`

  Old password of the user

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam users change_password [OPTIONS] USER                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
```
