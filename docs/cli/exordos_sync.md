
# exordos_sync

copy exordos element from local git repo to element nodes, example cmd: exordos sync --name empty /home/user/PycharmProjects/exordos/exordos_empty

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos sync [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `target_dir`:
    * Type: path
    * Default: `sentinel.unset`
    * Usage: `-t
--target-dir`

  Directory to copy exordos core to

* `name`:
    * Type: text
    * Default: `core`
    * Usage: `-n
--name`

  Element name

* `user`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--user`

  ssh user name

* `y`:
    * Type: boolean
    * Default: `false`
    * Usage: `--y
-y`

  Automatically answer yes for all questions

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos sync [OPTIONS] [PROJECT_DIR]                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 copy exordos element from local git repo to element nodes, example cmd: exordos sync --name empty /home/user/PycharmProjects/exordos/exordos_empty                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --target-dir  -t  PATH  Directory to copy exordos core to                                                                                                                                                                                                                                               │
│ --name        -n  TEXT  Element name                                                                                                                                                                                                                                                                    │
│ --user            TEXT  ssh user name                                                                                                                                                                                                                                                                   │
│ --y           -y        Automatically answer yes for all questions                                                                                                                                                                                                                                      │
│ --help                  Show this message and exit.                                                                                                                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
