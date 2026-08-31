# Power transitions and fault shutdown · H3-R2.2 result

[Русский](power-transition-result.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Startup](power-transition-sequences.md) · [Handover](power-handover.md) · [Inrush](inrush-load-step.md) · [Watchdog](watchdog-fault-display.md)

The complete H3-R2.2 chain is reviewed against the current R2 architecture: physical startup and KILL → USB/pack/DPM/brownout → eFuse/inrush/load-step → watchdog, hardware latch and retained cause.

| Result | Checked |
| --- | ---: |
| Startup/reset/recovery | 14 / 14 |
| USB/pack/DPM/brownout | 7316 / 7316 |
| Protected rail starts | 5 / 5 |
| Rail load-step envelopes | 4 / 4 |
| Watchdog/fault display | 10 / 10 |

Review corrected two real errors: the amber indicator now uses the latched `FAULT_KILL` rather than `FAULT_ASSERT_N`, and TPS3435 now distinguishes its `500 µs` device startup from the zero watchdog-window startup delay. Analytical failures and automatic re-arm paths are both `0`.

This result does not authorize placement, routing, purchase or fabrication. H6 repeats the calculations with extracted parasitics, while H8 measures the named waveform and fault-injection cases.

**Next point:** `H3-R2.3` — display, audio, IR, battery and Airband analog corners.

[Machine package](../hardware/verification/generated/H3-R2-transition-result.json).
