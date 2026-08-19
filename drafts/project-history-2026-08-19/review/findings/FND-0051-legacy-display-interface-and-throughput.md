# FND-0051 — legacy display connector and throughput do not match real modules

- Статус: **Несоответствие исправлено `DEC-0043`; exact target остаётся открыт**
- Дата: 2026-08-17
- Обнаружено: exact display/touch/storage pass
- Evidence: [`DSP-0001`](../architecture/DSP-0001-display-storage-real-device-evidence.md)
- Correction: [`DEC-0043`](../decisions/DEC-0043-task-based-display-performance.md)

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

## Принятое исправление target contract

Владелец выбрал task/dirty-rectangle acceptance в `DEC-0043`. Унаследованные
10 full frames/s и 4.5 MB/s больше не являются target gates. Critical/menu
first response проверяется в пределах 100 ms, waterfall и progress используют
малые preemptible regions, а полный redraw публикуется только как HIL result.

Дополнительная арифметическая проверка нашла, что прежний `≤1 KiB` display
quantum также не совместим с U214 wait `≤250 µs`: на максимальной паспортной
скорости ST7796S он занимает около `541 µs` без overhead. Нормативный shared-bus
quantum исправлен на `≤256 B` с measured IRQ-to-first-transfer gate `≤250 µs`.
