# PWR-0014 — exact BQ25798 inductor, passive and reset-default profile

- Статус: **Проведено ревью бумажной принципиальной схемы**
- Дата: 2026-08-18
- Parent frontend: [`PWR-0004`](PWR-0004-accepted-usb-pd-front-end.md)
- Decision: [`DEC-0075`](../decisions/DEC-0075-exact-bq25798-passive-profile.md)
- Corrected dependency: [`FND-0079`](../findings/FND-0079-product-usb-is-an-i4-consumer.md)
- Propagation review: [`REV-0005AF`](../reviews/REV-0005AF-bq25798-passive-profile.md)

## Scope and real-device revision

This pass turns the accepted `BQ25798RQMR` block into a complete paper-level
single-input, no-ship-FET, no-backup-mode 2S converter. It uses the current TI
Rev-C datasheet (`SLUSDV2C`, revised June 2026), not an older application
diagram. Three details matter:

- both `VAC1` and `VAC2` connect to `VBUS` when their external ACFET/RBFET
  pairs are absent; `ACDRV1/2` tie to ground;
- unused `SDRV` requires exactly `1 nF`, `50 V`, `0402` to ground; the older
  alternative connection is not used;
- POR charging is now documented as `1 A`; an `8.2 kOhm` PROG strap selects
  `2S`, `750 kHz`, `7.0 V VSYSMIN` and `8.4 V VREG`.

`D+`, `D-`, `QON` and disabled open-drain `STAT` are no-connects. Product USB2
therefore remains direct to S3 and belongs to `I4`, not this circuit.

## Frequency and inductor proof

The accepted physical default is `750 kHz` with one exact
`MWSA0503S-2R2MT`: `2.2 uH ±20%`, `29 mOhm` maximum DCR, `7 A` current and
saturation ratings, `5.4 × 5.2 × 3.0 mm`. TI explicitly pairs 750 kHz only
with 2.2 uH and describes it as the higher-efficiency choice when space permits.

At minimum inductance `1.76 uH`:

- the approximately worst 15-V-to-7…8.6-V buck ripple is `<2.85 A p-p`;
- even the BQ device-limited 5-A average path remains below about `6.43 A`
  peak (`5 A + ripple/2`), leaving paper margin to the 7-A rating;
- the accepted 30-W source and `<=2 A` charge policy normally impose a lower
  average current; saturation, DCR heating and acoustic/EMI behavior remain
  prototype gates.

The choice reuses the same active Sunlord family and footprint envelope as the
existing main/voice/accessory inductors. It does not remove a performance mode;
1.5 MHz/1 uH is rejected because it trades more switching loss and EMI for
smaller magnetics that the current enclosure does not require.

## Exact energy components

Every quantity below is represented by separate physical machine/diagram
instances.

| Node | Qty | Exact MPN | Accepted role |
|---|---:|---|---|
| VBUS | 2 | `Murata GRM31CR71E106MA12L` | 10-uF 25-V X7R bulk input |
| VBUS | 1 | `TDK C1005X7R1H104K050BB` | 100-nF 50-V HF bypass |
| PMID | 3 | `Murata GRM31CR71E106MA12L` | 10-uF 25-V X7R switching input bank |
| PMID | 1 | `TDK C1005X7R1H104K050BB` | 100-nF 50-V HF bypass |
| SYS | 5 | `Murata GRM31CR71E106MA12L` | 10-uF 25-V X7R boost/output bank |
| SYS | 1 | `TDK C1005X7R1H104K050BB` | 100-nF 50-V HF bypass |
| BAT | 2 | `Murata GRM31CR71E106MA12L` | 10-uF 25-V X7R pack-side bank |
| BTST1/2 | 2 | `Murata GRM155R71E473KA88D` | independent 47-nF 25-V X7R bootstrap capacitors |
| REGN | 1 | `TDK CGA5L1X7R1E475K160AC` | 4.7-uF 25-V X7R regulator bypass |
| SDRV | 1 | `KEMET C0402C102K5RACTU` | exact 1-nF 50-V X7R no-ship-FET termination |

The twelve identical 1206 bulk capacitors deliberately favor voltage-bias
margin and one common MPN over the smallest reference-BOM packages. Nominal
banks exceed the datasheet effective-capacitance minima; DC-bias, ripple and
placement are still verified on the real PCB. Backup-mode `2 × 33 uF` POSCAP,
the >15-V adapter hot-plug option and the long-lead 4S BAT option are omitted
because all three functions are outside the accepted product envelope.

## Exact configuration and sensing

| Function | Exact components | Paper result |
|---|---|---|
| POR | `RC0402FR-078K2L`, 8.2 kOhm 1% | 2S, 750 kHz, 1-A safe reset charge, 7.0-V VSYSMIN, 8.4-V VREG |
| BATP | `RC0402FR-07100RL`, 100 Ohm 1% | required series sense connection to the admitted pack positive |
| TS | `RC0402FR-075K23L` 5.23 kOhm, `RC0402FR-0730K1L` 30.1 kOhm, third `B57332V5103F360` 10-kOhm NTC | direct non-ignored BQ temperature gate, nominally close to the 0/10/45/60°C JEITA points |
| ILIM | `RC0402FR-0744K2L` 44.2 kOhm over `RC0402FR-07100KL` 100 kOhm | about 2.91 A at 4.8-V REGN and 3.08 A at 5.0 V; 2.71…3.29 A over specified REGN and 1% resistor corners |
| local I2C/IRQ | 2 × `RC0402FR-072K2L`; 1 × `RC0402FR-0710KL` | complete-bus SCL/SDA 2.2-kOhm pull-ups and separate INT 10-kOhm pull-up to TPS `LDO_3V3`; corrected by `FND-0080/DEC-0076` |
| charge default | 1 × `RC0402FR-0710KL` | CE pulled high to BQ REGN; TPS GPIO1 is open-drain and can only sink it after valid policy |

The external ILIM divider is a hardware ceiling, not source negotiation. BQ
uses the lower of this pin and its IINDPM register. TPS must first establish
the actual 5/9/15-V contract, write the corresponding current limit and only
then sink CE. Weak/default-current sources therefore receive a lower register
limit even though the physical ceiling preserves the accepted 9-V/3-A path.

The third NTC is independent: neither existing MAX17320 cell thermistor is
electrically shared with BQ TS. Its `B25/50=3380 K` characteristic with the
selected divider gives approximately `73.6% REGN` at 0°C, `68.4%` at 10°C,
`44.8%` at 45°C and `34.9%` at 60°C. Exact mechanical coupling to the
representative hottest cell/holder interface remains the next I3 mechanical
gate; firmware may make the charge window stricter but never set `TS_IGNORE`.

## Reset, fault and runtime contract

1. Before a valid PD image, GPIO1 is Hi-Z and the REGN pull-up holds CE high.
2. With a valid contract, TPS writes BQ IINDPM, reads it back, then sinks CE.
3. POR or watchdog reset restores the 2S physical profile and 1-A charge
   current; runtime may raise charge only to the accepted `<=2 A` ceiling and
   only inside source, load, cell and temperature budgets.
4. Source loss, TS fault, invalid pack state, missed charger status or
   out-of-envelope PDO releases CE and blocks re-enable until state is read
   back. OTG, backup, MPPT, BC1.2 and source modes stay disabled.
5. `INT` carries status/fault pulses to TPS; `STAT` is disabled and unconnected.

## Availability and cost snapshot

Checked 2026-08-18 because ten new exact BOM lines are selected. The Sunlord
inductor was active with 3,014 DigiKey units and also exists as JLC/LCSC
`C408408`; visible pricing was about `$0.85` single / `$0.446` reel. The exact
KEMET 1-nF capacitor had more than 2.6 million DigiKey units; the exact Murata
47-nF capacitor had active distributor stock. The resistor order codes were
active and stocked, including over 45k of the 5.23-kOhm part and millions of
the 100-Ohm part. Exact 10-uF orderability was confirmed at authorized
distribution.

The new/passive charger material is approximately `$1.7…2.3` per board at
100-to-reel visible prices, dominated by twelve conservative 1206 bulk
capacitors and the inductor. Factory quote, effective-capacitance lot data and
alternate qualification remain `I8`; there is no dramatic BOM increase.

Primary/reference sources:

- [TI BQ25798 Rev-C datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf)
- [TI TIDA-050047 schematic](https://www.ti.com/lit/pdf/TIDM748) and
  [reference BOM](https://www.ti.com/lit/pdf/TIDM749)
- [TI TPS25751 datasheet](https://www.ti.com/lit/ds/symlink/tps25751.pdf)
- [Sunlord MWSA-S series](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf)
- [Murata GRM31CR71E106MA12L](https://www.murata.com/en-us/products/productdetail?partno=GRM31CR71E106MA12L)
- [TDK B57332V5103F360](https://product.tdk.com/en/search/sensor/ntc/chip-ntc-thermistor/info?part_no=B57332V5103F360)

## Review result

The exact BQ inductor, 19 capacitor instances, ten resistor instances, third
NTC, all previously omitted special-pin terminations and the reset/runtime
contract receive **«Проведено ревью»** at paper-schematic level. Placement,
thermal/EMI/source-transition tests and NTC mechanics remain HIL. Exact
TPS25751/CAT24C512 surrounding passives later close in
`PWR-0015/DEC-0076/REV-0005AG`; `FND-0080` replaces the provisional
charger-only bus pulls with the complete-bus values. This does not authorize
KiCad.
