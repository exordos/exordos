
# exordos_compute_cloud-connections_add

Register OpenStack credentials in Core

## Usage

```console

 Usage: exordos compute cloud-connections add [OPTIONS]

```

## Options

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--name
-n`

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--project-id
-p`

  Core project UUID

* `kind`:
    * Type: choice
    * Default: `openstack`
    * Usage: `--kind`

  Cloud driver kind

* `auth_url` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--auth-url`

  Keystone v3 URL

* `region`:
    * Type: text
    * Default: `none`
    * Usage: `--region`

* `interface`:
    * Type: choice
    * Default: `public`
    * Usage: `--interface`

* `auth_type`:
    * Type: choice
    * Default: `v3applicationcredential`
    * Usage: `--auth-type`

* `application_credential_id`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--application-credential-id`

* `application_credential_secret`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--application-credential-secret`

  Secret; prompted without echo when omitted.

* `username`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--username`

* `password`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--password`

  Password; prompted without echo when omitted.

* `os_project_id`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--os-project-id`

  OpenStack project UUID, distinct from Core project UUID.

* `os_project_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--os-project-name`

* `user_domain_name`:
    * Type: text
    * Default: `default`
    * Usage: `--user-domain-name`

* `project_domain_name`:
    * Type: text
    * Default: `default`
    * Usage: `--project-domain-name`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos compute cloud-connections add [OPTIONS]

```
