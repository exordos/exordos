
# ee_update

Update element from a YAML file

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos ee update [OPTIONS] PATH_OR_NAME                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
```

## Options

* `repository`:
    * Type: text
    * Default: `https://repository.genesis-core.tech/exordos-elements/`
    * Usage: `-r
--repository`

  Repository endpoint

* `version`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--version`

  version of the element

* `path_or_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `path_or_name`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos ee update [OPTIONS] PATH_OR_NAME                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
 Update element from a YAML file                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --repository  -r  TEXT  Repository endpoint [default: https://repository.genesis-core.tech/exordos-elements/]                                                                                                                                                                                           │
│ --version     -v  TEXT  version of the element                                                                                                                                                                                                                                                          │
│ --help                  Show this message and exit.                                                                                                                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
