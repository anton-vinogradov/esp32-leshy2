# REV-0005AS — exact integrated-touch propagation

- Status: **Проведено ревью**
- Decision: [`DEC-0088`](../decisions/DEC-0088-exact-integrated-touch-controller-and-irq.md)
- Finding: [`FND-0093`](../findings/FND-0093-touch-controller-identity-and-polarity-were-left-open.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| assembly identity | pass: HMX035CTFT-001 remains the panel candidate; ST77922 is explicitly its integrated COG, not a second panel or invented companion IC |
| exact contacts | pass: assembly SCL/SDA/INT/reset, QSPI, display reset, straps, supply/ground and TE map to documented ST77922 die pads |
| bus contract | pass: SYS_I2C client is exact `display_touch_controller`, address `0x38`, maximum 400 kHz; collision/readback remains HIL |
| IRQ semantics | pass: exact assembly source says low on touch; 10-kOhm raw pull-up plus fixed non-inverting 1G07 reach shared GPIO37 |
| obsolete alternative | pass: 1G06 inverter is absent from device registry, instance map, diagrams and target product text |
| pin budget | pass: GPIO37 remains shared IRQ; GPIO39/47 remain direct PCNT0 encoder phases; S3 stays `33/3/0` |
| reset/default | pass: display and touch have independent exact reset-low resistors and published 10-us/120-ms/100-ms timing boundaries |
| product diagrams | pass: vertical diagrams name HMX assembly, ST77922, pull-up and buffer as separate boxes; the raw net is a junction, not a serial passive |
| firmware | pass: runtime contract consumes fixed active-low `0x38`; GPIO37 remains source-discovery wake and does not infer touch from edge alone |
| cost/function | pass: one resistor is negligible, inverter population is deleted, and no capability or interface changes |
| CAD boundary | pass: assembly sourcing/drawing, real-tail mate, placement, signal integrity and HIL remain open; no KiCad authorization is inferred |

## Self-review correction

The review corrected stale machine text that still described a direct GPIO39
touch path after GPIO39 had become encoder phase A. It also rejected leaving a
floating raw-input assumption merely because the controller output-stage type
is not separately characterized: the exact 10-kOhm pull-up is compatible with
both plausible output stages and preserves the published active-low behavior.
