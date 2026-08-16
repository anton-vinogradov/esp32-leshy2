# FND-0051 — legacy display connector and throughput do not match real modules

- Статус: **Несоответствие локализовано; target correction ждёт `IMP-0036`**
- Дата: 2026-08-17
- Обнаружено: exact display/touch/storage pass
- Evidence: [`DSP-0001`](../architecture/DSP-0001-display-storage-real-device-evidence.md)

## Несоответствия

1. Legacy J_LCD использует `C19273968`, реальный 24-position 0.5-mm
   bottom-contact FPC connector, но его 24-pin display mapping был
   предположением. Ближайший 4-inch exact module `DLS31040B1` имеет 14-pin
   interface; проверенный Waveshare 3.5-inch — 15/18-pin.
2. Старый candidate traffic budget требует 10 полных `320×480 RGB565` кадров
   в секунду и measured payload `≥4.5 MB/s`.
3. ST7796S, стоящий в обоих доступных low-cost module references, задаёт
   `66 ns` minimum serial write cycle: максимум `15.15 Mbit/s`/`1.89 MB/s` до
   overhead, то есть не более 6.16 ideal full frames/s.
4. Встроенный TF у обоих carrier modules использует общий SPI. Он не является
   электрически эквивалентной заменой отдельного SDMMC storage path.

## Выполненное исправление

- legacy connector/pinout не переносится в active machine-readable maps;
- три точных display boundaries и один exact microSD socket добавлены в
  `devices.json` со всеми реально выведенными contacts;
- active `SRC-0002` больше не говорит, что real display/microSD devices вообще
  не исследованы: открыт именно target/performance выбор;
- historical budget остаётся evidence snapshot, но его display row явно не
  разрешено использовать как current qualification gate.

## Что нельзя исправить автоматически

Нельзя одновременно объявить обязательными low-pin ST7796S и 10 full frames/s.
Это продуктово-архитектурный tradeoff: либо перейти к task/dirty-rectangle
acceptance, либо сохранить full-frame ceiling и заново выделить GPIO/стоимость
под QSPI/parallel/smart-display path. Решение вынесено в `IMP-0036`.
