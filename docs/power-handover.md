# USB, pack and DPM · H3-R2.2.2

[Русский](power-handover.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Startup sequencing](power-transition-sequences.md)

`H3-R2.2.2` is verified against the complete R2 source/load register, not one nominal mode. `7316` transitions pass: USB attach/detach, DPM, pack removal, USB loss without a pack and brownout.

## What the hardware does

USB-C passes through **TPS25751D**, while USB and the protected pack converge in **BQ25798**. Its `SYS` output powers the product. Weak USB reduces charge to zero first; a healthy pack automatically supplements any remaining deficit. When USB disappears, the integrated BATFET transfers the load to the pack. OTG and backup are forbidden, so the pack cannot drive power back into USB.

Unqualified 5 V is not a RUN source: only AON diagnostics and disabled charging are allowed until Rp/PD is read and the protected profile is written. Masked readback is mandatory.

## Result

| Check | Result |
| --- | ---: |
| USB attach with a healthy pack | `1740` / `1740` |
| USB detach → pack | `1740` / `1740` |
| DPM and system-load priority | `1740` / `1740` |
| Pack removal/isolation while on USB | `1740` / `1740` |
| USB loss without a pack | `350` / `350` |
| Brownout/anti-rearm | `6` / `6` |

Worst supplement is `3.516 A` against the `8.000 A` limit; unsafe admissions and automatic restarts are both `0`.

## Honest proof boundary

Logic, current limits and safe outcomes are proved analytically. Absolute `SYS` droop, BATFET transfer time and routed parasitics depend on the assembled board and are oscilloscope checks on the first unit in H8. Placement, routing, purchasing and fabrication remain unauthorized.

[`H3-R2.2.3/.4`](power-transition-result.md) completed inrush, load-step, watchdog and fault-display review. [`H3-R2.3`](analog-electrical-verification.md), [`H3-R2.4`](digital-electrical-verification.md) and [`H3-R2.5`](rf-electrical-verification.md) are reviewed; **current marker: `H3-R2.6`.**

[Complete machine result](../hardware/verification/generated/H3-R2-handover.json).
