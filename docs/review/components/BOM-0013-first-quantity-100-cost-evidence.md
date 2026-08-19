# BOM-0013 — first exact quantity-100 cost evidence

- Статус: **проведено ревью первой партии; full cost coverage active**
- Дата: 2026-08-19
- Decision: [`DEC-0105`](../decisions/DEC-0105-machine-readable-quantity-100-cost-evidence.md)
- Review: [`REV-0005BL`](../reviews/REV-0005BL-first-cost-evidence-propagation.md)
- Generated review: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)
- Machine manifest: [`G2F-3I-target-bom.csv`](generated/G2F-3I-target-bom.csv)

## Результат

- exact published USD evidence: **15/187 purchase lines**;
- covered physical placements: **22/857**;
- still unpriced: **172/187 lines**;
- covered base-product partial subtotal: **USD 57.2502 per device** at the
  quantity-100 component-price basis;
- orderability remains **186/187** and substitution-policy coverage remains
  **187/187**.

Это не COGS и не целевая цена готового устройства. В subtotal ещё не входят,
в частности, raw display, cells, three E01 nRF modules, SA518, U214 accessory,
antennas/cables/SMA bodies, большая часть power/control circuitry, PCB, PCBA,
корпус, тестирование и логистика.

## Что покрыто

`SUB-COMPUTE-RF` и связанные RF строки:

- `ESP32-S3-WROOM-1U-N16R2`, `ESP32-C5-WROOM-1U-N8R8`, `SC1512-A4`;
- `CC1101RGPR`;
- пять `AD8314ACPZ-RL7` и два `LTC5532ES6#TRMPBF` placements.

Power/safety:

- `MAX17320G20+T`, `BQ25798RQMR`, `TPS25751DREFR`.

Mechanical/interconnect:

- `EC11E18244AU`, `FH12-40S-0.5SH(55)`, `DM3AT-SF-PEJM5`;
- `DX07S016JA1R1500`, two `USB4105-GF-A`, two
  `U.FL-R-SMT-1(10)` placements.

Полный per-line unit price, line subtotal, price-break wording, source и дата
находятся в generated Markdown/CSV; ручной документ их не дублирует, чтобы
числа не расходились.

## Первые cost hotspots

- пять AD8314 placements: **USD 14.2850**;
- два LTC5532 placements: **USD 7.7754**;
- вместе exact actual-TX/native-Wi-Fi detector ICs занимают **USD 22.0604**,
  или около 38.5% только этого частичного subtotal.

Это наблюдение для следующего zero-loss cost pass, не разрешение заменить или
убрать detector path. Эти узлы обеспечивают аппаратное доказательство
фактической передачи и относятся к conservative `SUB-COMPUTE-RF` policy.

## Открыто

1. Закрыть опубликованные exact-MPN qty-100 prices для оставшихся доступных
   distributor lines.
2. Отдельно получить RFQ для `HMX035CTFT-001`, SA518 и строк без применимой
   quantity-100 ступени.
3. Не смешивать base product, optional U214 и regional battery kit subtotals.
4. После полного component coverage добавить PCB/PCBA/enclosure/test quotes и
   только тогда считать product COGS.

## Последующий статус

Эти числа сохраняют исторический результат первой партии. Вторая партия и
explicit RFQ/retail gates находятся в
[`BOM-0014`](BOM-0014-high-placement-cost-and-explicit-gates.md); текущий итог
после десятой партии находится в
[`BOM-0024`](BOM-0024-resistor-cost-evidence.md): 162/187 lines,
816/857 placements и partial base subtotal USD 150.4157.
