# Inrush and load steps

[Русский](inrush-load-step.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

Capacitance is no longer copied by hand: the generator collects every actual capacitor instance attached to each rail from the single component/net map. It currently accounts for `93` fitted capacitors.

| Rail | Nominal C, µF | Worst active load, mA | Result |
|---|---:|---:|---|
| `AON_SAFE_3V3` | 23.5 | 89.5 | pass_current_limited_start |
| `3V3_MAIN` | 59.7 | 2462.0 | pass |
| `VVOICE_4V` | 10.0 | 900.0 | pass |
| `5V_U214_PROTECTED` | 2.2 | 1250.0 | pass |
| `5V_UNIT_PROTECTED` | 2.2 | 1250.0 | pass |

The AON eFuse may enter a bounded current-limited ramp and retains positive margin. Main, voice and external dV/dt networks bound capacitive inrush; accepted worst active load plus inrush remains below each minimum current limit.

This proves the current envelope, not the short closed-loop buck droop. Effective MLCC capacitance, rail minimum and settling at named load steps remain H8 waveforms.

**Status:** `H3.2.3` reviewed; 5/5 startup envelopes pass. [Machine evidence](../hardware/verification/generated/H3-VRF23-inrush-load-step.json).
