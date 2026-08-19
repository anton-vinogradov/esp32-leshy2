# REV-0005AE — pack diagnostic frontend propagation review

> Historical first-pass review. Current reviewed hardware is
> `PWR-0017/DEC-0078/REV-0005AI`; it corrects the TPUL WQFN pin map and adds a
> second-channel refractory lockout plus repetition-safe load.

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0074`](../decisions/DEC-0074-bounded-pack-diagnostic-pulse.md)
- Analysis: [`PWR-0013`](../architecture/PWR-0013-exact-pack-diagnostic-frontends.md)
- Finding: [`FND-0078`](../findings/FND-0078-mspm0-pa24-forbids-injection-current.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Owner decision | 10-Ohm option B and hard/software `<=50 ms` ceiling preserved |
| Independent cutoff | direct MCU level removed; TPUL2G223 non-retriggerable Q is the only MOSFET gate authority |
| Reset/power loss | separate trigger and gate 10-kOhm pull-downs fail the load off |
| Pulse arithmetic | approximately 34.4 ms typical, 28.7-40.7 ms conservative paper range and 25-50 ms production acceptance |
| Load stress | approximately 0.57-0.88 A; 0.353 J nominal at 8.4 V/50 ms; full 2.78-A proof remains HIL |
| Real package contacts | PA25/A2 pin 20 and PA26/A1 pin 1 are exposed; PA24/A3 pin 19 is no longer battery-driven |
| ADC range | worst paper inputs 1.211/1.165 V stay below 1.378-V minimum internal reference |
| GPIO budget | unchanged `12 used / 3 service-reserved / 3 free`; free set corrected to PA24/PA27/PA28 |
| Machine source | 19 physical timer/load/divider/filter instances and exact routes replace all three abstract frontends |
| Generated/target diagrams | vertical atlas and both target landing diagrams name every physical instance and role |
| Firmware contract | edge-only request, >=10-ms settled sample within a measured >=25-ms pulse, internal reference, hardware timeout and no full-load claim propagated |

## Corrections made

- `FND-0078`: PA24 was physically exposed but electrically unsuitable because
  its supported injection current is zero; midpoint/stack move to PA25/PA26;
- the earlier direct reset-low load control did not independently enforce the
  accepted 50-ms ceiling; a non-retriggerable hardware one-shot now does;
- anonymous divider, load and filter blocks are now exact physical components;
- the X7R timing part was replaced by a dedicated C0G part so the lower pulse
  bound and therefore the loaded-sample window are demonstrable;
- the diagnostic is explicitly a pre-admission screen, not a 15-W product-load
  qualification.

## Remaining gates

Production cell MPN, droop/contact thresholds, timer-lot pulse distribution,
ADC acquisition/calibration, safe cooldown, repeated-pulse temperature,
insertion/removal and all source-handover HIL remain open. The paper circuit
receives **«Проведено ревью»** and does not authorize KiCad.
