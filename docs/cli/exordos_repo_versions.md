
# exordos_repo_versions

List element versions directly from a repository

## Usage

```console

 Usage: exordos repo versions [OPTIONS] NAME

```

## Options

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `name`

* `repo_url`:
    * Type: text
    * Default: `https://repo.exordos.com/exordos-elements`
    * Usage: `--repo-url`

* `stable`:
    * Type: boolean
    * Default: `false`
    * Usage: `--stable`

  Only show stable releases

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `-o
--output`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos repo versions [OPTIONS] NAME

 List element versions directly from a repository

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --repo-url      TEXT          [default:                                      │
│                               https://repo.exordos.com/exordos-elements]     │
│ --stable                      Only show stable releases                      │
│ --output    -o  [table|json]                                                 │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```
