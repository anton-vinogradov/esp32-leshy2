# Реестр физических первоисточников

[Железо](hardware.ru.md) · [Роадмап](roadmap.ru.md) · [English](physical-source-register.md)

Каждый корпус на продуктовых видах генерируется из одной machine-строки:
точный выбранный MPN (или явный TBD), подтверждённый производителем габарит,
именованная система координат, ориентация и направление интерфейса. Blocker
геометрии H1 не осталось; проверка посадки, RF, акустики, тепла и ресурса
реальных деталей остаётся на H5.

| Покрытие | Результат |
|---|---:|
| Отрисованных физических экземпляров | 182 |
| Экземпляров с точным MPN | 182 |
| Экземпляров с явным MPN TBD | 0 |
| Blocker геометрии H1 | 0 |
| Received-sample gate H5 | 14 |

## Системы координат

| Система | Datum | Корпусов |
|---|---|---:|
| `display-adapter` | L2-DISP-ADP-001-A top-left, viewed from its panel-facing side | 2 |
| `display-assembly` | HMX035CTFT-001 screen-body top-left, front view | 1 |
| `front-outer` | UI PCB top-left, viewed from the front/exterior | 30 |
| `rear-outer` | RF/power PCB top-left, viewed from the rear/exterior | 13 |
| `rf-inner` | RF/power PCB top-left, viewed from the rear/exterior | 100 |
| `rf-inner-route` | RF/power PCB top-left, viewed from the rear/exterior | 3 |
| `ui-inner` | UI PCB top-left, viewed from the front/exterior | 31 |
| `ui-inner-route` | UI PCB top-left, viewed from the front/exterior | 2 |

Полная таблица по каждому экземпляру хранится в
[`H1-physical-source-table.json`](../hardware/product-design/generated/H1-physical-source-table.json)
и является детерминированным входом для отрисовки, ревью и переноса в ECAD.
Единая front-facing проекция X/Y/Z записана в
[`H1-unified-coordinate-table.json`](../hardware/product-design/generated/H1-unified-coordinate-table.json).
