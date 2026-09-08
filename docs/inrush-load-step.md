# Inrush and load steps · H3-R2.2.3

[Русский](inrush-load-step.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Power-transition result](power-transition-result.md)

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `applicability:rail_inputs`; `applicability:sequence_inputs`; `applicability:handover_inputs`.

[Machine evidence](../hardware/verification/generated/H3-R2-inrush-watchdog.json).

The generator accounts for **132** fitted capacitors from the current R2 net ledger and applies the stated capacitance tolerances. Separate calculations for five protected outputs are retained. MAIN, voice and external 5-V paths use nominal slew arithmetic with minimum control capacitance; AON is treated as a current-limited start.

## Capacitance, load and provisional headroom

| Rail | C max, µF | Worst load, mA | Capacitive inrush, mA | Margin to model protection minimum, mA | Numerical comparison |
|---|---:|---:|---:|---:|---|
| `AON_SAFE_3V3` | 42.710000 | 72.100 | 92.900 | 0.000 | pass |
| `3V3_MAIN` | 91.110000 | 3046.000 | 71.079 | 882.921 | pass |
| `VVOICE_4V` | 12.000000 | 750.000 | 9.362 | 790.638 | pass |
| `5V_U214_PROTECTED` | 707.420000 | 1250.000 | 334.478 | 47.522 | pass |
| `5V_UNIT_PROTECTED` | 707.420000 | 1250.000 | 334.478 | 47.522 | pass |

The official U214 schematic includes **C12 = 470 µF**. The retained design budget is **705 µF**, a +50% allowance. The same budget is assigned to an attached M5 Unit; a larger reservoir needs a separate calculation. This is a design allowance, not proof of startup across protection and dynamic-load corners.

## Load step and numerical convergence

The maximum considered `3V3_MAIN` step is **2656.000 mA**. Model comparisons: starts **5 / 5**, load steps **4 / 4**. A 0.010-ms step and half that step produce at most 0.005000 ms timing difference; classification agrees: yes. Numerical convergence does not validate the input limits.

## Remaining work

Minimum dV/dt capacitance alone does not establish a guaranteed maximum IC slew rate. MAIN RILM, AON protection resistance at the fitted setting and supervisor bounds are not yet qualified. Positive nominal current headroom therefore does not prove startup.

Actual droop, ringing, closed-loop settling and voltage-dependent effective MLCC capacitance need separate analysis and measurements. These do not replace correction of the open analytical inputs. [Watchdog and retained shutdown reason](watchdog-fault-display.md) are covered separately.
