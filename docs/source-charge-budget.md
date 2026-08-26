# Source, charge, discharge and steady losses

[Русский](source-charge-budget.ru.md) · [Home](../README.md) · [DC rails](dc-power-budget.md) · [States](power-state-register.md)

H3.1.3 applies the rail budget to all `2032` states. At least 85% efficiency is independently reserved from source to SYS and from SYS to each enabled rail.

## Result

- Maximum SYS demand: `16.894 W`.
- Maximum series-pack current at 6.0 V: `2.816 A`; reserve to the 10-A cell contract is `255.114%`.
- Maximum steady rail-conversion loss: `2.534 W`; eFuse loss: `0.393 W`.
- Failed states: `0`; unresolved numeric inputs: `0`.

## Available-power control

5 V × 3 A is not treated as a universal source: `14` USB-only combinations are explicitly refused until load is reduced, a healthy pack is installed, or a higher PDO is selected. 9 V × 3 A and 15 V × 2 A run every declared profile. Charge is DPM-derated before system load in `254` combinations. Unknown 5-V fallback without a pack remains AON diagnostics only.

## Proof boundary

This closes the steady energy envelope. Recorded losses feed H3.6; transients, inrush, DPM and USB↔pack handover remain H3.2, while measured efficiency and current remain H8.

**Status:** `H3.1.3` is complete and reviewed; the exact current marker is `H3.6.1`.

[Complete machine calculation](../hardware/verification/generated/H3-VRF13-source-charge-budget.json).
