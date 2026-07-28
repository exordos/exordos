
# exordos

Provides all the necessary tools for work with Exordos Platform

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
```

## Options

* `config`:
    * Type: file
    * Default: `/home/user/.exordos/exordosctl.yaml`
    * Usage: `--config`

  Path to YAML config file

* `endpoint`:
    * Type: text
    * Default: `http://localhost:11010`
    * Usage: `-e
--endpoint`

  Exordos API endpoint

* `ecosystem_endpoint`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--ecosystem-endpoint`

  Exordos ecosystem API endpoint

* `user`:
    * Type: text
    * Default: `none`
    * Usage: `-u
--user`

  Client user name

* `login`:
    * Type: text
    * Default: `none`
    * Usage: `-l
--login`

  Client login

* `password`:
    * Type: text
    * Default: `none`
    * Usage: `-p
--password`

  Password for the client user

* `access_token`:
    * Type: text
    * Default: `none`
    * Usage: `-a
--access-token`

  access token for the client user

* `refresh_token`:
    * Type: text
    * Default: `none`
    * Usage: `--refresh-token`

  refresh token for the client user

* `realm`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--realm`

  Name of the realm

* `context`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-c
--context`

  Name of the context

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-P
--project-id`

  Project ID for the client user

* `verbose`:
    * Type: boolean
    * Default: `false`
    * Usage: `-vvv
--verbose`

  Verbose logs

* `developer_key_path`:
    * Type: text
    * Default: `none`
    * Usage: `-i
--developer-key-path`

  Path to developer public key

* `silent`:
    * Type: boolean
    * Default: `false`
    * Usage: `-s
--silent`

  Do not print messages, warnings or errors

* `otp_code`:
    * Type: text
    * Default: `none`
    * Usage: `--otp-code`

  OTP code for two-factor authentication

* `ttl`:
    * Type: float
    * Default: `none`
    * Usage: `--ttl`

  Time to live for the access token

* `refresh_ttl`:
    * Type: float
    * Default: `none`
    * Usage: `--refresh-ttl`

  Time to live for the refresh token

* `check_updates`:
    * Type: boolean
    * Default: `false`
    * Usage: `--check-updates`

  Check for updates

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
```
