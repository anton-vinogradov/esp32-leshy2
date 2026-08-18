# PWR-0013 — exact bounded pack load and admission ADC frontends

- Статус: **Заменено корректирующим PWR-0017; не использовать как текущую схему**
- Дата: 2026-08-18
- Parent circuit: [`PWR-0007`](PWR-0007-max17320-2s-surrounding-circuit.md)
- Decision: [`DEC-0074`](../decisions/DEC-0074-bounded-pack-diagnostic-pulse.md)
- Corrected finding: [`FND-0078`](../findings/FND-0078-mspm0-pa24-forbids-injection-current.md)
- Propagation review: [`REV-0005AE`](../reviews/REV-0005AE-pack-diagnostic-profile.md)

> `PWR-0017/DEC-0078/FND-0082` correct the WQFN physical map, replace the
> firmware-only repetition assumption with a second-channel hardware lockout
> and replace the single 1-W load. This file remains only as review history.

## Scope

This pass replaces the abstract pre-admission load, both abstract ADC dividers
and their paper-only GPIO claims with exact physical components and routes.
The owner accepted a `10 Ohm` diagnostic load with an independent hardware and
firmware pulse limit of at most `50 ms`.

The diagnostic is a short common-path screen for two cells, both holder
contacts and both slot fuses before the normally-open CHG/DIS pair. It is not a
full `2.78 A` product-load proof, does not recover a rejected cell and does not
change the no-deep-cell-recovery boundary.

## Real-device correction before selection

The exact MSPM0C1104 DGS-20 package exposes `PA24/A3`, `PA25/A2` and
`PA26/A1`, but the TI datasheet permits no injection current on PA24. Because
the raw battery dividers can remain energized while admission VDD is absent,
the old PA24 midpoint assignment was invalid even with a high-value divider.

The corrected allocation is:

| Evidence | Exact contact | Physical pin | Result |
|---|---|---:|---|
| fused 2S midpoint | `PA25/A2` | 20 | lower-cell evidence |
| fused full stack | `PA26/A1` | 1 | upper cell = stack minus midpoint |
| released contact | `PA24/A3` | 19 | free; no battery-derived analog source |

The budget is unchanged at `12 used / 3 service-reserved / 3 free`.

## Bounded load circuit

| Qty | Exact MPN | Role |
|---:|---|---|
| 1 | `Texas Instruments TPUL2G223BQBR` | dual non-retriggerable RC one-shot; channel 1 is the hardware pulse authority |
| 1 | `Yageo RC0402FR-07169KL`, 169 kOhm 1% | channel-1 timing resistor |
| 1 | `Murata GRM31C5C1H224JE02L`, 220 nF 5% C0G | channel-1 timing capacitor |
| 1 | `TDK C1005X7R1H104K050BB`, 100 nF X7R | one-shot local VCC bypass |
| 2 | `Yageo RC0402FR-0710KL`, 10 kOhm 1% | reset-low trigger and fail-low MOSFET gate |
| 1 | `Diodes Incorporated DMN2056U-7` | 20-V low-gate-drive N-MOS low-side switch |
| 1 | `Vishay CRCW251210R0JNEGIF` | 10-Ohm ±5%, 1-W, 2512 pulse-proof load |

`PA22/A4` is no longer a level-enable. It emits a rising edge into channel 1
of TPUL2G223. The channel is non-retriggerable, so another edge during the
active interval is ignored and a stuck-high GPIO cannot extend the pulse.
`Q` alone drives the DMN2056U gate. Independent trigger and gate pull-downs
keep the load off during reset, admission-VDD loss and fixture handover.

The unused second one-shot channel is held asynchronously clear; every unused
input is tied low, both push-pull outputs are open, and it has no RC network.

### Timing bound

At the admission supply, the TI characteristic factor gives approximately
`34.4 ms` typical for `169 kOhm × 220 nF`. The timing capacitor is a dedicated
C0G part rather than the X7R used by the accessory transient timer, because a
loaded ADC sample requires both ends of the pulse window to be bounded. The
deliberately stacked screen uses:

- ±10% TPUL pulse-width variation across specified operation;
- ±1% timing-resistance initial tolerance and ±1% conservative temperature
  allowance from its specified TCR;
- ±5% C0G initial capacitance;
- ±0.3% C0G temperature change over the worst 100-degree offset from 25 °C.

This gives a conservative paper window of approximately `28.7…40.7 ms`:

- lower: `34.4 ms × 0.90 × 0.99 × 0.99 × 0.95 × 0.997 = 28.7 ms`;
- upper: `34.4 ms × 1.10 × 1.01 × 1.01 × 1.05 × 1.003 = 40.7 ms`.

C0G removes the material X7R DC-bias/aging ambiguity from the timing proof.
Production HIL must measure the actual lot/temperature envelope and accept
only `25…50 ms`; the lower screen guarantees that the `>=10 ms` filtered loaded
sample is still captured during the pulse, while the upper screen preserves
the owner-accepted safety ceiling.

At the `6.0…8.4 V` working stack and ±5% load-resistor tolerance, the screened
current is approximately `0.57…0.88 A`. At 8.4 V nominal, the resistor sees
about `7.06 W` and `0.353 J` for the full 50-ms ceiling. The official Vishay
single-pulse curve for the 2512 pulse-proof family retains margin at 50 ms;
board copper, repetition/cooldown and enclosure temperature remain HIL gates.
The DMN2056U adds at most about 85 mOhm at 1.5-V gate drive and dissipates far
less than the resistor during the pulse.

## ADC divider profile

Both inputs use the MSPM0 internal `1.4 V` reference, whose specified minimum
is `1.378 V`. High-side resistors are split into repeated physical 220-kOhm
parts. This reduces unique BOM lines and limits fault current without claiming
that one resistor is a redundant safety barrier.

| Input | Exact network | Nominal at working maximum | Worst paper screen |
|---|---|---:|---:|
| midpoint `PA25/A2` | `2 × 220 kOhm` top, `169 kOhm` bottom, `10 nF` to local ground | 1.166 V at 4.2 V | 1.211 V at 4.3 V and 1% corners |
| stack `PA26/A1` | `5 × 220 kOhm` top, `169 kOhm` bottom, `10 nF` to local ground | 1.119 V at 8.4 V | 1.165 V at 8.6 V and 1% corners |

The exact filter capacitors are two independent
`Murata GRM155R71H103KA88D`. Divider current is about `6.90 uA` midpoint and
`6.62 uA` stack. Thevenin resistance is approximately 122 kOhm and 147 kOhm;
the MSPM0 50-nA maximum digital-pin leakage therefore corresponds to about
6.1 mV and 7.4 mV at the ADC node before calibration.

The RC time constants are approximately 1.22 ms and 1.47 ms. Runtime must wait
at least 10 ms after a relevant edge before treating either reading as settled,
use the internal reference, and sample baseline and loaded values with one
calibrated sequence. Production droop/contact thresholds, ADC acquisition
settings, temperature compensation and repeated-pulse cooldown remain HIL
outputs rather than invented constants.

## Availability and cost

TPUL2G223BQBR is listed by TI as active production and orderable in WQFN-16.
DMN2056U-7 and CRCW251210R0JNEGIF are active and had distributor stock when
selected. The 10-nF filters are active stocked Murata parts. All other timing,
bypass, pull and divider values reuse exact MPNs already present in the board
BOM.

Checked new material other than the timer is below roughly `$0.60` per board
at reel pricing before assembly. The fresh TI timer price and CM sourcing quote
must be refreshed at BOM freeze because it entered production in 2026. No GPIO
is added and the analog correction only moves the existing two measurements.

Primary sources:

- [TI MSPM0C1104 datasheet](https://www.ti.com/lit/ds/symlink/mspm0c1104.pdf)
- [TI TPUL2G223 datasheet](https://www.ti.com/lit/ds/symlink/tpul2g223.pdf)
- [TI TPUL2G223BQBR orderable page](https://www.ti.com/product/TPUL2G223/part-details/TPUL2G223BQBR)
- [Diodes DMN2056U datasheet](https://www.diodes.com/datasheet/download/DMN2056U.pdf)
- [Vishay D/CRCW-IF pulse-proof datasheet](https://www.vishay.com/docs/20024/dcrcwife3.pdf)
- [Murata GRM155R71H103KA88D product page](https://www.murata.com/en-global/products/productdetail?partno=GRM155R71H103KA88D)
- [Murata GRM31C5C1H224JE02L product page](https://www.murata.com/en-us/products/productdetail?partno=GRM31C5C1H224JE02%23)

## Review result

Exact load resistor, MOSFET, independent non-retriggerable cutoff, fail-low
pulls, timing/bypass parts, two corrected ADC contacts, nine divider resistors
and two filters receive **«Проведено ревью»** at paper-schematic level.
Thresholds, cooldown, pulse-lot characterization, ADC calibration, insertion,
removal and source-handover HIL remain open. This does not authorize KiCad.
