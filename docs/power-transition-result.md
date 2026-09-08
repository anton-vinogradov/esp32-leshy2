# Power transitions and fault shutdown · H3-R2.2 result

[Русский](power-transition-result.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Startup](power-transition-sequences.md) · [Handover](power-handover.md) · [Inrush](inrush-load-step.md) · [Watchdog](watchdog-fault-display.md)

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `applicability:inrush_inputs`; `applicability:sequence_inputs`; `applicability:handover_inputs`.

[Machine evidence](../hardware/verification/generated/H3-R2-transition-result.json).

The analysis chain is retained: physical KILL-to-RUN and reset → USB/pack/DPM/brownout → protected rails, inrush and load steps → watchdog, hardware latch and retained shutdown reason. The table enumerates model coverage, not proven operating modes of the current hardware.

| Model group | Enumerated cases |
|---|---:|
| Startup, reset and recovery | 14 |
| USB, pack, DPM and brownout | 7316 |
| Protected-rail starts | 5 |
| Rail load steps | 4 |
| Watchdog and shutdown-reason display | 10 |

## Sequence and retained corrections

After reset, the safety controller holds the fault request active. Resumption requires successful self-test, continuous physical KILL and the following KILL-to-RUN edge. Recovery of USB, firmware or watchdog signaling does not authorize automatic restart.

Two earlier corrections are retained: the amber indicator uses latched `FAULT_KILL`, not `FAULT_ASSERT_N`; TPS3435 distinguishes its 500-µs device startup from zero watchdog-window startup delay. A reason screen is planned when MAIN and UI are safe; complete AON loss cannot promise a final record, which later startup handles explicitly.

Numerical failures in the retained aggregate comparison: 0; model automatic restart paths: 0. A zero numerical counter does not resolve open power-applicability findings.

## Why review remains required

The model must be reconciled with fitted MAIN/AON components and settings, including the missing guaranteed supervisor bounds; dependent comparisons must then be repeated. Routed-parasitic analysis and first-prototype measurements remain separate stages, not substitutes for this correction.

The [current H3 result](h3-r2-acceptance.md) separates analytical findings, physical evidence and firmware obligations.
