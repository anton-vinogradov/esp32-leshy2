# DEC-0043 — task-based display performance

> Последующее решение: `DEC-0052` сохраняет task/dirty-region contract, но
> заменяет исторический shared-U214 лимит `256 B` на direct-QSPI path и
> measured `<=1 ms` display occupancy. Текст ниже фиксирует принятое на тот
> момент состояние.

- Статус: **Принято владельцем; распространение проведено ревью**
- Дата: 2026-08-17
- Выбранный вариант: `IMP-0036/A`
- Основание: прямой ответ владельца «да» после проверки, что продукту нужны
  waterfall из малых обновлений и меню, а не video/full-screen animation

## Решение

Display path квалифицируется по наблюдаемым задачам продукта, а не по
унаследованному требованию `10 full-frame-equivalents/s`. Baseline остаётся
low-pin write-only SPI + I²C touch с dirty-rectangle/tiled renderer. Точный
размер, панель, touch и production MPN этим решением не выбираются.

Обязательный acceptance contract:

1. critical safety/fault/actual-TX state начинает отображаться не позднее
   `100 ms` после принятого изменения product state;
2. обычное действие меню получает первый видимый отклик не позднее `100 ms`,
   а длительная работа показывает progress и не создаёт немого stall;
3. waterfall обновляет только новые строки/столбцы/области; renderer может
   coalesce визуальные обновления, но каждый пропуск считает и показывает, а
   raw radio/audio capture не теряется ради перерисовки;
4. display traffic всегда preemptible, не нарушает radio/audio/storage/safety
   deadlines и проверяется при худшей admitted concurrent load;
5. полный redraw измеряется и публикуется как HIL result, но не является
   периодической product workload или самостоятельным qualification gate;
6. отдельный SDMMC path сохраняется, пока shared-SPI storage не докажет без
   потерь те же throughput, stall, hot-removal и fault-isolation свойства.

Когда display делит SPI с U214, максимальный непрерываемый pixel quantum равен
`256 B`, а accessory IRQ-to-first-transfer должен оставаться `≤250 µs` при
паспортной частоте выбранной панели. Это исправляет прежнее несовместимое
сочетание `≤1 KiB` и `≤250 µs`: для ST7796S 1024 B занимают около `541 µs`
даже без protocol/software overhead.

## Последствия

- ST7796S references больше не исключаются искусственным full-frame budget;
- текущий S3 low-pin envelope не расширяется до QSPI/8080/RGB/EVE без
  фактического провала scenario HIL;
- exact panel/optics/mechanics и measured shared-bus behavior остаются
  открытыми G2F/G3 gates;
- провал любого accepted task threshold автоматически переоткрывает interface
  choice и complete pin/power/cost comparison, а не скрывается firmware tuning.

Ни одна exact display module этим решением не получает target/Q status.
