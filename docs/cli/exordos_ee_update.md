
# exordos_ee_update

Update elements by UUID, name, name glob, or manifest path.

Name globs support *, ?, and [abc] and match case-sensitively. Quote patterns to prevent shell expansion: exordos ee update 'ecosystem_ui_*'. Globs select installed elements only; each matching name is updated once. An unmatched pattern is an error. With --tag or --clear-tags, only installed element tags are changed; the element version is not updated.

## Usage

```console

 Usage: exordos ee update [OPTIONS] [UUID_OR_NAME_OR_PATH]...

```

## Options

* `dev`:
    * Type: boolean
    * Default: `false`
    * Usage: `--dev`

  Update to the latest development/prerelease version

* `version`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--version`

  version of the element

* `y`:
    * Type: boolean
    * Default: `false`
    * Usage: `--yes
-y`

  Automatically answer yes for all questions

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

* `clear_tags`:
    * Type: boolean
    * Default: `false`
    * Usage: `--clear-tags`

  Remove all tags.

* `tags`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--tag`

  Set the complete tag list. Repeat for each tag.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos ee update [OPTIONS] [UUID_OR_NAME_OR_PATH]...

 Update elements by UUID, name, name glob, or manifest path.
 Name globs support *, ?, and [abc] and match case-sensitively. Quote patterns to prevent shell expansion: exordos ee update 'ecosystem_ui_*'. Globs select installed elements only; each matching name is updated once. An unmatched pattern is an error. With --tag or --clear-tags, only installed
 element tags are changed; the element version is not updated.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --dev                    Update to the latest development/prerelease version                                                                                                                                                                                                                             │
│ --version     -v  TEXT   version of the element                                                                                                                                                                                                                                                          │
│ --yes         -y         Automatically answer yes for all questions                                                                                                                                                                                                                                      │
│ --project-id  -p  UUID   Project UUID, required only if the upload repository doesn't exist yet                                                                                                                                                                                                          │
│ --timeout         FLOAT  Seconds to wait for repository upload and element sync to complete [default: 600.0]                                                                                                                                                                                             │
│ --clear-tags             Remove all tags.                                                                                                                                                                                                                                                                │
│ --tag             TEXT   Set the complete tag list. Repeat for each tag.                                                                                                                                                                                                                                 │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
