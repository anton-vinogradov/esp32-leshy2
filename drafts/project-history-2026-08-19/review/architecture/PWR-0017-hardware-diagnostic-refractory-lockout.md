# PWR-0017 — exact hardware diagnostic refractory lockout

- Статус: **Проведено ревью бумажной принципиальной схемы**
- Дата: 2026-08-18
- Corrects: [`PWR-0013`](PWR-0013-exact-pack-diagnostic-frontends.md)
- Decision: [`DEC-0078`](../decisions/DEC-0078-hardware-diagnostic-refractory-lockout.md)
- Finding: [`FND-0082`](../findings/FND-0082-tpul-pin-map-and-repeat-pulse-gap.md)
- Propagation review: [`REV-0005AI`](../reviews/REV-0005AI-diagnostic-lockout-propagation.md)

## Scope

The accepted diagnostic still applies a short 10-Ohm load to the fused raw 2S
stack before the normally-open protection FETs and samples both cell voltages.
This correction makes the physical WQFN contact map buildable and bounds not
only one pulse but also the maximum hardware repetition rate.

It preserves the diagnostic function, current class, ADC contacts and GPIO
budget. It is not full-load proof and cannot authenticate an arbitrary cell.

## Exact package correction

The official TI WQFN-16 transparent top view and pin table give:

| Function | Physical contact |
|---|---:|
| channel-1 falling trigger / rising trigger / clear | 1 / 2 / 3 |
| channel-1 complementary output | 4 |
| channel-2 active-high output | 5 |
| channel-2 C / RC | 6 / 7 |
| ground / exposed pad | 8 / exposed pad |
| channel-2 falling trigger / rising trigger / clear | 9 / 10 / 11 |
| channel-2 complementary output | 12 |
| channel-1 active-high output | 13 |
| channel-1 C / RC | 14 / 15 |
| supply | 16 |

The previous machine record exchanged contacts 5 and 16. The corrected record
and tests now prevent that exact regression.

## Cascaded lockout circuit

Channel 1 remains unchanged in purpose:

- `PA22/A4` drives rising-trigger `1T`; `1T_N` is low;
- `169 kOhm / 220 nF C0G` gives about `34.4 ms` typical;
- production accepts only `25…50 ms`;
- `1Q` alone drives the load MOSFET.

Channel 2 is cascaded at the end of the pulse:

- `1Q` drives falling-trigger `2T_N`;
- `2T` and `2CLR_N` are fixed high;
- the rising edge at pulse start is ignored; the natural falling edge at pulse
  end starts channel 2;
- `2Q_N` drives `1CLR_N`, so channel 1 is asynchronously held inactive for the
  complete channel-2 interval;
- `620 kOhm / 1 uF` sets the refractory interval; `2Q` remains open.

There is no first-pulse race: channel 2 starts only after channel 1 has already
returned inactive. At lockout release, a correctly returned-low MCU line leaves
channel 1 ready. A stuck-high line can use clear release as one trigger, but the
resulting pulse again starts channel 2, so the same hardware rate bound applies.

TI requires a startup wait of `500 × Cext` seconds for first-pulse accuracy.
The largest capacitor therefore needs 0.5 ms; runtime forbids diagnostics until
at least 1 ms after stable admission VDD.

## Timing screen

The TI 3.3-V table gives `918 ms` typical for `1 MOhm / 1 uF`; scaling to the
exact 620-kOhm part gives about `569 ms` typical. The lower paper stack uses:

- `-10%` TPUL pulse-width variation;
- `-1%` resistor initial tolerance and `-1%` temperature allowance;
- `-10%` capacitor initial tolerance and `-15%` X7R temperature characteristic;
- `-5%` allowance from the official TDK low-voltage DC-bias curve.

That gives approximately `360 ms`; the production lower gate is rounded down
to `350 ms`. The corresponding positive component/device corner remains about
`798 ms`, below the TPUL `860 ms` recommended configured maximum. Production
accepts only measured `350…860 ms` over lot and qualified temperature.

## Repetition-safe load

| Qty | Exact MPN | Role |
|---:|---|---|
| 2 | `Bourns CRM2512-FX-20R0ELF` | parallel 20-Ohm ±1%, 2-W, 2512 load branches |
| 1 | `Diodes Incorporated DMN2056U-7` | fail-low low-side switch |
| 1 | `Yageo RC0402FR-07620KL` | 620-kOhm channel-2 timing resistor |
| 1 | `TDK C1608X7R1C105K080AC` | 1-uF 16-V X7R channel-2 timing capacitor |

The parallel branches are `10 Ohm ±1%`. At the conservative 8.8-V screen and
9.9-Ohm minimum, total instantaneous resistor power is about `7.82 W`, or
`3.91 W` per branch. The official CRM2512 pulse curve permits roughly tens of
watts at 50 ms, so the single-pulse margin is large.

Even with a 50-ms pulse followed by only the 350-ms hardware minimum, duty is
at most 12.5% and average total resistor power is about `0.98 W`, or `0.49 W`
per branch. At 125 °C the linear Bourns derating gives about `0.706 W` per part.
The paper circuit therefore remains below the combined hot rating even if
firmware continuously requests pulses. Exact 300-mm² full-rating copper is not
automatically claimed: copper geometry, local heating and enclosure airflow
remain HIL/layout gates.

## HIL-derived droop thresholds

Firmware captures baseline and loaded midpoint/stack samples in one calibrated
sequence after at least 10 ms settling. For each pulse:

- `V0 = Vmid`;
- `V1 = Vstack - Vmid`;
- `Iload` comes from the calibrated effective load and loaded stack voltage;
- each path estimate is `Rpath = (Vbaseline - Vloaded) / Iload`.

The production acceptance numbers must be generated from the exact qualified
cell MPN across state of charge and temperature, plus holder/fuse/contact,
ADC/load calibration and aging margins. Until that prerequisite exists, a
missing, saturated, sign-inconsistent or temporally misaligned sample fails
closed, but no invented universal milliohm limit is allowed.

Normal runtime waits at least 10 seconds between attempts. The exact-cell HIL
profile may lengthen this operational cooldown; it cannot shorten the hardware
350-ms bound or the firmware 10-s floor.

## Availability and cost

The TDK capacitor is in production with broad distributor stock; the Yageo
resistor is active and stocked; the exact Bourns resistor was active with more
than 40k units visible at an authorized distributor. At 100-piece visible
pricing the two Bourns parts plus timer passives add roughly `$0.38` and replace
the old single load part, so the net increase is below roughly `$0.30` before
assembly.

Primary sources:

- [TI TPUL2G223 datasheet](https://www.ti.com/lit/ds/symlink/tpul2g223.pdf)
- [Bourns CRM2512 datasheet and pulse curve](https://www.bourns.com/docs/product-datasheets/CRM.pdf)
- [TDK C1608X7R1C105K080AC product/characterization page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1C105K080AC)
- [Yageo RC0402FR-07620KL exact specification](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07620KL)

## Review result

Correct physical pin provenance, cascaded edge behavior, hardware repetition
bound, exact timer passives and repetition-safe load receive **«Проведено
ревью»** at paper-schematic level. Numeric exact-cell droop limits, lot timing,
hot copper and full insertion/source-handover HIL remain open. This does not
authorize KiCad.

