
# exordos_ee_install

Install elements by UUID, name, name glob, or manifest path.

Name globs support *, ?, and [abc] and match case-sensitively. Quote patterns to prevent shell expansion: exordos ee install 'ecosystem_ui_*'. Each matching name is installed once, using the usual version selection. An unmatched pattern is an error.

## Usage

```console

 Usage: exordos ee install [OPTIONS] [UUID_OR_NAME_OR_PATH]...

```

## Options

* `version`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--version`

  Version to use for all elements specified by name

* `project_id`:
    * Type: uuid
    * Default: `00000000-0000-0000-0000-000000000000`
    * Usage: `-p
--project-id`

  Project UUID, required only if the upload repository doesn't exist yet

* `timeout`:
    * Type: float
    * Default: `600.0`
    * Usage: `--timeout`

  Seconds to wait for repository upload and element sync to complete

* `uuid_or_name_or_path`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid_or_name_or_path`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos ee install [OPTIONS] [UUID_OR_NAME_OR_PATH]...

 Install elements by UUID, name, name glob, or manifest path.
 Name globs support *, ?, and [abc] and match case-sensitively. Quote patterns to prevent shell expansion: exordos ee install 'ecosystem_ui_*'. Each matching name is installed once, using the usual version selection. An unmatched pattern is an error.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version     -v  TEXT   Version to use for all elements specified by name                                                                                                                                                                                                                               │
│ --project-id  -p  UUID   Project UUID, required only if the upload repository doesn't exist yet                                                                                                                                                                                                          │
│ --timeout         FLOAT  Seconds to wait for repository upload and element sync to complete [default: 600.0]                                                                                                                                                                                             │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
