# Конфигурация для exordos cli

Путь по умолчанию для файла конфигурации: `~/.exordos/exordosctl.yaml`

Пример конфигурации:

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
developer_key_path: ~/.ssh/id_rsa.pub
```

Вы можете изменить путь к файлу конфигурации, установив аргумент командной строки `--config`.

Пример:

```bash
exordos --config ~/.exordos.yaml elements list
```

## Реалмы

Реалмы используются для разделения сред. Например, у вас могут быть производственная и разработческая среды.

См. страницу [реалмы](realms.ru.md) для получения дополнительной информации.

## developer_key_path

Путь к вашему SSH-ключу.

Вы можете изменить путь к SSH-ключу через конфигурацию или установив аргумент командной строки `--developer_key_path` или `-i`
или через переменную окружения `GEN_DEV_KEYS`.

## Инициализация

Вы можете интерактивно инициализировать файл конфигурации, выполнив следующую команду:

```bash
exordos settings init
```
