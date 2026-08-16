# IMP-0016 — честный трёхантенный 2.4 GHz hunt

- Статус: **⚠️ Предложение; требуется решение владельца**
- Связано: `C-N24-02`, `C-N24-10`, `FND-0020`, draft `REQ-N24-0001`
- Зона: Main passive measurement; calibration/test source inherits its own gates
- Дата: 2026-08-16

## Контекст

Три nRF24 дают три одновременных бинарных RPD samples, а не три RSSI. Без дополнительного analog RF hardware нельзя честно вывести dBm, azimuth или VSWR. При этом три разнесённые/секторные антенны всё ещё могут быть полезны как сравнительный близкополевой hunt, если назвать измерение правильно и откалибровать разброс трактов.

## ⚠️ Предложение — варианты

### A — calibrated RPD hit-rate comparison (рекомендация)

- сохраняет принятые 3×nRF24 и текущий BOM class;
- для каждого radio/antenna показывает `hits / samples`, dwell, channel, data rate, age и calibration state;
- сравнение разрешено только на одном frequency/time window после fixture normalization трёх трактов;
- UI говорит `sector stronger / comparable / unknown`, но не рисует dBm, градусы или «точный пеленг»;
- waterfall/occupancy остаются бинарно-статистическими; краткий сигнал короче scan cycle может быть пропущен.

Это максимальная честная функция существующего radio silicon без добавления RF measurement path.

### B — встроенный real-power comparison

Добавить по трактам calibrated RF coupler/power detector либо отдельный measurement frontend. Это может дать traceable relative-power/dB data и улучшить directional hunt, но требует новой RF architecture, isolation/insertion-loss budget, ADC/dynamic-range/temperature calibration, BOM/area и emissions HIL. Само по себе это всё ещё не VSWR: для него нужны forward/reflected paths.

### C — убрать hunt

Оставить только parallel occupancy/waterfall. Самый простой вариант, но удаляет полезное трёхантенное сравнение и потому не рекомендуется.

## Стоимость без потери продукта

Вариант A исправляет ложное название без добавления BOM и сохраняет причину иметь три одновременных receiver. Вариант B — улучшение измерительного класса, не экономия. Замена трёх radio одним radio+RF switch теряет одновременность и не считается zero-loss.

## Один вопрос владельцу

Принять A как target baseline, оставив B будущим optional measurement expansion?

## Первичный источник

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)

