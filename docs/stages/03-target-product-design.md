# Stage 3 — target product design

- Статус: **На ревью направления владельцем**
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
compares three same-scope physical directions:

1. `P1` compact wide — aggressive lower size bound;
2. `P2` balanced portrait — current engineering recommendation;
3. `P3` field-service chassis — RF/service feasibility upper bound.

The drawing shows body, controls, safety, RF, battery, service and M5
attachment zones together. Dimensions are working envelopes, not commitments.

## Open owner direction

G3 needs one direction or an explicitly described hybrid before exact control,
connector, antenna-access and service surfaces can receive review. This is not
an electronics selection. It prevents later pin/BOM optimization from silently
choosing the industrial design.

## Downstream boundary

After G3 direction review, G4 produces at least two complete electronics
architectures for the same physical product. Candidate block diagrams and
preliminary exact GPIO/bus maps may be used as feasibility evidence, but only
G5–G7 can select one atomic target architecture. KiCad remains blocked.
