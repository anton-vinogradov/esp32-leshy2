# Power-transition verification result

[Русский](power-transition-result.ru.md) · [Home](../README.md) · [Startup/KILL](power-transition-startup.md) · [Handover](power-handover.md) · [Inrush](inrush-load-step.md) · [Watchdog/UI](watchdog-fault-display.md)

H3.2 closes as one reviewed chain: startup/KILL → USB↔pack/brownout → eFuse/inrush/load-step → watchdog/retained reason.

- `7` startup/shutdown sequences, `7` handover states, `5` rail-startup envelopes and `6` fault scenarios pass with no unresolved analytical failure.
- Earliest re-arm is `48.444 ms`, leaving `20.444 ms after maximum POR.
- The watchdog detects missing service no later than `1760 ms`.
- Two real source errors were corrected: latch polarity/asynchronous inputs and the wrong POR timing claim.
- Physical waveforms, switch bounce, MLCC DC bias, charger-loop droop and fault injection are not claimed complete; they are explicitly assigned to H8.

**Status:** `H3.2` reviewed. Exact current marker: `H3.6.1`, worst-case board, battery and enclosure thermal model.

[Machine closure package](../hardware/verification/generated/H3-VRF25-transition-consolidation.json).
