
# exordos_iam_tokens_regenerate

Sign a new token in place of the one issued so far. The previous token stops working at once, and the new one is in the answer to this command and nowhere else: copy it now

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam tokens regenerate [OPTIONS] UUID                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `y`:
    * Type: boolean
    * Default: `false`
    * Usage: `--y
-y`

  Automatically answer yes for all questions

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam tokens regenerate [OPTIONS] UUID                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Sign a new token in place of the one issued so far. The previous token stops working at once, and the new one is in the answer to this command and nowhere else: copy it now                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --y     -y  Automatically answer yes for all questions                                                                                                                                                                                                                                                  │
│ --help      Show this message and exit.                                                                                                                                                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
