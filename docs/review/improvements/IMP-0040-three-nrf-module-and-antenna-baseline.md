# IMP-0040 — three-nRF module and antenna baseline

- Статус: **⚠️ Открыто решение владельца**
- Дата: 2026-08-17
- Evidence: [`N24M-0001`](../architecture/N24M-0001-exact-module-antenna-comparison.md)
- Requirement: [`REQ-N24-0001`](../requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)
- Working geometry: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)

## Контекст решения

Три nRF должны одновременно поддерживать любой `PTX/PRX` mix, быть одинаково
полнофункциональными и иметь три стабильные antenna/calibration identities.
`DEC-0047` уже ограничил обещание честным измеренным RF envelope. Теперь нужно
выбрать exact module/antenna direction, иначе нельзя закончить rail budget,
physical zoning, cable/keep-out model и целевой `N24H-0001` HIL.

## Вариант A — 3× `E01-ML01IPX`, 0 dBm, три разнесённые антенны (рекомендуется)

Три одинаковых SMD modules с IPEX ставятся внутри, а три коротких измеряемых
feed paths идут к разнесённым внешним SMA либо индексированным FPC radiators.
Это сохраняет нативный максимум nRF24L01P 0 dBm, симметрию трёх трактов и
совместимость с полезной частью legacy antenna-bank geometry. Одновременный
`3T` nominal module current — около 39 mA, до rail losses и transients.

Цена: три IPEX connectors, cables и radiators; нужны retention, bend/fold и
cable-loss checks. Зато antenna placement не привязано к месту цифрового
модуля, а три calibration identities воспроизводимы.

Опционально можно сохранить land-pattern compatibility с `E01-ML01S` для
bench/cost experiments, но не объявлять её product-equivalent без отдельного
RF/mechanical HIL.

## Вариант B — 3× `E01-ML01S`, 0 dBm, встроенные PCB antennas

Минимум connector/cable/assembly BOM и тот же nominal radio current. Но каждый
module должен оказаться у собственной свободной board/enclosure edge-zone.
Внутренняя component zone старого макета для этого непригодна; батареи, платы,
рука и корпус сильнее меняют паттерны и calibration. Потребуется новая
трёхкромочная компоновка вместо прямого reuse внешнего antenna bank.

Это потенциально дешевле после физического proof, но не zero-loss экономия по
умолчанию: можно потерять воспроизводимость sector hunt, isolation и service
replaceability.

## Вариант C — 3× 27 dBm PA/LNA modules внутри base device

Даёт большой link budget, но `E01-2G4M27D` требует до 490 mA на один TX при
3.3 V: `3T` достигает 1.47 A только по модулям. Local leakage на 27 dB выше
0 dBm path, габарит и SMA burden значительно больше. Это прямо ухудшает самый
трудный обязательный режим `1T+2R/2T+1R` и противоречит цели снизить стоимость
без потерь. Для base device вариант не рекомендуется.

High-power path можно позже рассматривать только как отдельный Laboratory
accessory/remote RF head с собственным питанием, containment и профилем. Он не
заменяет три симметричных base paths.

## Рекомендация

Принять A как production-layout direction: три одинаковых 0 dBm IPEX modules
и три разнесённых external/FPC antenna paths. Зафиксировать общий compact land
как optimization goal для `ML01S/IPX`, если sample/land-pattern check не
ухудшает target. Вариант B оставить cost experiment; C удалить из base BOM.

## Вопрос владельцу

Принимаем вариант A как направление целевой компоновки nRF, оставляя
`E01-ML01S` только проверяемым cost/bench alternate, а PA/LNA — внешним
Laboratory profile?
