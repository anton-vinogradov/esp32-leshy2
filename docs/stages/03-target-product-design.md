# Stage 3 — target product design

- Статус: **Ожидает G2F electrical candidate review**
- Дата: 2026-08-17
- Пререквизит: repeat G2 **Проведено ревью** (`REV-0002AS`)
- Метод: [`FLOW-0001/G3`](../review/architecture/FLOW-0001-product-to-cad-gates.md)

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
`G2F-3I` leading paper map. Дальше она закрывает physical RF, exact peripherals,
signal integrity, memory/traffic/power/service и HIL. После квалификации
рабочей карты G3 переносит её в старый reproducible mockup.

## Downstream boundary

Physical packing/RF/power/service conflicts возвращаются в `G2F`; working pins
могут измениться. Whole-device optimality и только затем atomic target остаются
обязательными. KiCad по-прежнему заблокирован.
