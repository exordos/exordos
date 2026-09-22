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
        - path: configs/my-config.yaml
        - path: templates/my-template.yaml
```

### Артефакты, полученные скриптом

Вместо прямого указания на файл артефакт может запускать скрипт (или любой
исполняемый файл). Скрипт выполняется с текущим каталогом `work_dir`, а после
его завершения вложенный список `artifacts` (шаблоны glob, относительно
`work_dir`; поддерживается как минимум символ `*`) отбирает полученные файлы.
Если найденный элемент — каталог, он архивируется через `tar` и сжимается
через `zstd` (например, найденный каталог `dist/` станет `dist.tar.zst`);
файлы копируются как есть. Все пути (`script`, `work_dir`) указываются
относительно файла `exordos.yaml`.

```yaml
      artifacts:
        - script: images/docs_build.sh
          work_dir: ../
          artifacts:
            - dist/
```

### Ссылки на артефакты в шаблонах манифестов

Статическим и скриптовым артефактам можно задать имя через поле `name`.
Именованный артефакт доступен в шаблонах манифестов Jinja2 через
`{{ artifacts.<name> }}` и рендерится в URN артефакта
(`urn:artifacts:<uuid>`):

```yaml
      artifacts:
        - path: packages/my_package.whl
          name: pip_package
```

В шаблоне манифеста:

```jinja
  $metapaas.types:
    victoria:
      package: "{{ artifacts.pip_package }}"
```

После рендеринга:

```yaml
  $metapaas.types:
    victoria:
      package: "urn:artifacts:<uuid>"
```

Именованный артефакт должен давать ровно один файл. Если шаблоны glob
скрипта совпадают с несколькими файлами, возникает ошибка сборки, так как
соответствие имени и URN становится неоднозначным.

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
  company:
    driver: nginx                     # nginx-сервер с включённым WebDAV
    url: https://repo.example.com
    auth: [user, password]            # опциональный basic auth
```

Для отправки в конкретный целевой объект передайте файл конфигурации с
флагом `-c` и укажите цель через `-t`, если их в файле несколько:

```bash
exordos push -c exordos/exordos.push.yaml -t company
```

### Репозиторий реалма

У каждого проекта в реалме есть свой репозиторий, запись в который идёт с
токеном core IAM текущего пользователя. Цель push для него не нужна:
укажите проект в контексте реалма в `~/.exordos/exordosctl.yaml`

```yaml
realms:
  my_realm:
    endpoint: https://my-realm.example.com/api/core
    contexts:
      developer:
        user: developer
        project_id: 7d3b5c1e-2f4a-4b8e-9c6d-0a1b2c3d4e5f
    current-context: developer
current-realm: my_realm
```

и выполните push с `--realm-repo`:

```bash
exordos push --realm-repo
# или для другого проекта того же реалма
exordos --project-id 7d3b5c1e-2f4a-4b8e-9c6d-0a1b2c3d4e5f push --realm-repo
```

Элементы попадают в `https://my-realm.example.com/repo/<project_id>/`, и
реалм сразу подхватывает их в репозитории проекта `internal`.
