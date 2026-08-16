# REV-0003D — ревью traffic и memory envelope

- Статус: **Проведено ревью подшага; power позднее закрыт `REV-0003E`**
- Дата: 2026-08-16
- Входы: `DM-0001`, `PIN-0001`, `SCN-01..08`, official component ceilings
- Выходы: `BUD-0001`, `FND-0030`, `IMP-0023`

## Проверки

| Проверка | Результат |
|---|---|
| Display math | 320×480 RGB565 = 307,200 B; 3.2 MB/s/full-frame ≤100 ms boundary записан |
| Radio ceilings | 3×nRF24, CC1101 и U214 on-air ceilings не выданы за lossless capture; SPI/service margins добавлены |
| IPC | bulk directions, burst, control latency и 100 ms stale-lease cancellation разделены |
| Storage/audio | SD sustained floor, bounded stalls и 48 kHz mono full-duplex demand заданы раздельно |
| Bus arbitration | 30% headroom, ≤70% occupancy и bounded non-preemptible chunk обязательны каждому layout |
| S3 memory | common/SCN overlay accounting сохраняет N8R2 только при measured 1,920 KiB usable floor; N8R8 не выбран автоматически |
| C5 memory | PSRAM and internal-DMA floors заданы без использования внешней RAM там, где driver её не допускает |
| Update | dual-slot 3 MiB image class не требует full-image PSRAM staging и не удаляет rollback |
| Power audit | source-current table выявила 5 V→~1.5 W mismatch SA518; power не помечен reviewed до решения |

## Вывод

Traffic и memory подшаг получает статус **«Проведено ревью»**. На момент этого review layout generation ожидал `IMP-0023`; последующее `DEC-0025/REV-0003E` закрыло power/pack envelope и открыло layouts.
