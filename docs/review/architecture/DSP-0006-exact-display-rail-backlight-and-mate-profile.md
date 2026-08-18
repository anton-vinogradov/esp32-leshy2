# DSP-0006 — exact display rail, backlight and first mate profile

> Amended by `DEC-0086/UI-0001`: the previously direct TP_INT route is moved
> through a polarity adapter into shared GPIO37; GPIO39/47 now serve encoder
> PCNT0. Display power, reset, QSPI, connector and backlight conclusions remain.

- Status: **Проведено ревью paper electrical endpoint; physical mate and HIL open**
- Finding: [`FND-0088`](../findings/FND-0088-display-endpoint-still-contained-abstract-circuits.md)
- Decision: [`DEC-0084`](../decisions/DEC-0084-exact-protected-display-electrical-endpoint.md)
- Prior contact fit: [`DSP-0005`](DSP-0005-hmx035ctft-electrical-fit.md)
- Machine source: `hardware/architecture/devices.json` and
  `hardware/architecture/candidates/G2F-3I.json`

## Reviewed boundary

The source assembly remains exact marking `HMX035CTFT-001`, 3.5-inch portrait
320×480 IPS, ST77922 QSPI plus integrated I2C touch. The official QDtech
reference reports 120 mA backlight current and about 198 mA / 0.97 W for the
complete reference display-only state. It is still a disclosed assembly
marking, not yet a proven standalone orderable panel.

## Exact physical parts

| Function | Exact MPN | Reviewed role |
|---|---|---|
| first panel-mate candidate | `Hirose FH12-40S-0.5SH(55)` | 40 positions, 0.5-mm pitch, bottom contact, 0.30-mm FPC, 2.0-mm height, active and stocked |
| backlight branch switch | `TI TPS2553DRVR-1` | active-high, reverse-blocking, latch-off overcurrent/thermal switch |
| current-limit resistor | `Yageo RC0402FR-07133KL` | 133 kOhm, 1%; TI table gives about 174…234 mA including resistor corners around 200 mA nominal |
| LEDK series resistor | `Panasonic ERJ-P08F10R0V` | 10 Ohm, 1%, 1206, 0.66 W, anti-surge; replaces the generic 10-Ohm reference part |
| PWM transistor | `Diodes DMN2056U-7` | exact low-gate-drive N-MOSF, LEDK low-side sink |
| gate series | `Yageo RC0402FR-07100RL` | 100 Ohm, 1%, limits GPIO40 gate edge/ringing |
| reset/gate/fault pulls | 4 × `Yageo RC0402FR-0710KL` | separate display reset, touch reset, MOSFET gate and fault pull positions |
| local bulk | 2 × `Murata GRM188R60J106ME47D` | one 10-uF panel-logic bank and one 10-uF protected-LEDA bank |
| local HF bypass | 3 × `TDK C1005X7R1H104K050BB` | panel logic, eFuse input and protected-LEDA output |

The checked material delta excluding the panel is approximately USD 2.5…2.9
at quantity 100; the already-required FPC connector dominates. Protection,
MOSFET and passives stay below approximately USD 1. No GPIO is added.

## Power topology and rejected whole-panel switch

`VDDI`, `VDD` and `IM1` come directly from protected `3V3_MAIN` with one
10-uF and one 100-nF local capacitor. ST77922 permits VDD/VDDI application and
removal in either order, so the common source is conservative.

A separate latch switch on all panel logic is deliberately rejected. When it
opened, live QSPI/I2C/reset signals could inject current into the unpowered
panel. Preventing that would require qualified isolation of at least six QSPI
conductors, the I2C branch and reset signals. The resulting cost, delay and
failure surface do not buy a proportional benefit because `3V3_MAIN` already
has latch-off containment.

Only `LEDA` passes through `TPS2553DRVR-1`. Its `EN` is hardware-high from
`3V3_MAIN`; 133 kOhm at `ILIM` sets about 200 mA nominal, above the 120-mA
reference backlight. A persistent overcurrent latches the branch off after the
device deglitch. Recovery requires a main-power cycle; no auto-retry network is
present. `FAULT_N` has an exact 10-kOhm pull-up and fixture test point, but
does not consume S3 GPIO.

The three `LEDK` contacts join before `ERJ-P08F10R0V`, then reach the drain of
`DMN2056U-7`; source returns locally to ground. At 120 mA the 10-Ohm resistor
dissipates about 0.144 W, well below its 0.66-W rating. GPIO40 drives the gate
through 100 Ohm and a separate 10-kOhm pull-down holds the backlight off during
reset.

## Reset and interface contract

- TCA6424 `P06` drives display `RESX`; a physical 10-kOhm pull-down asserts it
  while the expander output is reset/high-impedance.
- TCA6424 `P07` drives `TP_RESXP` with its own physical 10-kOhm pull-down.
- Both pulses are at least 10 us. After display reset release, firmware waits
  at least 120 ms before `Sleep Out`; after touch reset release it waits at
  least 100 ms before touch transactions.
- Controlled shutdown sends `Sleep In`, asserts both resets, turns GPIO40 off
  and then permits main power removal. Uncontrolled battery removal remains a
  specified non-damaging ST77922 case, not a promise of retained UI state.
- Existing SYS_I2C 2.2-kOhm pull-ups are the only populated touch pull-ups.
  QDtech's reference 10-kOhm pair is not duplicated.
- `TP_INT` reaches S3 GPIO39 without an assumed board pull. Output type,
  polarity and idle state are specimen-HIL gates.
- QSPI source-series and shunt-tuning footprints are reserved DNP. Values
  enter the populated BOM only after shared display/microSD RC, high-Z and
  contention measurements.

## Connector maturity

`FH12-40S-0.5SH(55)` is an exact, active and stocked **first qualification
candidate**, not the final mate. Its 40 electrical contacts are mapped 1:1 in
the machine source so the paper circuit is complete. The following evidence is
still mandatory before footprint freeze:

1. obtain a real `HMX035CTFT-001` specimen or a supplier-controlled tail
   drawing;
2. measure tail pitch/thickness and photograph conductor side and stiffener;
3. prove insertion direction, latch closure, retention and 20-cycle service;
4. prove installed bend radius/envelope and display replacement access;
5. continuity-map all 40 contacts before power.

## Remaining HIL

- standalone panel identity, orderability, lifecycle and lot consistency;
- connector mate/orientation/retention and installed mechanics;
- QSPI timing at the selected clock, shared-SPI CS-high high-Z and contention;
- touch interrupt electrical type/polarity and reset/recovery;
- LED current corners, PWM flicker/EMI, thermal map and latch recovery;
- internal-FPC ESD and enclosure abuse boundary.

These gates block final connector/footprint and target-architecture freeze, but
not the reviewed paper electrical endpoint.

## Primary sources

- [QDtech ES3C35P official resource index](https://www.lcdwiki.com/res/ES3C35P/)
- [QDtech ES3C35P official schematic](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf)
- [Elecrow/QDtech 3.5-inch ESP32-S3 specification](https://www.elecrow.com/download/product/DLE06235B/3.5inch_IPS_ESP32-S3_Specification.pdf)
- [ST77922 specification hosted by Espressif](https://dl.espressif.com/AE/esp-iot-solution/ST77922_SPEC_V0.1.pdf)
- [Hirose FH12-40S-0.5SH(55) exact product page](https://www.hirose.com/product/p/CL0586-0527-7-55?lang=en)
- [TI TPS2553DRVR-1 exact product page](https://www.ti.com/product/TPS2553-1/part-details/TPS2553DRVR-1)
