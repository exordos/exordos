# Файл конфигурации Exordos

Файл `exordos.yaml` содержит конфигурацию для проекта Exordos. Он должен быть помещен в каталог `exordos` в корне проекта. Он состоит из нескольких разделов, таких как `build`, `deploy` и т.д.

## Структура проекта

Для каждого проекта Exordos в корне проекта должен существовать каталог `exordos`:

```sh
.
├── my_project
│   └── main.py
├── exordos
│   └── exordos.yaml
├── pyproject.toml
└── README.md
```

## Пример конфигурации сборки

```yaml
# Раздел сборки. Описывает процесс сборки проекта.
build:
  # Зависимости проекта
  # Этот раздел используется для указания зависимостей сборки
  # для проекта
  deps:
      # Целевой путь в образе
    - dst: /opt/exordos_core
      # Локальный путь на машине сборки
      path:
        src: ../../exordos_core
  
  # Этот раздел описывает элементы проекта.
  # Образы, артефакты и манифесты для каждого элемента.
  elements:
      # Список образов в элементе
    - images:
      - name: exordos-core
        format: raw
        
        # Профиль ОС для образа
        profile: ubuntu_24

        # Скрипт настройки
        script: images/install.sh

        # Переопределить параметры сборки образа, например параметры Packer
        override:
          disk_size: "10G"

      manifest: manifests/exordos-core.yaml
      
      # Список артефактов в элементе
      artifacts:
        - configs/my-config.yaml
        - templates/my-template.yaml
```

## Файл конфигурации push

Конфигурация push хранится в отдельном файле — `exordos.push.yaml` — расположенном рядом с `exordos.yaml` в каталоге `exordos`. Она определяет один или более именованных целевых объектов push, каждый из которых указывает драйвер и целевой путь.

### Формат

```yaml
push:
  <target_name>:
    driver: <driver>   # например, "fs" для репозитория локальной файловой системы
    path: <path>       # целевой путь для собранных артефактов
```

### Пример

```yaml
push:
  local:
    driver: fs
    path: /var/lib/exordos-pools/http
```

Для отправки в конкретный целевой объект передайте файл конфигурации с флагом `-c`:

```bash
exordos push -c exordos/exordos.push.yaml
```
