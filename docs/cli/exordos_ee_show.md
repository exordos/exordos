
# exordos_ee_show

Show element general information

## Usage

```console

 Usage: exordos ee show [OPTIONS] NAME

```

## Options

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `name`

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos ee show [OPTIONS] NAME

 Show element general information

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output  -o  [json|html|table|yaml]  Output format; JSON prints one resource object.                                                                                                                                                                                                                    │
│ --help                                Show this message and exit.                                                                                                                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
