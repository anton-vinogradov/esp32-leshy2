# PWR-0010 — exact external-eFuse passive profile

- Статус: **Проведено ревью принципиальной схемы**
- Дата: 2026-08-18
- Parent topology: [`PWR-0008`](PWR-0008-exact-downstream-rail-tree.md)
- eFuse choice: [`DEC-0069`](../decisions/DEC-0069-latch-off-external-efuse.md)
- Decision: [`DEC-0071`](../decisions/DEC-0071-post-start-accessory-transient-profile.md)
- Propagation review: [`REV-0005AB`](../reviews/REV-0005AB-external-efuse-passive-profile.md)
- Primary IC evidence: [TI TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf)

## Correction that forced this pass

The earlier text treated the accepted `2.0 A` envelope as startup current and
implied that `ITIMER` postponed the nominal `1.50 A` current limit. That is not
how `TPS259470L` works. Its `RILM` current limit is active immediately during
startup. `ITIMER` is consulted only after startup while current lies between
`ILIM` and the approximately `2×ILIM` fast-trip boundary.

The corrected contract therefore separates two mechanisms:

1. `dVdt` limits capacitive inrush while the accessory rail rises;
2. `ITIMER` admits the bounded `2.0 A` envelope only after startup.

This is a correction of a functional claim, not a passive-value refinement.

## Exact accepted paper profile

Every row is one separately placed physical component. Reusing one capacitor
MPN at input and output does not merge those two instances.

| Instance | Exact MPN | Value/package | Function |
|---|---|---|---|
| `ext_rilm` | `Yageo RC0402FR-072K21L` | 2.21 kOhm, ±1%, 0402 | `ILM` to ground; nominal 1.509-A active limit |
| `ext_dvdt_cap` | `Murata GRM155R71H472KA01D` | 4.7 nF, ±10%, 50 V, X7R, 0402 | startup output-slew control |
| `ext_itimer_cap` | `Murata GRM188R71E224KA88D` | 220 nF, ±10%, 25 V, X7R, 0603 | post-start overload timer |
| `ext_ovlo_top` | `Yageo RC0402FR-07169KL` | 169 kOhm, ±1%, 0402 | OVLO divider top |
| `ext_ovlo_bottom` | `Yageo RC0402FR-0747KL` | 47 kOhm, ±1%, 0402 | OVLO divider bottom |
| `ext_input_cap` | `Murata GRM21BR71E225KE11L` | 2.2 uF, ±10%, 25 V, X7R, 0805 | local `IN` bypass |
| `ext_output_cap` | `Murata GRM21BR71E225KE11L` | 2.2 uF, ±10%, 25 V, X7R, 0805 | local `OUT` bypass |
| `ext_bleeder` | `Yageo RC0603FR-071KL` | 1 kOhm, ±1%, 100 mW, 0603 | passive protected-output discharge |

The machine source connects every contact explicitly and projects all eight
parts into the vertical principled diagram. `AUXOFF` is not silently assigned;
whether it should become separate hardware inrush-done evidence remains a
later sequencing-circuit question.

## Current-limit screen

The datasheet design equation is:

`RILM = 3334 / ILIM`, therefore `ILIM_typ = 3334 / 2210 = 1.509 A`.

Applying ±1% resistor tolerance and the conservative ±10% transfer screen gives
approximately `1.344…1.676 A`. Thus the lower paper limit remains above the
accepted `1.25 A` continuous load. The minimum approximate fast-trip boundary
is `2 × 1.344 = 2.688 A`, so a `2.0 A` post-start transient remains in the
timer-controlled region rather than the immediate fast-trip region.

These calculations qualify a first schematic value. Exact specimen limit,
temperature drift and fault latency remain measured acceptance gates.

## Startup-slew and U214 screen

TI gives `CdVdt(pF) = 2000 / SR(V/ms)`. The 4.7-nF choice gives a typical
`0.426 V/ms` output rise. Using the disclosed `dVdt` source-current range
`0.81…3.82 uA` and capacitor ±10% produces a deliberately broad raw range of
approximately `0.157…0.903 V/ms`, or roughly `31.8…5.5 ms` for a 5-V rise.

The first admitted Cap profile is limited to `1 mF` effective input
capacitance until measured otherwise. At the worst paper slew its capacitive
component is at most `0.903 A`. U214 visibly contains `C12=470 uF` plus smaller
bulk capacitors; against its published maximum LoRa operating load of
`163.4 mA`, even the conservative `1 mF` profile totals about `1.067 A`, below
the `1.344-A` paper current-limit floor. The real effective capacitance,
converter startup state and cable/connector parasitics remain HIL inputs.

## Post-start transient timer

TI gives `t = ΔV × C / IITIMER`. With 220 nF, the typical interval is
`1.51 V × 220 nF / 1.8 uA = 184.6 ms`. Combining IC limits, ±10% initial
capacitance and a conservative additional X7R ±15% temperature span gives a
paper envelope of approximately `86.6…404 ms` before latch-off.

Firmware must never budget this interval during startup, continuously renew it
or use it as ordinary 2-A operation. A post-start excursion is one bounded
event; an asserted fault ends the accessory session and requires a fresh
explicit action after removal of the physical cause. A second closely spaced
excursion is not promised the full interval: larger `CITIMER` also extends its
recharge, so burst/re-arm timing remains a measured HIL gate.

## OVLO, bypass and discharge

The `169 kOhm / 47 kOhm` divider gives
`1.2 × (1 + 169/47) = 5.515 V` nominal OVLO. IC threshold and resistor
tolerances produce approximately `5.353…5.708 V`; the disclosed ±0.1-uA input
leakage widens the paper screen by about ±17 mV to `5.336…5.725 V`. Converter
tolerance and transients must fit that window in HIL.

`TPS259470L` OVLO recovery bypasses the programmed `dVdt` ramp and restarts in
current limit. Software must therefore isolate accessory signals and treat
recovery as a new admission event; it may not infer a normal ramp from EN
remaining high.

The two local 2.2-uF/25-V X7R capacitors exceed TI's close input/output bypass
minima while preserving voltage-rating and DC-bias margin at 5 V. The 1-kOhm
bleeder consumes 5 mA and 25 mW at 5 V. A 470-uF U214 input falls ideally from
5 V to 0.8 V in about `0.86 s`; 560 uF takes about `1.03 s`, while the full
1-mF admitted-profile ceiling would take about `1.83 s`. Removal/reprofile
timing uses the measured connector threshold, not those ideal values.

## Availability and cost snapshot

Exact order-code pages checked on 2026-08-18:

- [RC0402FR-072K21L / LCSC C138019](https://www.lcsc.com/product-detail/C138019.html)
- [GRM155R71H472KA01D / LCSC C77024](https://www.lcsc.com/product-detail/C77024.html)
- [GRM188R71E224KA88D / Mouser](https://www.mouser.com/ProductDetail/Murata-Electronics/GRM188R71E224KA88D)
- [RC0402FR-07169KL / LCSC C327367](https://www.lcsc.com/product-detail/C327367.html)
- [RC0402FR-0747KL / LCSC C93943](https://www.lcsc.com/product-detail/C93943.html)
- [GRM21BR71E225KE11L / LCSC C77081](https://www.lcsc.com/product-detail/C77081.html)
- [RC0603FR-071KL / LCSC C22548](https://www.lcsc.com/product-detail/C22548.html)

The checked 100-piece pricing is approximately `$0.10` per board for all eight
positions together. This does not materially change the device cost class.
Availability is a dated sourcing screen, not production AVL closure.

## Review boundary

The exact passive values, real contacts, calculations, startup/post-start
semantics and machine propagation receive **«Проведено ревью»**.

Still open before schematic/BOM freeze: DC-bias/specimen capacitance, exact
converter tolerance at OVLO, hot/current-limit/fault injection, output-fall
threshold, U214 and generic-profile inrush HIL, high-current copper/return
geometry and the possible need for a connector transient clamp. This document
does not authorize KiCad.
