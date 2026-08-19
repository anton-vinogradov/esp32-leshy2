# FND-0083 — a generic protected-cell placeholder could not close real limits

- Статус: **Исправлено выбором exact qualification target; specimen/certification gate сохранён**
- Дата: 2026-08-18
- Correction: [`PWR-0018`](../architecture/PWR-0018-xtar-18650-4000mah-cell-profile.md)
- Decision: [`DEC-0079`](../decisions/DEC-0079-xtar-18650-4000mah-qualification-target.md)
- Review: [`REV-0005AJ`](../reviews/REV-0005AJ-exact-cell-propagation.md)

## Finding

`protected button-top 18650, MPN TBD` was enough to reserve volume, but not to
close the power architecture. It provided no exact capacity, geometry,
charge/discharge limit, initial resistance, protection trip or transport
identity. Consequently the design could neither prove its `12 W / 15 W`
load envelope nor generate honest loaded-droop and thermal test matrices.

Naming the raw cell hidden under a third-party protection board would not fix
this. The completed protected assembly has different contacts, length,
resistance, trip behavior and certification identity from the raw cell.

## Correction

Two exact `XTAR 18650 4000mAh` protected button-top cells become the first
qualification target. The manufacturer datasheet gives `4000 mAh` typical,
`3800 mAh` minimum, `10 A` maximum continuous discharge, `2 A` standard and
`4 A` maximum charge, `<=40 mOhm` initial resistance, `11…14 A` discharge
overcurrent protection and a maximum `18.7 × 69.7 mm` envelope.

This exact choice closes the paper current/capacity/geometry inputs and freezes
the product charge ceiling at the cell's standard `2 A`. It does not turn
marketing `CE/RoHS` claims into a battery transport approval: an exact
assembly-matching UN38.3 test summary, received specimens, holder fit,
protection trip, thermal response and droop distributions remain mandatory.

