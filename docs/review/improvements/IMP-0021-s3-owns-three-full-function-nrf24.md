# IMP-0021 — перенести целевое владение 3× полнофункциональных nRF24 на S3

- Статус: **⚠️ Предложение — сравнительный вход единого architecture package; отдельно не принимается (`DEC-0026`)**
- Связано: `DEC-0001`, `DEC-0009`, `DEC-0021`, `FND-0001`, `FND-0019`, `FND-0028`, `AUD-0003`, `REQ-N24-0001`
- Цена: без нового MCU/radio; conditional small CE-latch BOM и HIL
- Дата: 2026-08-16

## Контекст

Старое C5 ownership было принято до доказательства pin/transport architecture. Теперь установлено, что C5 имеет один GP-SPI и legacy назначает его двум ролям. S3 имеет два GP-SPI, уже физически связан с nRF24, владеет UI/storage/security parsing и baseline BLE. При этом все три nRF24 должны остаться полнофункциональными, а не общим синхронным блоком.

`AUD-0003` показывает реализуемый S3-профиль без отъёма I²S ES8311: IR остаётся C5; C5 UART flash bridge удаляется только после доказательства собственного C5 USB recovery; GPIO2/42/43/44 используются для I²S; текущие GPIO6/46 остаются nRF CE-control/IRQ. Независимые CE формирует reset-safe latch/expander, а CS уже независимы через 74HC138.

## Варианты

### A — S3 владеет всеми 3×nRF24, общий SPI2 (рекомендация)

- один S3 driver/scheduler и typed API для UI/storage;
- текущие SPI/CS/IRQ nets сохраняются, общий CE заменяется независимыми latched CE states;
- C5 сохраняет Wi-Fi/802.15.4 и dual-path IR, а существующий SPI3 transport больше не конфликтует с local nRF master;
- display/SD/CC1101/U214/nRF bus arbitration и worst-case capture loss проходят HIL до final pin/schematic acceptance;
- если shared-bus HIL не проходит, отдельный SPI performance-вариант возвращается без смены функционального требования.

### B — оставить все 3×nRF24 на C5

Требует переноса inter-MCU link на 1-bit SDIO, exact C5 revision и полной новой nRF routing. Даёт dedicated nRF SPI, но сильнее загружает GPIO C5, добавляет raw-frame IPC и больше NRE.

### C — split ownership

Не рекомендуется: две driver/state/calibration/STOP domains без принятой пользовательской задачи.

## Что A не означает

- IR не возвращается на S3;
- BLE-compatible subset не заменяет полный native nRF feature set;
- общий SPI не объявляется lossless без измерения;
- UART bridge не удаляется до доказанного C5 USB/BOOT/RESET recovery;
- CE-latch part и final pin numbers не принимаются этим scope-решением — они проходят stage-3 comparison/HIL.

## Предварительная рекомендация

После wishlist freeze сравнивать A как основной S3-heavy кандидат. На текущем известном составе он снимает single-GP-SPI blocker C5 с меньшей переделкой и меньшим IPC, сохраняя три полнофункциональных radio. Вывод должен быть пересчитан на полном demand model и остаётся conditional на consolidated resource budget и shared-bus latency/loss HIL.

## Результат полного static comparison

`DEC-0023` заморозил wishlist, а `LAY-S3-0001`, `LAY-C5-0001`, `LAY-BAL-0001` и `CMP-0001` пересчитали варианты на полном `DM-0001/BUD-0001`. Все три statically feasible; weighted scores запрещены до measurements/quotes. S3-вариант остаётся рекомендуемым conditional baseline: меньше irreducible BOM/reroute, нет raw nRF IPC, C5 сохраняет GPIO и native recovery margin.

## Приёмка

По `DEC-0026` отдельного вопроса о владельце nRF24 нет. Вариант A может войти только в целиком сведённый package, который одновременно фиксирует memory, transport, UI, pins, recovery, STOP/TX-state, coexistence и cost. До этого `LAY-S3`, `LAY-C5` и `LAY-BAL` остаются сравнительными черновиками.
