# USB, pack and DPM · H3-R2.2.2

[Русский](power-handover.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Startup sequencing](power-transition-sequences.md)

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `applicability:source_inputs`; `applicability:sequence_inputs`.

[Machine evidence](../hardware/verification/generated/H3-R2-handover.json).

The model enumerates the complete R2 source/load register: USB attach and detach, dynamic power management (DPM), pack removal, USB loss without a pack and brownout. This scenario inventory is retained; applicability of the power limits is checked separately.

## Intended sequence

USB-C passes through **TPS25751D**, while USB and the protected pack converge in **BQ25798**. The `SYS` output powers the product. Insufficient USB power reduces charging first, down to zero; a healthy pack must then supplement the remaining demand. When USB disappears, the integrated BATFET transfers the load to the pack. This is the intended sequence, not measured proof of uninterrupted `SYS`.

OTG and backup are forbidden: reverse pack-to-USB power is not enabled by the configuration. Unqualified 5 V is not a RUN source: only AON diagnostics and disabled charging are allowed until Rp/PD is read and the protected profile is written. Masked readback is mandatory after writing.

## Provisional comparisons

| Scenario family | Enumerated model cases |
|---|---:|
| USB attach with a healthy pack | 1740 |
| USB detach → pack supply | 1740 |
| DPM: system-load priority | 1740 |
| Pack removal or isolation while on USB | 1740 |
| USB loss without a pack | 350 |
| Brownout and anti-rearm | 6 |

Retained model comparisons: **7316 / 7316**, numerical failures: **0**. Worst pack supplement in this model is **3.516 A** against the retained 8-A limit. Model unsafe admissions: 0; automatic restarts: 0. These numbers do not qualify the fitted power cell's current or thermal limits.

## Verification boundaries

Applicability of the MAIN source model, protection limits and supervisor bounds remain analytical questions. Actual `SYS` droop, BATFET transfer time and routed parasitics are separate obligations requiring routed-design analysis and first-prototype waveforms. A positive logical transition check does not replace that evidence.

Continue with [inrush and load steps](inrush-load-step.md), [watchdog and shutdown reason](watchdog-fault-display.md), and the [combined transition result](power-transition-result.md). Fresh reports do not close current power qualification.
