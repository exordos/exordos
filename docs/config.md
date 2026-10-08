# Config for exordos cli

Default path for config file: `~/.exordos/exordosctl.yaml`

Example config:

```yaml
current-realm: default
realms:
  default:
    check_updates: true
    contexts:
      admin:
        password: admin
        user: admin
    current-context: admin
    endpoint: http://10.20.0.2:11010
  my_stand:
    check_updates: true
    contexts:
      base:
        password: my_password
        user: my_admin
    current-context: base
    endpoint: https://console.my_company.tech:80
  production:
    check_updates: true
    endpoint: http://10.40.0.2:11010
    skip_tls_verify: true
repositories:
  my-repo:
    driver: nginx
    url: http://repo.example.com:8080/
    auth: [user, pass]
  local-repo:
    driver: nginx
    url: http://10.20.0.2:8080/repo/
developer_key_path: ~/.ssh/id_rsa.pub
```

You can change the path to the config file by setting the command line argument `--config`.

Example:

```bash
exordos --config ~/.exordos.yaml elements list
```

## Realms

Realms are used to separate environments. For example, you can have production and development environments.

See the [realms](realms.md) page for more information.

## developer_key_path

The path to your ssh key.

You can change the path to the ssh key by config or by setting the command line argument `--developer_key_path` or `-i`
or by environment variable `GEN_DEV_KEYS`.

## Repositories

Repositories are used to store and distribute build artifacts. You can manage them in the config file under the `repositories` key, or by using the `exordos settings repo` commands.

### List repositories

```bash
exordos settings repo list
```

Show repositories in JSON format with sensitive data:

```bash
exordos settings repo list -o json --show-sensitive
```

### Add a repository

```bash
exordos settings repo add my-repo --driver nginx --url http://repo.example.com:8080/ --username user --password pass
```

The credentials are stored as `auth: [user, pass]` in the configuration file.

### Delete a repository

```bash
exordos settings repo delete my-repo
```

## Initialization

You can interactively initialize the config file by running the following command:

```bash
exordos settings init
```
