
# exordos_deploy

Deploy the element to realm through the proxy repository

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos deploy [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
```

## Options

* `exordos_cfg_file`:
    * Type: text
    * Default: `exordos.yaml`
    * Usage: `-c
--exordos-cfg-file`

  Name of the project configuration file

* `output_dir`:
    * Type: text
    * Default: `output`
    * Usage: `-o
--output-dir`

  Directory where element artifacts are stored

* `only_manifests`:
    * Type: boolean
    * Default: `true`
    * Usage: `--only-manifests`

  Rebuild if the output already exists

* `watch`:
    * Type: boolean
    * Default: `true`
    * Usage: `-w
--watch`

  Watch deploy process

* `interval`:
    * Type: float range
    * Default: `1.0`
    * Usage: `--interval`

  Refresh interval in seconds.

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos deploy [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
 Deploy the element to realm through the proxy repository                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --exordos-cfg-file  -c  TEXT                  Name of the project configuration file                                                                                                                                                                                                                    │
│ --output-dir        -o  TEXT                  Directory where element artifacts are stored                                                                                                                                                                                                              │
│ --only-manifests                              Rebuild if the output already exists                                                                                                                                                                                                                      │
│ --watch             -w                        Watch deploy process                                                                                                                                                                                                                                      │
│ --interval              FLOAT RANGE [x>=0.1]  Refresh interval in seconds.                                                                                                                                                                                                                              │
│ --help                                        Show this message and exit.                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
