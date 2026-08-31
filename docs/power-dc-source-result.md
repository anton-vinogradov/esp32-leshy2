# DC, source and charge result · H3-R2.1

[Русский](power-dc-source-result.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Rails](power-rail-margins.md) · [Sources](power-source-margins.md)

`H3-R2.1.5` completes the first H3 workstream cross-check. H3-R2.1 is reviewed; the whole H3 phase is not, and neither KiCad nor ordering is authorized.

## Coverage

The check reconciles `2266` states, `56` operating profiles, `224` rail corners, `618` loads and all `75` source/pack lines. No gap, duplicate or hidden miscellaneous line remains.

## What is proved

- Minimum rail-current reserve: `30.560%`; junction-temperature reserve: `24.706 °C`.
- Maximum SYS: `17.930 W`; pack: `3.516 A`, sustained `1.549 A`.
- 5 V × 3 A safely refuses `14` heavy USB-only states; charge yields before load in `306` states.
- 9 V × 3 A and 15 V × 2 A run every declared profile.

## Next boundary

`H3-R2.2` verifies dynamics: startup, shutdown, inrush, DPM, brownout, watchdog and USB↔pack handover. Routed parasitics remain H6 and measurement remains H8.

**Current marker:** `H3-R2.2.1` — ordered startup, shutdown, reset and recovery. Placement, routing, purchasing and fabrication remain forbidden.

[Machine cross-check](../hardware/verification/generated/H3-R2-dc-source-crosscheck.json).
