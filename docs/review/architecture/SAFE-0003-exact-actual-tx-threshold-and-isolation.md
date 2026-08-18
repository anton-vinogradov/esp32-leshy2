# SAFE-0003 — exact actual-TX threshold and domain-isolation circuit

- Статус: **Проведено ревью paper electrical scope; measured calibration/HIL open**
- Finding: [`FND-0110`](../findings/FND-0110-actual-tx-thresholds-and-aon-boundary-were-abstract.md)
- Decision: [`DEC-0101`](../decisions/DEC-0101-exact-actual-tx-threshold-and-domain-isolation.md)
- Propagation review: [`REV-0005BG`](../reviews/REV-0005BG-actual-tx-threshold-propagation.md)

## Primary facts

- TI specifies `TLV1824PWR` as a quad 2.4…40-V open-drain comparator and calls
  for a local 0.1-uF low-ESR bypass. Its inverting-comparator hysteresis
  example uses detector at IN−, threshold at IN+, R1 from supply, R2 to ground
  and R3 from output; with open drain, the pull-up participates in the high
  threshold and should be at least ten times lower than R3.
- `LTC5532ES6#TRMPBF` has approximately 120-mV typical, 155-mV maximum
  no-RF output in gain-2 topology.
- `AD8314ACPZ-RL7` V_UP is approximately 0.01…1.2 V over its useful range and
  remains at most about 0.05 V with no signal.
- The accepted IR TIA has a nominal 0.30-V dark reference, so it cannot reuse a
  threshold whose calculated clear point is approximately 0.297 V.
- `TCA9534APWR` accepts 1.65…5.5 V and selects address 0x38 when A2/A1/A0 are
  connected directly low.
- `SN74LVC3G07DCUR` is an ACTIVE triple non-inverting open-drain buffer with
  Ioff partial-power-down support. Exact DCU contacts are 1A/1Y=1/7,
  2A/2Y=3/5, 3A/3Y=6/2, GND=4 and VCC=8.

Primary sources:

- [TI TLV1824 Rev. E datasheet](https://www.ti.com/lit/ds/symlink/tlv1824.pdf)
- [ADI LTC5532 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/5532f.pdf)
- [ADI AD8314 Rev. C datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8314.pdf)
- [TI TCA9534A Rev. C datasheet](https://www.ti.com/lit/ds/symlink/tca9534a.pdf)
- [TI SN74LVC3G07 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc3g07.pdf)

## First threshold population

Every channel is a separate physical four-resistor network:

- `R1`: AON_SAFE_3V3 → IN+;
- `R2`: IN+ → SAFETY_GROUND;
- `R3`: comparator OUT → IN+;
- `RPU`: AON_SAFE_3V3 → comparator OUT;
- detector/TIA output → IN−.

For open output, `R1` is in parallel with `RPU+R3`. For low output, `R2` is in
parallel with `R3`. At nominal 3.3 V:

| Channels | R1 | R2 | R3 | RPU | rising assert | falling clear | nominal hysteresis |
|---|---:|---:|---:|---:|---:|---:|---:|
| S3, C5, nRF0, nRF1, nRF2, CC, voice | 100 kΩ | 10 kΩ | 1 MΩ | 10 kΩ | 0.327 V | 0.297 V | 29.5 mV |
| IR optical | 100 kΩ | 12 kΩ | 1 MΩ | 10 kΩ | 0.384 V | 0.350 V | 34.7 mV |

Exact first targets are reused active/orderable project lines:
`RC0402FR-07100KL`, `RC0402FR-0710KL`, `RC0402FR-0712KL` and
`RC0402FR-071ML`. The RF clear point remains well above the documented
no-signal floors. The IR clear point leaves about 50 mV nominal headroom over
the accepted dark reference.

These values only make the first PCB population deterministic. Production
values remain outputs of conducted/optical measurements across accepted
bands, power levels, temperature and lots.

## Comparator and source-mask support

Each `TLV1824PWR` is powered from `AON_SAFE_3V3`, returns to
`SAFETY_GROUND`, and has its own `C1005X7R1H104K050BB` 100-nF local bypass.
Every open-drain output has its own physical 10-kOhm AON pull-up; no prose-only
or shared substitute remains.

`TCA9534APWR` is likewise AON-powered and locally bypassed. A2/A1/A0 connect
directly to safety ground for 0x38. SDA/SCL connect to RP GPIO28/GPIO29 on the
local side of TCA4307; the already-instantiated 2.2-kOhm controller-side bus
pull-ups are on `3V3_MAIN`. Main power cannot be present without a valid AON
rail, and the local bus is not exported through the mask. INT remains a
protected/testable point but is not part of the safety claim.

## AON aggregate and main-domain isolation

Four `BAT54ALT1G` pairs diode-OR EV_N0…EV_N7 into `ANY_TX_AON_N`.
`RC0402FR-0710KL` pulls this node high independently of indicator leakage.
`RC0402FR-072K2L + LTST-C190KRKT` form the firmware-independent physical
indicator branch.

One AON-powered `SN74LVC3G07DCUR` transfers three read-only signals:

| Buffer channel | AON input | passive-drain output | main-domain pull-up/consumer |
|---|---|---|---|
| 1 | `EV_N1_C5` | `C5_RF_TX_EVIDENCE_N` | 10 kΩ to 3V3_MAIN, C5 GPIO23 |
| 2 | `EV_N7_IR` | `IR_TX_EVIDENCE_N` | 10 kΩ to 3V3_MAIN, C5 GPIO24 |
| 3 | `ANY_TX_AON_N` | `RP_ANY_TX_N` | 10 kΩ to 3V3_MAIN, RP GPIO22 |

Non-inverting open-drain transfer preserves the accepted active-low runtime
meaning. When main power is absent, all three outputs are passive/high-Z and
there is no positive AON source into C5 or RP. The existing separate
`SN74LVC1G07DCKR` S3-evidence path to TCA6424 P23 remains unchanged.

## HIL exit

- Measure every RF threshold, hysteresis, assert and decay at every accepted
  band/power edge, temperature corner and representative detector/coupler lot.
- Prove no false negative at minimum permitted TX and no false positive in
  quiet/receive states or from the selected neighbouring group fixture.
- Measure IR dark/ambient/tunnel-coupled distributions and duty-cycle edges.
- Inject AON-only, main-only transition, brownout and reset cases; prove no
  C5/RP back-power and correct active-low state.
- Confirm TCA9534A address/readback, local-bus timing and source identity.
- Recalculate first population only through a reviewed machine-source change;
  no bench bodge becomes an undocumented production value.

