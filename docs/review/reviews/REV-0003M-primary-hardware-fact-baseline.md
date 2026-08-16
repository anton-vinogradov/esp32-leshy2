# REV-0003M — ревью primary hardware fact baseline

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, фактологический gate перед `SYN-*`
- Артефакт: `SRC-0001`

## Проверка

| Gate | Результат |
|---|---|
| Source quality | MCU/module/peripheral facts ссылаются на текущую manufacturer documentation |
| Package reality | SoC GPIO не смешаны с module-exposed pins; memory-reserved pins исключаются |
| Coupled resources | S3 PSRAM/GPIO, C5 SDIO/USB/revision и RMT/IR пересечения явны |
| Radio semantics | nRF24 и CC1101 разложены до bus/select/control/event obligations без owner assignment |
| External profiles | U214, Unit GPS и Unit NFC учтены вместе с полным signal/power profile |
| Search breadth | дополнительный controller разрешён к сравнению; S3/C5-only assumption не наследуется |
| Open-product boundary | optional ROM lockdown не подменяет owner-controlled signed updates/recovery |
| Legacy independence | прежние owner, transport, GPIO и named layout axes не использованы |
| Decision hygiene | module variant, controller count, buses, pins и architecture winner не выбраны преждевременно |

## Итог

`SRC-0001` отделяет проверяемые физические факты от вариантов компоновки и получает статус **«Проведено ревью»**. Теперь `SYN-*` могут быть построены с нуля из `CAP/CON/RES`, но обязаны инстанцировать именно package-level ограничения `SRC-0001`, а не номинальные возможности SoC или legacy source.
