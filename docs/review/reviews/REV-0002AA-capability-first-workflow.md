# REV-0002AA — ревью capability-first порядка до компоновки

- Статус: **Проведено ревью процесса; wishlist ещё не заморожен**
- Дата: 2026-08-16
- Вход: указание владельца «сначала все хотелки, потом бюджет ног и варианты компоновки»
- Выходы: `DEC-0022`, `INV-0002`

## Проверено

| Проверка | Результат |
|---|---|
| Полнота исходного импорта | `INV-0001` содержит 118 legacy leaf rows + 3 UX + 4 hardware-road candidates = 125 |
| Owner additions | принятые пожелания из текущей проработки собраны отдельно |
| Extras | технически возможные, но не запрошенные функции вынесены в `W-EXTRA-*` |
| Разделение concern | функции отделены от MCU owner, transport, GPIO, decoder/latch и layout |
| nRF24 | full-function invariant сохраняется; `IMP-0021` отложен как layout candidate |
| UI/STOP/audio | `IMP-0010` не возвращается на решение до wishlist freeze |
| Stage gate | этап 3 требует owner-confirmed wishlist freeze и единый demand model |
| Product README | не меняется: процесс и открытые варианты не являются свойствами готового продукта |

## Итог

Процесс проведён ревью. Следующая работа — не pin budget, а завершение всех capability slices и явных owner-extra решений в `INV-0002`. Статус `INV-0002` остаётся **«В работе; список не заморожен»**.
