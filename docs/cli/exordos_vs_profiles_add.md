
# exordos_vs_profiles_add

Add a new profile to the Exordos installation

## Usage

```console

 Usage: exordos vs profiles add [OPTIONS]

```

## Options

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object (an array for bulk creation).

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the profile

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the profile

* `name`:
    * Type: text
    * Default: `profile`
    * Usage: `-n
--name`

  Name of the profile

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the profile

* `profile_type`:
    * Type: text
    * Default: `global`
    * Usage: `-t
--profile_type`

  Profile_type (ELEMENT, GLOBAL)

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos vs profiles add [OPTIONS]

 Add a new profile to the Exordos installation

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --output        -o  [json|html|table|yaml]  Output format; JSON prints one resource object (an array for bulk creation).                                                                                                                                                                              │
│    --uuid          -u  UUID                    UUID of the profile                                                                                                                                                                                                                                       │
│ *  --project-id    -p  UUID                    Name of the project in which to deploy the profile [required]                                                                                                                                                                                             │
│    --name          -n  TEXT                    Name of the profile                                                                                                                                                                                                                                       │
│    --description   -D  TEXT                    Description of the profile                                                                                                                                                                                                                                │
│    --profile_type  -t  TEXT                    Profile_type (ELEMENT, GLOBAL)                                                                                                                                                                                                                            │
│    --help                                      Show this message and exit.                                                                                                                                                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
