
# exordos_deploy

Deploy a built element to a realm. The element must already be built (`exordos build`). With no --repository, the local build output is served in-process and installed directly -- no push needed. With --repository, the build is pushed first, exactly like `exordos push`, then installed.

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos deploy [OPTIONS]                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
```

## Options

* `element_dir`:
    * Type: path
    * Default: `output`
    * Usage: `-e
--element-dir`

  Directory where element artifacts are stored (output of `exordos build`)

* `repository`:
    * Type: text
    * Default: `none`
    * Usage: `-t
--repository`

  Repository name (key from the `repositories` section in ~/.exordos/exordosctl.yaml). Selects push mode: push the build to this repository first, then install. If omitted, local mode is used instead (no push).

* `project_id`:
    * Type: uuid
    * Default: `00000000-0000-0000-0000-000000000000`
    * Usage: `-p
--project-id`

  Project UUID, required only if the dev repository doesn't exist yet

* `dev_repo_name`:
    * Type: text
    * Default: `exordos-dev-repo`
    * Usage: `--dev-repo-name`

  Name of the local dev repository used to publish deployed elements

* `dev_repo_priority`:
    * Type: integer
    * Default: `4096`
    * Usage: `--dev-repo-priority`

  Priority of the local dev repository (0-4096)

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `-f
--force`

  Force push even if the element already exists (push mode only)

* `timeout`:
    * Type: float
    * Default: `600.0`
    * Usage: `--timeout`

  Seconds to wait for repository sync and element install to complete

* `element`:
    * Type: text
    * Default: `none`
    * Usage: `--element`

  Name of the element to deploy from the build inventory. If omitted and multiple elements are available, an interactive prompt is shown. If only one element exists, it is selected automatically.

* `realm`:
    * Type: text
    * Default: `none`
    * Usage: `-r
--realm`

  Name of the realm to deploy to. If omitted, the current realm from the configuration is used.

* `exordosctl_cfg_file`:
    * Type: text
    * Default: `/home/user/.exordos/exordosctl.yaml`
    * Usage: `-c
--exordosctl-cfg-file`

  Name of the exordosctl configuration file

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos deploy [OPTIONS]                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
 Deploy a built element to a realm. The element must already be built (`exordos build`). With no --repository, the local build output is served in-process and installed directly -- no push needed. With --repository, the build is pushed first, exactly like `exordos push`, then installed.            
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --element-dir          -e  PATH     Directory where element artifacts are stored (output of `exordos build`)                                                                                                                                                                                            │
│ --repository           -t  TEXT     Repository name (key from the `repositories` section in ~/.exordos/exordosctl.yaml). Selects push mode: push the build to this repository first, then install. If omitted, local mode is used instead (no push).                                                    │
│ --project-id           -p  UUID     Project UUID, required only if the dev repository doesn't exist yet                                                                                                                                                                                                 │
│ --dev-repo-name            TEXT     Name of the local dev repository used to publish deployed elements [default: exordos-dev-repo]                                                                                                                                                                      │
│ --dev-repo-priority        INTEGER  Priority of the local dev repository (0-4096) [default: 4096]                                                                                                                                                                                                       │
│ --force                -f           Force push even if the element already exists (push mode only)                                                                                                                                                                                                      │
│ --timeout                  FLOAT    Seconds to wait for repository sync and element install to complete [default: 600.0]                                                                                                                                                                                │
│ --element                  TEXT     Name of the element to deploy from the build inventory. If omitted and multiple elements are available, an interactive prompt is shown. If only one element exists, it is selected automatically.                                                                   │
│ --realm                -r  TEXT     Name of the realm to deploy to. If omitted, the current realm from the configuration is used.                                                                                                                                                                       │
│ --exordosctl-cfg-file  -c  TEXT     Name of the exordosctl configuration file                                                                                                                                                                                                                           │
│ --help                              Show this message and exit.                                                                                                                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
