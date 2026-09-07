# Реестр физических первоисточников

[Железо](hardware.ru.md) · [Роадмап](roadmap.ru.md) · [English](physical-source-register.md)

Это сохранённый реестр концепта H1, а не текущий перечень нативных компонентов H6.
Замены и исключения R2 применяет [модель концепта H1](h1-r2-physical-layout.ru.md);
текущую геометрию и открытые вопросы показывают [нативные виды H6](h6-r2-component-views.ru.md) и [проверка интерфейсов](h6-r2-interface-review.ru.md).
Каждому корпусу исторического реестра соответствует machine-строка:
точный выбранный MPN (или явный TBD), подтверждённый производителем габарит,
именованная система координат, ориентация и направление интерфейса. Историческое закрытие H1
не подтверждает соответствие текущим PCB, не закрывает геометрию H6 и не разрешает производство;
проверки посадки, RF, акустики, тепла и обычной работы реальных деталей остаются отдельными.

| Покрытие | Результат |
|---|---:|
| Отрисованных физических экземпляров | 231 |
| Экземпляров с точным MPN | 231 |
| Экземпляров с явным MPN TBD | 0 |
| Blocker геометрии H1 | 0 |
| Received-sample gate H5 | 14 |

## Системы координат

| Система | Datum | Корпусов |
|---|---|---:|
| `display-assembly` | ER-TFT035IPS-6 + ER-TPC035-6 configured CTP-outline top-left, front view | 1 |
| `front-outer` | UI PCB top-left, viewed from the front/exterior | 31 |
| `rear-outer` | RF/power PCB top-left, viewed from the rear/exterior | 13 |
| `rf-inner` | RF/power PCB top-left, viewed from the rear/exterior | 148 |
| `rf-inner-route` | RF/power PCB top-left, viewed from the rear/exterior | 3 |
| `ui-inner` | UI PCB top-left, viewed from the front/exterior | 33 |
| `ui-inner-route` | UI PCB top-left, viewed from the front/exterior | 2 |

Полная таблица по каждому экземпляру хранится в
[`H1-physical-source-table.json`](../hardware/product-design/generated/H1-physical-source-table.json)
как историческая основа отрисовки, а не разрешение передвигать компоненты текущих PCB.
Единая front-facing проекция X/Y/Z записана в
[`H1-unified-coordinate-table.json`](../hardware/product-design/generated/H1-unified-coordinate-table.json).
