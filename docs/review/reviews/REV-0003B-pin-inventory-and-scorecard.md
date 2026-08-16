# REV-0003B — ревью MCU pin/controller inventory и layout scorecard
> **Историческая запись ревью.** `DEC-0027` архивировал её stage-3 architecture outputs; этот документ не является активным пререквизитом zero-based synthesis.


- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3 — системная архитектура и владение
- Входы: `DM-0001`, official S3/C5 module documentation, legacy tsCircuit allocation
- Выходы: `PIN-0001`, `SC-0001`, `FND-0029`

## Проверки

| Проверка | Результат |
|---|---|
| Exact modules | N8R2/N*R8 S3 и N8R8 C5 memory/pin effects отделены; generic module не используется как доказательство |
| Exposed pins | доступные GPIO, straps, fixed USB/SDIO и unavailable PSRAM pins записаны до layout allocation |
| Controllers | единственный C5 GP-SPI, fixed SDIO, S3 GP-SPI/I²S/SDMMC и C5 RMT ceiling внесены в hard constraints |
| Legacy pressure | проверено, что текущий S3 artifact использует все exposed pins; освобождение onboard part не выдаётся за свободный accessory signal |
| Transport/recovery | GP-SPI, 1-bit SDIO, 4-bit SDIO и UART разведены по pin/recovery/nRF24 consequences |
| Wishlist preservation | scorecard hard-fails потерю любой frozen capability, включая три full-function nRF24 и dual-path C5 IR |
| Safety | independent STOP и actual-TX являются отдельными hard-fail gates |
| Comparable layouts | один demand revision, одна 100-point шкала и одинаковые evidence rules обязательны для S3-heavy, C5-heavy и balanced |
| Premature scoring | scores запрещены до numeric traffic/memory/power и STOP completion |

## Найденное несоответствие

Предварительные предложения независимо считали доступными преимущества 8 MB Octal PSRAM S3, legacy `GPIO35..37` transport, 4-bit C5 SDIO, native C5 USB recovery и свободный C5 GP-SPI. Вместе эти свойства несовместимы. Несоответствие зафиксировано как `FND-0029`; ни один layout не сможет скрыть его weighted score.

## Вывод

Инвентаризация исходных pin/controller фактов и структура сравнения получили статус **«Проведено ревью»**. Это не выбирает module variant, transport или владельца 3×nRF24. `DM-0001` остаётся в работе до численных envelopes и решения по независимому STOP.
