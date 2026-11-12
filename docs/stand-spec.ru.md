# Спецификация стенда

Для более сложных случаев, когда нужно запустить установку с несколькими узлами (которые рассматриваются как физические узлы), вы можете использовать `спецификацию стенда`. Спецификация стенда — это YAML-файл, описывающий установку Exordos — сколько узлов инициализации, сколько физических узлов, их характеристики и другие параметры.

Используйте опцию `--stand-spec` или `-s` для команды `bootstrap`, чтобы указать файл с описанием стенда:

```sh
exordos bootstrap -i output/exordos-core.raw -f -m core -s data/stands/stand-small.yaml
```

## Формат

Поле | Описание
---|---
`name` | Имя стенда (используется как префикс для созданных ВМ)
`bootstraps` | Список узлов инициализации. Каждая запись определяет `memory` (МБ) и `cores`
`baremetals` | Список физических узлов. Каждая запись определяет `name`, `memory` (МБ) и `cores`

## Пример

```yaml
name: dev-andromeda
bootstraps:
  - memory: 2048
    cores: 2
baremetals:
  - name: node-alpha
    memory: 2048
    cores: 2
  - name: node-beta
    memory: 2048
    cores: 2
```

Этот стенд создает один узел инициализации и два физических узла, каждый с 2 ГБ ОЗУ и 2 ядрами CPU.

## Настройки гипервизора при bootstrap

Параметры планирования начального гипервизора задаются при bootstrap Core:

```console
exordos bootstrap --inventory <inventory> --launch-mode core \
  --hyper-name compute-host --hyper-cores-ratio 4 --hyper-ram-ratio 1.5
```

Также доступны `--hyper-description`, `--hyper-avail-cores` и
`--hyper-avail-ram` (МБ). Коэффициенты должны быть неотрицательными; если их не
задать, Core использует `1.0`. Опции работают с обоими режимами
`--pool-agent-placement`: `core` и `local`.

При `--stand-spec` задавайте `name`, `description`, `avail_cores`, `avail_ram`,
`cores_ratio` и `ram_ratio` в записях `hypervisors`. Спецификация стенда имеет
приоритет над CLI-опциями гипервизора. Существующие пулы пропускаются по URI
подключения; bootstrap не обновляет их настройки.

Образ Core также должен поддерживать новые поля bootstrap: обновить нужно и
CLI, и Core.
