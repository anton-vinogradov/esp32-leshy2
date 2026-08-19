# DEC-0018 — двухтрактный consumer IR; former C5 implementation profile

- Статус: **Capability decision retained; exact C5 implementation superseded by `DEC-0095`**
- Источник: `IMP-0015`, вариант A
- Дата: 2026-08-16

## Решение

> Нормативно сохраняются robust ordinary receive и отдельный carrier-aware
> learning path. `DEC-0095/IRF-0001` later accept C5/RMT with exact
> `TSOP95238TT`, `TSMP95000TT`, `VSMY14940` and actual-optical evidence. The
> `TSOP38238/TSAL6200` names below remain the original comparison history, not
> the current target BOM.

Consumer IR получает два независимых RX-тракта, физически и программно принадлежащих ESP32-C5:

- `TSOP38238` — первый robust demodulated 38 kHz receiver для обычного дальнего/помехоустойчивого приёма;
- `TSMP95000` — отдельный carrier-out receiver для измерения несущей при обучении в доказанном диапазоне 30–60 kHz;
- оба RX RMT channel C5 резервируются под IR, один TX RMT channel — под формирование emitter waveform;
- `TSAL6200` — первый кандидат 940 nm emitter, но только вместе с квалифицированным logic low-side driver, hardware pull-down, current limit и доказанными duty/thermal/IEC 62471 limits.

Запись обучения хранит значение несущей и её provenance: `measured`, `protocol`, `database`, `imported` либо `manual`. Только выход learning path 30–60 kHz создаёт `measured`; огибающая `TSOP38238` не выдаётся за измеренную несущую.

## Границы

- Автоматическое обучение 455 kHz и других частот вне 30–60 kHz отложено до отдельного wideband/analog frontend proposal.
- Передача известного или импортированного out-of-band профиля возможна только после отдельного electrical/optical HIL конкретного carrier.
- `Universal remote` означает только corpus-proven профили, а не совместимость с любым оптическим оборудованием.
- Main содержит работу с собственным выбранным устройством; Lab — пассивный анализ; unknown replay и service/security codes требуют Controlled Zone `AUTHORIZED_TARGET`; TV-B-Gone, brute-force и multi-code sweep требуют `BOTH`.
- Точный MPN/revision/AVL, схема TX, оптическое окно, range/noise criteria, STOP, C5 pins, S3↔C5 transport и HIL остаются implementation gates.

## Ресурсы и стоимость

Вариант занимает оба RX RMT C5 и добавляет один GPIO, receiver, passives, площадь и общий optical window относительно single-RX схемы. Точная pin map принимается только на этапе 3 после сводного GPIO/resource budget. Если бюджет не помещает решение, вопрос возвращается владельцу: реализация не вправе молча перейти к варианту B или C.

Дополнительная стоимость принята ради одновременного сохранения robust ordinary receive и carrier-aware learning. Это функциональный компромисс, а не zero-loss экономия. На этапе BOM сравниваются exact AVL/quote и стоимость размещения/тестирования; удаление любого RX path требует нового owner decision.

## Последствия для артефактов

- `REQ-IR-0001` получает статус **«Проведено ревью»**.
- `FND-0018` закрывается на уровне требований.
- `FND-0017` остаётся открытой implementation finding до доказательства целевой C5-схемы, safe state, STOP и optical HIL.
- Stage 3 обязан включить оба RX GPIO/RMT и TX RMT в единый ресурсный бюджет вместе с 3×nRF24 и межпроцессорным транспортом.

## Первичные источники

- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP-IDF RMT API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/peripherals/rmt.html)
- [Vishay TSOP382/384 datasheet](https://www.vishay.com/docs/82491/tsop382.pdf)
- [Vishay TSMP95000 datasheet](https://www.vishay.com/docs/82907/tsmp95000.pdf)
- [Vishay TSAL6200 datasheet](https://www.vishay.com/docs/81010/tsal6200.pdf)
