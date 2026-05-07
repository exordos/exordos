
# repo_init

Initialize the repository

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo init [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
```

## Options

* `exordos_cfg_file`:
    * Type: text
    * Default: `exordos.yaml`
    * Usage: `-c
--exordos-cfg-file`

  Name of the project configuration file

* `target`:
    * Type: text
    * Default: `none`
    * Usage: `-t
--target`

  Target repository to push to

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `-f
--force`

  Force init even if the repo already exists

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos repo init [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
 Initialize the repository                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --exordos-cfg-file  -c  TEXT  Name of the project configuration file                                                                                                                                                                                                                                    │
│ --target            -t  TEXT  Target repository to push to                                                                                                                                                                                                                                              │
│ --force             -f        Force init even if the repo already exists                                                                                                                                                                                                                                │
│ --help                        Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
