# Stage 3 — target product design

- Статус: **В работе от reviewed G2F principled-pinout baseline**
- Дата: 2026-08-17
- Пререквизит: repeat G2 **Проведено ревью** (`REV-0002AS`)
- Метод: [`FLOW-0001/G3`](../review/architecture/FLOW-0001-product-to-cad-gates.md)
- Working design: [`DEC-0051`](../review/decisions/DEC-0051-principled-pinout-as-working-design.md) /
  [`PIN-0003`](../review/architecture/PIN-0003-g2f-3i-principled-pinout.md)

## Reviewed inputs

- [`PD-0001`](../review/product-design/PD-0001-g3-physical-design-inputs.md) —
  field/control/safety/RF/expansion/service/power physical inputs;
- all base/optional/excluded capability dispositions through `DEC-0040`;
- no archived owner, pin map, board split or enclosure is a target constraint.

## Current artifact

[`LAY-0001`](../review/product-design/LAY-0001-form-factor-candidates.md)
сохраняет три преждевременных same-scope physical experiments:

1. `P1` compact wide — aggressive lower size bound;
2. `P2` balanced portrait — former engineering recommendation;
3. `P3` field-service chassis — RF/service feasibility upper bound.

Они больше не требуют выбора. `DEC-0041` возвращает активную работу к
logical/electrical feasibility, а затем к адаптации legacy `75×150 mm`
two-board clamshell generator. Его геометрия тоже рабочая гипотеза, не
обязательный финальный размер.

## Active prerequisite

`DEM-0001` и `SRC-0002` reviewed. `DEC-0042` создал единый источник; теперь он
содержит три structurally checked maps. `DEC-0044/NIF-0001/REV-0004L` выбрали
`G2F-3I` leading paper map. `PIN-0003/REV-0004V` дают generated principled
pinout diagram и exact pad/net tables; current budget честно равен S3
`31/3/2`, C5 `14/6/1`, RP `48/0/0`, slow `23/1/0` after accepted direct-QSPI
GPIO41/42 allocation (`DEC-0052/REV-0004X`). Это выполняет необходимый
working-baseline checkpoint `DEC-0041` и разрешает начать перенос в старый
reproducible mockup. `DSP-0003/REV-0004Y` теперь сравнивают старый 4-inch
1-bit SPI reference, новый 3.5-inch direct-QSPI class и EVE fallback;
`IMP-0045` остаётся решением exact display class. `FND-0060` exact electrical endpoints,
принятие profiled kit (`IMP-0043`), exact two-source assemblies и assembled RF
HIL (`FND-0058`) закрываются параллельно. Найденный physical/RF/power/service conflict меняет
рабочую карту через повторное G2F review, а не маскируется внутри макета.

## Downstream boundary

Physical packing/RF/power/service conflicts возвращаются в `G2F`; working pins
могут измениться. Whole-device optimality и только затем atomic target остаются
обязательными. KiCad по-прежнему заблокирован.
