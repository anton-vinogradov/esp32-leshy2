# REV-0003A — ревью пререквизитов единого demand model

- Статус: **Проведено ревью пререквизитов; сам `DM-0001` в работе**
- Дата: 2026-08-16
- Этап: 3 — системная архитектура и владение
- Входы: `DEC-0023`, `INV-0004`, `REV-0002AD`, все `REQ-*`, current findings

## Проверки

| Пререквизит | Результат |
|---|---|
| Этап 2 | **Проведено ревью** |
| Wishlist | 125/125 frozen; base/optional/deferred separated |
| nRF24 | full function fixed, physical owner explicitly open |
| Fixed owners | S3 native BLE/Wi-Fi, C5 Wi-Fi/802.15.4 and IR stated consistently |
| Safety | independent STOP, actual-TX, conservative power and three levels are hard demands |
| External modules | GNSS/U214/U216 are qualified profiles, not hidden onboard BOM |
| Known blockers | `FND-0001`, `FND-0006`, `FND-0007`, `FND-0019`, `FND-0028` carried into model |
| Layout neutrality | no GPIO, transport, decoder or nRF owner accepted by prerequisite review |

## Исправление до старта

Canonical `docs/contracts/ownership.md`, `DEC-0001` and `DEC-0019` still contained an effective C5-owner statement for nRF24 after ownership had been reopened. They were corrected before demand modelling: IR remains C5, while 3×nRF24 owner is open. Historical C5 placement remains a layout candidate, not an accepted target.

## Вывод

Пререквизиты этапа 3 достаточны. `DM-0001` начат; layouts cannot be scored until exact pin/controller, traffic/memory/power, STOP topology and hard-fail rubric are complete.
