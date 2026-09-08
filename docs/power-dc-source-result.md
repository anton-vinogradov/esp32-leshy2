# DC, source and charge result · H3-R2.1

[Русский](power-dc-source-result.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Rails](power-rail-margins.md) · [Sources](power-source-margins.md)

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `rail_current_voltage_thermal_pass`; `numerical:existing_checks`; `applicability:rail_inputs`; `applicability:source_inputs`.

[Machine evidence](../hardware/verification/generated/H3-R2-dc-source-crosscheck.json).

## Coverage

The check reconciles `2266` states, `56` operating profiles, `224` rail corners, `629` loads and all `77` source/pack lines. No gap, duplicate or hidden miscellaneous line remains.

## Provisional model result

- Minimum rail-current reserve: `30.560%`; junction-temperature reserve: `24.706 °C`.
- Maximum SYS: `17.930 W`; pack: `3.516 A`, sustained `1.549 A`.
- 5 V × 3 A safely refuses `14` heavy USB-only states; charge yields before load in `306` states.
- The retained power-budget model admits every profile at 9 V × 3 A and 15 V × 2 A; this does not prove startup or valid voltage in the current circuit.

## Next boundary

`H3-R2.2` verifies dynamics: startup, shutdown, inrush, DPM, brownout, watchdog and USB↔pack handover. Routed parasitics remain H6 and measurement remains H8.

Current numerical results are provisional; analytical applicability findings remain open.
