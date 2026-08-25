
# exordos_settings_repo_add

Add a repository entry to the settings file

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos settings repo add [OPTIONS] REPO                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
```

## Options

* `repo` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `repo`

* `driver` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--driver`

  Driver kind for the repository, e.g. nginx

* `url` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-u
--url`

  URL of the repository

* `username`:
    * Type: text
    * Default: `none`
    * Usage: `--username`

  Username for the repository

* `password`:
    * Type: text
    * Default: `none`
    * Usage: `--password`

  Password for the repository

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos settings repo add [OPTIONS] REPO                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
```
