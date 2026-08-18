# DEC-0080 — exact AON-PG/POR/main-rail sequence

- Статус: **Принято; проведено ревью paper electrical behavior**
- Дата: 2026-08-18
- Analysis: [`PWR-0019`](../architecture/PWR-0019-exact-source-sequence-and-power-reserve.md)
- Finding: [`FND-0084`](../findings/FND-0084-abstract-main-source-sequencer.md)
- Propagation: [`REV-0005AK`](../reviews/REV-0005AK-source-sequence-propagation.md)

## Decision

1. There is no separate MCU, expander or programmable source-admission
   sequencer between AON and `3V3_MAIN`.
2. An admitted battery or protected USB path creates `BQ25798 SYS`; `SYS`
   directly enables `TPS629203DRLR`.
3. Pulled-up `TPS629203.PG` directly drives `TPS3808G33DBVR.MR_N`. The
   supervisor must see both AON PG and its own 3.07-V SENSE threshold before
   starting the existing CT delay.
4. `TPS3808.RESET_N = POR_N` directly enables `TPS564252 #MAIN`. One exact
   `RC0402FR-0710KL` pulls POR up to AON and one exact
   `RC0402FR-07100KL` pulls it/main EN down.
5. The nominal released level is `3.3 × 100/(100+10) = 3.0 V`. At the
   supervisor's 3.07-V valid-rail boundary and 1% resistor corners it remains
   about `2.79 V`, above the main converter's 1.25-V maximum rising threshold.
   Asserted RESET remains below its 1.10-V maximum falling threshold.
6. Charge admission initially reserves a conservative 15% of negotiated input
   power for the complete protected input/converter path. Charge current is
   the lesser of 2 A and remaining admitted power divided by pack voltage; DPM,
   missing evidence, temperature or fault state can only reduce it.

## Consequence

Two abstract endpoints disappear and one already-used resistor value changes
position. No new unique BOM line, GPIO, firmware boot dependency or user
function is added. Battery-only, USB-only and automatic supplement behavior
remain owned by the exact protected source path; loss of AON validity now has
a direct calculable route to main-rail shutdown.

Exact ramp, CT tolerance, load-step, USB attach/remove, battery removal,
supplement-mode and brownout traces remain HIL. This decision does not
authorize KiCad.

