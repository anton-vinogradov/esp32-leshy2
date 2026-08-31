# Source, pack and charge margins · H3-R2.1.4

[Русский](power-source-margins.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Rail margins](power-rail-margins.md)

`H3-R2.1.4` evaluates all 2266 legal R2 states. All 75 source/pack lines have an explicit owner; there is no hidden allowance.

## Result

- Maximum SYS demand: `17.930 W`; raw source request at 85%: `21.094 W`.
- Maximum pack current at 6.0 V: `3.516 A`; reserve to the 8-A PF-R2-03 admission is `127.555%`.
- A requested 2-A charge either completes or is automatically DPM-reduced: derated states `306`.
- Failed checks: `0`; hidden or unowned lines: `0`.

## What each source can actually run

5 V × 3 A is not called universal: 14 USB-only states explicitly refuse an oversized profile. A healthy pack may supplement USB. Unknown fallback contributes zero numeric power until Rp/PD is measured; without a pack it remains AON-only. 9 V × 3 A and 15 V × 2 A run every declared profile, and charging always yields to system load.

## Proof boundary

The electrical simultaneous corner gives a `5.578 V` pack endpoint and `0.989 W` calculated in the two cells. The sustained envelope is separately restricted to SUPPORT_IDLE and 1.00 A on external 5 V: `1.549 A`, `0.192 W` in the cells. Startup, DPM and USB↔pack handover remain H3-R2.2, routed resistance remains H6 and measurement remains H8.

**Next exact marker:** `H3-R2.1.5` — cross-check and publish the H3-R2.1 result.

[Complete machine result](../hardware/verification/generated/H3-R2-source-margins.json).
