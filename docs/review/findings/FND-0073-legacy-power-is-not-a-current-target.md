# FND-0073 — legacy power sheet is not a current target

- Статус: **Подтверждено; battery ambiguity закрыта `DEC-0062`, power correction active**
- Дата: 2026-08-18
- Artifact: [`PWR-0002`](../architecture/PWR-0002-i3-power-prerequisite-audit.md)
- Legacy source: [`hardware/tscircuit/power.tsx`](../../../hardware/tscircuit/power.tsx)

## Finding

Legacy power is internally recognizable but no longer matches the product:

1. `BQ25887` is a 2S boost charger with cell balancing and monitoring ADC, not
   an NVDC system power path or a learned/coulomb-counting fuel gauge.
2. Fixed 3-A input mode is not justified by two Type-C Rd resistors; source
   current advertisement needs CC/PD detection.
3. The old master switch prevents charging in OFF and gives no USB-only/dead-
   pack service path.
4. `3V3 / 2 A` is below the accepted `2.5 A` continuous floor, while the old
   `5 V / 3 A` includes deleted onboard loads and is now needlessly large.
5. The source has no accepted AON safety rail, 4-V voice rail, reverse-safe
   accessory path, current/fault tree or complete quiet-state switches.
6. An open two-cell holder is a mechanical idea, not a qualified 2S pack; cell
   mismatch, reversed insertion and removal of one cell remain unresolved.

## Why this matters

Copying the sheet would simultaneously hide functional loss, preserve obsolete
cost and create battery/USB safety ambiguity. The existing tsCircuit file stays
untouched as historical evidence; it is not patched forward and does not
authorize KiCad.

## Correction

`PWR-0002` re-derives loads and scenarios and preserves the valid 2S/rail
ideas. `DEC-0062` explicitly retains two individually replaceable cells with
a new pre-connect/reverse/mismatch/removal safety boundary. Current power-path
directions are now compared in `PWR-0003/IMP-0053`.
