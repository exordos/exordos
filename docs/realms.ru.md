# Добавление и установка нового реалма

## Добавление и установка нового реалма как текущего

```console
exordos settings set-realm <realm_name> \
  --endpoint <endpoint_url> \
  --check_updates \
  --current
```

Пример:

```console
exordos settings set-realm production --endpoint http://10.40.0.2:11010 --current
```

## Добавление и установка нового реалма без установки в качестве текущего

```console
exordos settings set-realm <realm_name> \
  --endpoint <endpoint_url> \
  --check_updates \
  --skip_tls_verify
```

Пример:

```console
exordos settings set-realm production --endpoint http://10.40.0.2:11010
```

## Получить текущий реалм

```console
exordos settings current-realm
```

## Список всех реалмов

```console
exordos settings list-realms
```

Пример:

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

## Установить текущий реалм

```console
exordos settings use-realm production
```

## Отобразить настройки exordos

```console
exordos settings view
```

Пример:

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

## Установить контекст авторизации

```console
exordos settings set-context <context_name> \
  --user <user> \
  --password <password> \
  --access_token <access_token> \
  --refresh_token <refresh_token> \
  <realm_name>
```

Пример:

```console
exordos settings set-context --name "Admin Token" --access_token "...56riyO2U_gMjfYDwg" \
  --refresh_token "...bZ1BENYKg" MyTown
```
