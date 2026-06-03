
# exordos_build

Build a Exordos element. The command build all images, manifests and other artifacts required for the element. The manifest in the project may be a raw YAML file or a template using Jinja2 templates. For Jinja2 templates, the following variables are available by default:

- {{ version }}: version of the element

- {{ name }}: name of the element

- {{ manifests }}: list of manifests

Additional variables can be passed using the --manifest-var options.

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos build [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

- `exordos_cfg_file`:
    - Type: text
    - Default: `exordos.yaml`
    - Usage: `-c
--exordos-cfg-file`

  Name of the project configuration file

- `deps_dir`:
    - Type: text
    - Default: `none`
    - Usage: `--deps-dir`

  Directory where dependencies will be fetched

- `output_dir`:
    - Type: path
    - Default: `output`
    - Usage: `-o
--output-dir`

  Directory where output artifacts will be stored

- `ssh_public_key`:
    - Type: path
    - Default: `sentinel.unset`
    - Usage: `-i
--ssh-public-key`

  Path to a public SSH key file to inject into the VM. Can be specified multiple times. If not provided, no key will be injected.

- `force`:
    - Type: boolean
    - Default: `false`
    - Usage: `-f
--force`

  Rebuild if the output already exists

- `manifest_var`:
    - Type: text
    - Default: `sentinel.unset`
    - Usage: `--manifest-var`

  Additional variables to pass to the manifest template. The format is 'key=value'. For example: --manifest-var key1=value1 --manifest-var key2=value2

- `project_dir`:
    - Type: path
    - Default: `.`
    - Usage: `project_dir`

- `help`:
    - Type: boolean
    - Default: `false`
    - Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos build [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 Build a Exordos element. The command build all images, manifests and other artifacts required for the element. The manifest in the project may be a raw YAML file or a template using Jinja2 templates. For Jinja2 templates, the following variables are available by default:                           
 - {{ version }}: version of the element                                                                                                                                                                                                                                                                   
 - {{ name }}: name of the element                                                                                                                                                                                                                                                                         
 - {{ manifests }}: list of manifests                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
 Additional variables can be passed using the --manifest-var options.                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --exordos-cfg-file  -c  TEXT  Name of the project configuration file                                                                                                                                                                                                                                    │
│ --deps-dir              TEXT  Directory where dependencies will be fetched                                                                                                                                                                                                                              │
│ --output-dir        -o  PATH  Directory where output artifacts will be stored                                                                                                                                                                                                                           │
│ --ssh-public-key    -i  PATH  Path to a public SSH key file to inject into the VM. Can be specified multiple times. If not provided, no key will be injected.                                                                                                                                           │
│ --force             -f        Rebuild if the output already exists                                                                                                                                                                                                                                      │
│ --manifest-var          TEXT  Additional variables to pass to the manifest template. The format is 'key=value'. For example: --manifest-var key1=value1 --manifest-var key2=value2                                                                                                                      │
│ --help                        Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
