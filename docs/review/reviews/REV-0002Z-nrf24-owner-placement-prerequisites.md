# REV-0002Z — ревью пререквизитов повторного выбора владельца 3×nRF24

- Статус: **Проведено ревью пререквизитов**
- Дата: 2026-08-16
- Этап: 2→3 ownership prerequisite
- Входы: owner full-function clarification, actual source/net map, accepted audio/IR/BLE/U214 contracts, S3/C5/nRF24/U214 primary sources
- Выходы: `FND-0028`, `AUD-0003`, `IMP-0021`

## Проверено

| Область | Результат |
|---|---|
| Legacy C5 owner | не доказан; единственный C5 GP-SPI конфликтует с SPI inter-MCU link |
| Full-function | общий CE недостаточен; требуются независимые logical CE states и per-radio sessions |
| S3 peripherals | два GP-SPI; текущая physical nRF routing; UI/storage/security parsing локальны |
| S3 pins | conditional fit найден: IR C5 освобождает 2/42, доказанное удаление redundant C5 flash UART освобождает 43/44 для четырёх I²S; nRF control остаётся 6/46 через CE latch+IRQ combiner |
| U214 intersection | SPI/UART/IRQ/BUSY/RST остаются заняты внешним Cap и не названы free pins |
| C5 fallback | возможен только с новым SDIO transport/revision/pin proof; tighter and higher-NRE |
| Bus performance | S3 shared SPI — основной открытый риск; сформированы bounded-chunk/loss/latency/HIL criteria |
| Cost | S3 preliminarily minimizes reroute/IPC/BOM; no zero-loss claim before HIL |

## Итог

Пререквизиты проведены ревью. `DEC-0001` остаётся исторически принятым, но его nRF24 ownership переоткрыто и не может считаться окончательным входом stage 3. На известном в момент аудита составе `IMP-0021/A` является предварительно сильнейшим S3-heavy кандидатом. Последующее `DEC-0022` откладывает решение: сначала замораживается полный реестр хотелок, затем S3-heavy, C5-heavy и balanced/modular компоновки сравниваются на одном demand model.
