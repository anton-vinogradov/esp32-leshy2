# DEC-0052 — direct QSPI display path on S3

> Последующее решение `DEC-0053` принимает 3.5-inch portrait `320×480` IPS
> QSPI+touch class, не меняя эту pin/resource allocation.

- Статус: **Принято владельцем; распространение проведено ревью**
- Дата: 2026-08-17
- Выбранный вариант: `IMP-0044/A`
- Основание: прямой ответ владельца «давай» на предложение QSPI-first
- Evidence: [`DSP-0002`](../architecture/DSP-0002-fast-display-path-options.md)
- Review: [`REV-0004X`](../reviews/REV-0004X-qspi-display-decision-propagation.md)

## Решение

1. Baseline display owner остаётся ESP32-S3; новый MCU не добавляется.
2. Working map получает direct 4-bit QSPI display на S3 SPI2:
   `GPIO35=SCK`, `GPIO36=D0`, `GPIO4=D1`, `GPIO41=D2`, `GPIO42=D3`,
   `GPIO38=CS_N`. Current `GPIO39` сохраняется display-control reserve до
   выбора exact controller, `GPIO40` — backlight PWM.
3. microSD остаётся 1-bit SPI client того же SPI2 с отдельным CS. Общая D1/
   MISO допустима только при доказанном CS-high high-Z обоих clients,
   корректном per-device mode switching и отсутствии contention/back-power.
4. Fixed `256 B` display quantum отменяется. Новый arbitration baseline —
   `<=1 ms` непрерываемого владения SPI2 одной display transaction; byte
   quantum выводится из измеренной datasheet-valid скорости exact panel.
5. `GPIO43` не занимается TE заранее. TE добавляется только если exact panel
   его выводит и HIL доказывает пользу; `GPIO6` остаётся direct reserve.
6. BT817/BT818 EVE остаётся fallback после измеренного провала direct QSPI или
   принятого расширения UI. Четвёртый MCU допустим только после провала обоих
   путей либо изменения product scope на video/high-animation class.

## Последствия

- S3 budget меняется с `29 used / 3 reserved / 4 free` на `31/3/2`;
- RP/C5 radio ownership, IPC, slow plane и RF concurrency не меняются;
- exact size, controller, touch, brightness, optics, mechanics and production
  MPN этим решением не выбираются;
- accepted menu/waterfall task thresholds и microSD throughput/stall gates
  сохраняются;
- `DEC-0043` остаётся историческим основанием task-based rendering, но его
  shared-U214 `256 B` clause superseded настоящим решением.
