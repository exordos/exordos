# Adding and installing a new realm

## Adding and installing a new realm as current realm

```console
exordos settings set-realm <realm_name> \
  --endpoint <endpoint_url> \
  --check_updates \
  --current
```

Example:

```console
exordos settings set-realm production --endpoint http://10.40.0.2:11010 --current
```

## Adding and installing a new realm without setting it as current realm

```console
exordos settings set-realm <realm_name> \
  --endpoint <endpoint_url> \
  --check_updates \
  --skip_tls_verify
```

Example:

```console
exordos settings set-realm production --endpoint http://10.40.0.2:11010
```

## Get current realm

```console
exordos settings current-realm
```

## List all realms

```console
exordos settings list-realms
```

Example:

```console
user@user:~$ exordos settings list-realms
default:
  check_updates: true
  contexts:
    admin:
      password: admin
      user: admin
  current-context: admin
  endpoint: http://10.20.0.2:11010
production:
  check_updates: true
  endpoint: http://10.40.0.2:11010
  skip_tls_verify: true
```

## Set current realm

```console
exordos settings use-realm production
```

## Display exordos settings

```console
exordos settings view
```

Example:

```console
user@user:~$ exordos settings view
current-realm: production
endpoint: http://10.20.0.2:11010
realms:
  default:
    check_updates: true
    contexts:
      admin:
        password: admin
        user: admin
    current-context: admin
    endpoint: http://10.20.0.2:11010
  production:
    check_updates: true
    endpoint: http://10.40.0.2:11010
    skip_tls_verify: true
schema_version: 1
```

## Set authorization context

```console
exordos settings set-context <context_name> \
  --user <user> \
  --password <password> \
  --access_token <access_token> \
  --refresh_token <refresh_token> \
  <realm_name>
```

Example:

```console
exordos settings set-context --name "Admin Token" --access_token "...56riyO2U_gMjfYDwg" \
  --refresh_token "...bZ1BENYKg" City
```

## Bootstrapping a managed realm

When running `exordos bootstrap --realm-spec /etc/exordos/realm_spec.json`,
the CLI reads the element names and repository URL from the realm spec:

```json
{
  "elements": ["exordos_s3", "exordos_db"],
  "repo_url": "https://repository.example.com/exordos-elements/"
}
```

Explicit `--elements` options replace the list from the realm spec.
If the field is absent or contains an empty list, the default bootstrap is used.

A non-empty `repo_url` is added to the bootstrap repositories.
Existing repositories, including those specified with `--repository`, are
preserved. If the exact URL is already in the list, it is not added again.
An absent or empty `repo_url` leaves the repository list unchanged.
