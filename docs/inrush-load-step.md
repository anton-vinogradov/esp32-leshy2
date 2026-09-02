# Inrush and load steps · H3-R2.2.3

[Русский](inrush-load-step.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Power-transition result](power-transition-result.md)

The generator collects `132` fitted capacitors directly from the current R2 net ledger, applies each exact MPN tolerance and checks five protected outputs. Main, voice and external 5-V rails use the fastest `dV/dt` corner from the minimum control-capacitance corner. AON is checked as a current-limited start.

| Rail | C max, µF | Worst load, mA | Inrush, mA | Margin to min limit, mA | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `AON_SAFE_3V3` | 42.710000 | 72.100 | 92.900 | 0.000 | ✅ |
| `3V3_MAIN` | 91.110000 | 3046.000 | 71.079 | 882.921 | ✅ |
| `VVOICE_4V` | 12.000000 | 750.000 | 9.362 | 790.638 | ✅ |
| `5V_U214_PROTECTED` | 707.420000 | 1250.000 | 334.478 | 47.522 | ✅ |
| `5V_UNIT_PROTECTED` | 707.420000 | 1250.000 | 334.478 | 47.522 | ✅ |

The official U214 schematic really does fit `C12 = 470 µF`; it is not hidden. The calculation admits `705 µF`, a `+50%` envelope. The same ceiling applies to an attached M5 Unit; a larger reservoir needs its own calculation first. Both external branches remain below the `1.632 A` minimum limit even with the `1.25 A` worst load.

The largest `3V3_MAIN` step is `2656.000 mA`; its endpoint plus startup current retains positive hardware margin. `10 µs` and `5 µs` discretizations preserve identical pass/fail results with no more than `0.005000 ms timing difference.

## Honest proof boundary

This proves the current envelope and absence of a hardware-limit crossing. Real minimum droop, ringing, closed-loop settling and routed effective MLCC capacitance are named H8 oscilloscope checks, not invented analytical results.

**Status:** `H3-R2.2.3` reviewed; `5/5` starts and `4/4` rail load-step envelopes pass.

[Complete machine result](../hardware/verification/generated/H3-R2-inrush-watchdog.json).
