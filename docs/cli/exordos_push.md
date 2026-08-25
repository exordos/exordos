
# exordos_push

Push the element to the repository

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos push [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `exordos_cfg_file`:
    * Type: text
    * Default: `exordos.yaml`
    * Usage: `-c
--exordos-cfg-file`

  Name of the project configuration file

* `driver`:
    * Type: text
    * Default: `none`
    * Usage: `-d
--driver`

  Driver to use, nginx for example

* `driver_params`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--driver-params`

  Additional params to pass to the driver. The format is 'key=value'. For example: --driver-params url=<http://repo.local.exordos.com:8080/> --driver-params auth=["user","password"]

* `target`:
    * Type: text
    * Default: `none`
    * Usage: `-t
--target`

  Target repository to push to

* `element_dir`:
    * Type: path
    * Default: `output`
    * Usage: `-e
--element-dir`

  Directory where element artifacts are stored

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `-f
--force`

  Force push even if the element already exists

* `latest`:
    * Type: boolean
    * Default: `false`
    * Usage: `-l
--latest`

  Push the element too as the latest version (if stable version)

* `jobs`:
    * Type: integer range
    * Default: `1`
    * Usage: `-j
--jobs`

  Number of artifacts to upload in parallel

* `project_dir`:
    * Type: path
    * Default: `.`
    * Usage: `project_dir`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos push [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 Push the element to the repository                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --exordos-cfg-file  -c  TEXT                  Name of the project configuration file                                                                                                                                                                                                                    │
│ --driver            -d  TEXT                  Driver to use, nginx for example                                                                                                                                                                                                                          │
│ --driver-params         TEXT                  Additional params to pass to the driver. The format is 'key=value'. For example: --driver-params url=http://repo.local.exordos.com:8080/ --driver-params auth=["user","password"]                                                                         │
│ --target            -t  TEXT                  Target repository to push to                                                                                                                                                                                                                              │
│ --element-dir       -e  PATH                  Directory where element artifacts are stored                                                                                                                                                                                                              │
│ --force             -f                        Force push even if the element already exists                                                                                                                                                                                                             │
│ --latest            -l                        Push the element too as the latest version (if stable version)                                                                                                                                                                                            │
│ --jobs              -j  INTEGER RANGE [x>=1]  Number of artifacts to upload in parallel [default: 1]                                                                                                                                                                                                    │
│ --help                                        Show this message and exit.                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
