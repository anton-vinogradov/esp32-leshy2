# DEC-0065 — supervised 2S battery topology

- Статус: **Принято владельцем; распространено**
- Дата: 2026-08-18
- Closes: [`DEC-0064`](DEC-0064-reopen-battery-electrical-topology.md), [`IMP-0055`](../improvements/IMP-0055-battery-electrical-topology-after-reopen.md)
- Comparison: [`PWR-0006`](../architecture/PWR-0006-one-or-two-cell-topology-comparison.md)
- Propagation review: [`REV-0005T`](../reviews/REV-0005T-supervised-2s-topology-decision-propagation.md)

## Decision

1. Base Leshy2 uses two individually replaceable qualified 18650 cells in a
   supervised `2S` electrical arrangement. Both admitted cells are required
   for battery-powered operation; one-cell operation is not a base-product
   requirement.
2. The working battery envelope is `6.0…8.4 V`. The accepted
   `BQ25798RQMR` charger/NVDC path is configured for two series cells.
3. The pair remains disconnected until both cells pass mechanical polarity,
   profile, voltage, temperature, contact and loaded-droop admission. A
   mismatch is rejected rather than hidden by charging or ordinary balancing.
4. The downstream `3.3 V`, `4.0 V` voice and `5 V` auxiliary rails use buck
   classes from the 2S input unless a later exact calculation proves a
   different converter class necessary.
5. The pack path must sustain the reviewed `12 W` continuous and `15 W`
   bounded-transient product envelope. At `6.0 V` and `90%` conversion that is
   `2.22 A` continuous and `2.78 A` transient before tolerance, aging,
   ripple, temperature and fault margin.
6. Controlled two-slot `1S` and one-slot `1S` remain documented only as
   possible future product variants. They do not influence the base-product
   rail tree or justify direct parallel connection of removable cells.

## Consequences

- `PWR-0005/IMP-0054` resume as the current exact manager/admission gate.
- The downstream passes now select the manager, switching path, contacts,
  rails and `XTAR 18650 4000mAh` first cell target. Certification/specimen,
  droop, thermal and fault HIL remain `I3`; this decision is not KiCad
  authorization.
- Either-cell removal opens the 2S source. Early-removal detection, hold-up,
  orderly shutdown, data integrity and no-restart behavior remain calculated
  circuit and HIL gates.
- A future one-cell-capable SKU requires a new owner decision and a complete
  review of its isolated slot paths, converters, current, loss and thermal
  envelope.
