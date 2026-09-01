
# exordos_configs_add-from-env

Add configuration from environment variables

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos configs add-from-env [OPTIONS] NODE                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```

## Options

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project ID ofthe config

* `env_prefix`:
    * Type: text
    * Default: `gct_env_`
    * Usage: `--env-prefix`

  Prefix used to filter environment variables for envs

* `env_path`:
    * Type: text
    * Default: `/var/lib/exordos/app.env`
    * Usage: `--env-path`

  Path to the env file will be saved on the node

* `env_format`:
    * Type: choice
    * Default: `env`
    * Usage: `--env-format`

  Format of the env file

* `cfg_prefix`:
    * Type: text
    * Default: `gct_cfg_`
    * Usage: `--cfg-prefix`

  Prefix used to filter environment variables for configs

* `base64`:
    * Type: boolean
    * Default: `false`
    * Usage: `--base64`

  Base64 encode is enabled for configs

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  Config UUID

* `node` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `node`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos configs add-from-env [OPTIONS] NODE                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```
