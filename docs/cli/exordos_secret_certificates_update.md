
# exordos_secret_certificates_update

Update certificate

## Usage

```console

 Usage: exordos secret certificates update [OPTIONS] UUID

```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the certificate

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the certificate

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the certificate

* `email`:
    * Type: text
    * Default: `none`
    * Usage: `-e
--email`

  Email address to use for the certificate

* `domains`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--domain`

  Domain of the certificate, replaces the current list. Can be repeated

* `method`:
    * Type: choice
    * Default: `none`
    * Usage: `-m
--method`

  Method (provider) to issue and manage the certificate

* `cert`:
    * Type: filename
    * Default: `sentinel.unset`
    * Usage: `--cert`

  PEM certificate or full chain file

* `key`:
    * Type: filename
    * Default: `sentinel.unset`
    * Usage: `--key`

  Unencrypted PEM private key file

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos secret certificates update [OPTIONS] UUID

 Update certificate

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID               Name of the project in which to deploy │
│                                       the certificate                        │
│ --name         -n  TEXT               Name of the certificate                │
│ --description  -D  TEXT               Description of the certificate         │
│ --email        -e  TEXT               Email address to use for the           │
│                                       certificate                            │
│ --domain       -d  TEXT               Domain of the certificate, replaces    │
│                                       the current list. Can be repeated      │
│ --method       -m  [dns_core|manual]  Method (provider) to issue and manage  │
│                                       the certificate                        │
│ --cert             FILENAME           PEM certificate or full chain file     │
│ --key              FILENAME           Unencrypted PEM private key file       │
│ --help                                Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯
```
