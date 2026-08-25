
# exordos_iam_projects_add_user

Add a user to a project (by UUID, email, or name)

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam projects add_user [OPTIONS]                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
```

## Options

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project

* `user` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-u
--user`

  UUID, email, or name of the user to add

* `role` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--role`

  Role to assign (e.g. 'owner')

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos iam projects add_user [OPTIONS]                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
```
