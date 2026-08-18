# DEC-0068 — separate fixed downstream rails

- Статус: **Принято как принципиальное инженерное решение; распространено**
- Дата: 2026-08-18
- Analysis: [`PWR-0008`](../architecture/PWR-0008-exact-downstream-rail-tree.md)
- Propagation review: [`REV-0005Y`](../reviews/REV-0005Y-downstream-rail-tree-propagation.md)

## Decision

1. `BQ25798 SYS` feeds four independent converters:
   `AON_SAFE_3V3`, `3V3_MAIN`, `VVOICE_4V` and `5V_EXT`.
2. `TPS629203DRLR + WPN201612H2R2MT` is the exact first target for the
   always-on 3.3-V safety rail. MAX17320 AOLDO is not a product AON source.
3. Three physical `TPS564252DRLR` instances provide fixed 3.3, 4.0 and 5.0 V.
   Runtime selection between 4 and 5 V does not exist. A feedback/mux fault
   therefore cannot apply the accessory voltage to SA518.
4. Separate `MWSA0503S-3R3MT` inductors serve main and voice; one
   `MWSA0503S-4R7MT` serves external 5 V.
5. Five physical `TPS22919DCKR` instances switch the nRF group, CC1101,
   microSD, ES8311 and Si4732. One grouped nRF power domain is permitted, but
   it does not alter the requirement that all three radios operate
   simultaneously in every PTX/PRX mix.
6. A connector-side TPS259470-family 5-V eFuse provides true reverse blocking,
   a tolerance-safe current limit, bounded 2-A transient allowance, current
   test point and open-drain fault evidence. [`DEC-0069`](DEC-0069-latch-off-external-efuse.md)
   subsequently selects exact latch-off `TPS259470LRPWR` instead of the early
   auto-retry suffix.
7. Every unused interface remains powered off and discharged where its
   electrical contract permits it. Hardware STOP dominates nRF, CC, voice and
   external-rail enables.
8. Exact passive values, thermal/layout closure and HIL remain prerequisites;
   this decision does not authorize KiCad.

## Package correction

The official TPS56425x datasheet proves that SOT-563 pin 4 is `PG`, not
`BST`; bootstrap is integrated. The machine contact map, sequence and product
diagram use the corrected physical pin.

## Cost/lifecycle boundary

The accepted topology reuses exact buck/load-switch MPNs to reduce BOM and
assembly setup while retaining physical rail isolation. Newer `TPS564252B`
may be requalified when it has comparable stock; it is not substituted merely
because the family is newer. A pin-compatible OOA voice variant remains a HIL
fallback, not an untracked mixed BOM.
