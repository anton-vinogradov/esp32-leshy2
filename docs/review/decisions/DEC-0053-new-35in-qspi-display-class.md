# DEC-0053 — 3.5-inch portrait QSPI display class

- Статус: **Принято владельцем — IMP-0045/A; распространение проведено ревью**
- Дата: 2026-08-17
- Основание: [`IMP-0045`](../improvements/IMP-0045-new-35in-qspi-display-class.md)
- Evidence: [`DSP-0003`](../architecture/DSP-0003-exact-fast-display-shortlist.md) /
  [`DSP-0004`](../architecture/DSP-0004-display-part-number-register.md)
- Review: [`REV-0004Z`](../reviews/REV-0004Z-display-class-decision-propagation.md)

## Решение

1. Product target — **3.5-inch portrait `320×480` IPS, direct QSPI и
   capacitive touch**. Это принятый класс экрана, а не выбранная целиком
   отладочная плата.
2. Primary HIL — Elecrow/QDtech `DLE06235B` / `ES3C35P` с `ST77922`.
3. Secondary HIL — Waveshare `ESP32-S3-Touch-LCD-3.5B`, SKU `31137`, с
   `AXS15231B`.
4. Старый 4-inch Elecrow `DLS31040B1/DLS31040B2`, touch-вариант `MSP4031`,
   с `ST7796S` и `FT6336U` сохраняется как A0 workload/control fixture и
   дешёвый fallback, но не является production target.
5. 4-inch/4.3-inch EVE modules остаются high-end fallback, если direct-QSPI
   HIL не выполнит принятые требования.

## Что ещё не выбрано

Production status не получает ни одна dev board. До закупочного и HIL gate
остаются открыты точные MPN дисплейной сборки, FPC/board connector, touch
implementation, backlight driver, ESD/protection, cover lens, brightness и
optical stack. Реестр известных и отсутствующих обозначений находится в
`DSP-0004`; отсутствие опубликованного MPN обозначается `TBD`, а не заменяется
названием controller IC.

## Почему это не преждевременный BOM freeze

- `DEC-0052` уже требует direct QSPI; новый класс реализует его без отдельного
  display coprocessor и без возврата к 1-bit SPI.
- Два разных controller/HIL reference уменьшают firmware и sourcing risk, но
  не доказывают interchangeability raw panels.
- Active area нового класса примерно на 23% меньше старого 4-inch reference.
  Читаемость, waterfall density и glove/control geometry обязаны пройти
  адаптированный physical mockup до фиксации корпуса.

## Последствия

- S3 principled pinout `DEC-0052` не меняется.
- Firmware может планировать два prototype driver profiles — `ST77922` и
  `AXS15231B` — но production init table определяется только точной панелью.
- Physical design использует 3.5-inch portrait window как текущий target input
  и сохраняет возможность вернуться к A0/EVE fallback при измеренном провале.
