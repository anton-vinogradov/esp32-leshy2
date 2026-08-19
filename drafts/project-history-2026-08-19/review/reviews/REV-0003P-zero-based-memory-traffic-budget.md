# REV-0003P — ревью zero-based memory/traffic budget

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, шаг 5b
- Артефакт: `BUD-0002`

## Пререквизиты

| Gate | Результат |
|---|---|
| Zero-based input | использованы reviewed `CAP/CON/RES/SRC/SYN/PIN`; archived `BUD-0001` не является входом |
| Equal scenarios | три candidates проверены одним набором scenario/traffic/memory ceilings |
| Exact package coupling | S3 N16R2 проверен как 2 MiB PSRAM + сохранённые GPIO35…37; C5 N8R8 и RP2354A имеют отдельные budgets |
| Honest maxima | datasheet air/raw-bus ceilings отделены от admitted application guarantee |
| Full nRF semantics | три одновременных independent PRX и native modes сохранены; lossless 3× theoretical maximum не выдуман |
| Failure visibility | overflow/drop/source/age и admission failure обязательны; скрытое throttling запрещено |
| Update | S3/C5 retain two-image contract; RP2354 partition proof includes two signed slots and recovery |
| No premature winner | arithmetic results compare candidates but do not select architecture before power/RF/cost package |

## Проверенная арифметика

| Item | Result |
|---|---|
| S3 PSRAM floor | `896 + 512 + 384 = 1792 KiB` measured usable floor |
| reference display | `480×320×2 = 307,200 B`; `×10/s = 3.072 MB/s` |
| full-duplex mono audio | `48,000×2×2 = 192 kB/s` |
| nRF absolute screen | `3×2 Mbit/s÷8 = 750 kB/s` payload upper bound |
| nRF+CC impossible-screen bus | `750×1.20 + 75×1.25 = 993.75 kB/s = 79.5%` of 10 Mbit/s SPI |
| admitted 3×nRF bus | `600×1.20 = 720 kB/s = 57.6%` |
| mixed nRF+CC bus | `450×1.20 + 60×1.25 = 615 kB/s = 49.2%` |
| IPC gate | 1.5 MB/s measured payload ×70% = 1.05 MB/s admitted, above radio payload+metadata budget |

## Саморевью несоответствий

Старое интуитивное требование можно было прочитать как lossless simultaneous maximum всех четырёх packet radios. Оно не присутствует в reviewed wishlist/scenario contract и не поддерживается общей 10 Mbit/s шиной с 30% запасом. `BUD-0002` не удаляет full-function nRF: фиксирует independent controls/IRQ/FIFO/native modes, simultaneous PRX и 200 kB/s sustained payload на каждый radio, а превышение делает наблюдаемым.

Если именно принятый 600 kB/s aggregate target или deadline HIL не проходит, split ownership открывается автоматически. До такого измерения добавлять четвёртый layout было бы преждевременным.

## Итог

Все три candidates проходят paper memory и admitted-throughput gates. `SYN-2B` несёт максимальный C5 latency risk, `SYN-2A` — максимальный S3 contention risk, `SYN-3A` — дополнительный update/runtime target при минимальном scheduling risk. Эти различия переходят в power/RF/cost и затем в атомарное сравнение.

Числовая модель, пороги admission и восемь HIL gates получают статус **«Проведено ревью»**. Фактические hardware measurements остаются открытыми и не подменяются этим статусом.
