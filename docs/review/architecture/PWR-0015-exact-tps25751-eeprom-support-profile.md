# PWR-0015 — exact TPS25751D and CAT24C512 support profile

- Статус: **Проведено ревью бумажной принципиальной схемы**
- Дата: 2026-08-18
- Decision: [`DEC-0076`](../decisions/DEC-0076-exact-tps25751-eeprom-support-profile.md)
- Corrected finding: [`FND-0080`](../findings/FND-0080-tps25751-autonomous-start-and-bus-pulls.md)
- Propagation review: [`REV-0005AG`](../reviews/REV-0005AG-tps25751-eeprom-support-profile.md)

## Boundary

This pass closes the component-level paper circuit around exact
`TPS25751DREFR` and `CAT24C512WI-GT3`. It covers autonomous attach/startup,
hardware straps, energy storage, EEPROM power/protection, local and host bus
pull-ups, unused contacts and the sink-only termination. Product connector,
connector-side VBUS/CC protection, USB2 SI and physical placement remain I4.

## Autonomous safe startup

Raw connector VBUS must reach two electrically different TPS pin groups:

1. `VBUS` pins 32/33 power attach detection, safe discharge and the internal
   dead-battery LDO path;
2. `VBUS_IN` pins 23/24/25 feed the protected PPHV switch input;
3. `ADCIN1=LDO_3V3` (decoded 7) and `ADCIN2=GND` (decoded 0) select the TI
   SafeMode row and I2C target address `0x20`;
4. SafeMode keeps PD, PPHV and charging disabled while the TPS loads the
   address-`0x50` EEPROM image without S3 or `3V3_MAIN`;
5. only a valid image may accept a source contract and enable PPHV; BQ25798 CE
   remains pulled high until GPIO1 deliberately sinks it after IINDPM setup;
6. once BQ SYS produces `AON_SAFE_3V3`, TPS `VIN_3V3` moves onto that admitted
   rail. Its 6-mA maximum active load is included in the revised 15-mA
   continuous / 20-mA transient AON paper budget. The later `DEC-0091`
   three-nRF evidence amendment raises the transient reserve to 30 mA without
   changing the selected AON converter or cutoff.

Missing or corrupt EEPROM therefore fails with PPHV and charge off, not with an
uncontrolled 5-V pass-through. Blank/corrupt/raw-VBUS-only behavior remains a
specimen HIL gate because the datasheet contract cannot prove a board layout or
the programmed image.

## Exact physical support instances

| Function | Qty | Exact MPN | Paper value / connection |
|---|---:|---|---|
| VIN_3V3 local capacitor | 1 | `GRM188R60J106ME47D` | 10 uF, 6.3 V, X5R |
| LDO_3V3 local capacitor | 1 | `GRM188R60J106ME47D` | 10 uF; inside 5…25-uF allowed range |
| LDO_1V5 local capacitor | 1 | `GRM188R60J106ME47D` | 10 uF; inside 4.5…12-uF allowed range |
| PPHV bulk | 4 | `GRM32ER71E226KE15L` | 4×22 uF, 25 V, X7R; 88 uF nominal |
| VBUS local capacitor | 1 | `CGA5L1X7R1E475K160AC` | 4.7 uF, 25 V, X7R |
| CC shunts | 2 | `GRM1555C1H221JA01D` | 220 pF, 50 V, C0G; one per protected CC; amended by `DEC-0083` |
| EEPROM bypass | 1 | `C1005X7R1H104K050BB` | 100 nF, 50 V, X7R |
| EEPROM WP pull-up | 1 | `RC0402FR-0710KL` | 10 kOhm to LDO_3V3 |
| TPS local-I2C pull-ups | 2 | `RC0402FR-072K2L` | 2.2 kOhm SCL and SDA to LDO_3V3 |
| S3 host-I2C pull-ups | 2 | `RC0402FR-072K2L` | 2.2 kOhm SCL and SDA to 3V3_MAIN |
| shared host IRQ pull-up | 1 | `RC0402FR-0710KL` | 10 kOhm to 3V3_MAIN |

These are 17 separately instantiated physical components. Four PPHV
capacitors deliberately reuse an existing 25-V BOM line. PPHV effective
capacitance at the accepted 15-V maximum, CC total capacitance including
protector, route and connector, and startup overshoot remain layout/lot/HIL
checks. `USB-0001/DEC-0083` later replaces the original 330-pF first targets
with the current 220-pF parts after adding exact four-line protection.

The earlier charger-only 10-kOhm SCL/SDA pulls were not valid for the complete
TPS + EEPROM + BQ bus. They are replaced, not paralleled, by the exact 2.2-kOhm
pair. Charger INT and CE keep their separate 10-kOhm pull-ups.

## First image and recovery

TI's FLxx host-update sequence preserves and replaces a previously initialized
region; it is not the authority for initializing a blank EEPROM. Production
therefore has two allowed first-image paths:

1. program and verify `CAT24C512WI-GT3` before placement; or
2. power the assembled TPS from a current-limited raw 5-V VBUS fixture, observe
   `ReadyForPatch` on I2Ct after the blank/corrupt boot attempt, verify I2Cc is
   high-Z, sink WP and program the EEPROM through direct SDA/SCL pads.

The fixture never injects 3.3 V into TPS `LDO_3V3`; doing so would turn an LDO
output into an unreviewed back-power path. S3 and `3V3_MAIN` are not required.
The direct path must abort on any I2Cc activity or unexpected PPHV/CE state.
First-image headers, full readback, power-cycle boot and recovery from each
corrupt region are production/HIL acceptance cases.

## Exact straps and terminations

- `PP5V` is grounded: the accepted product is sink-only and provides neither
  source power nor VCONN.
- CAT24 `A0/A1/A2` and `VSS` are grounded; `VCC` comes from TPS `LDO_3V3`.
- TPS GPIO0 is open-drain. The resistor holds WP high at reset; only the signed,
  authorized update flow may sink it.
- GPIO2, GPIO3, GPIO6, GPIO7, GPIO11 and the already unused GPIO4/5 functions
  are grounded per the exact pin contract.
- GND pins 11/12/14/31 and the exposed GND pad join the local ground plane.
- DRAIN pins 15/30 and the exposed DRAIN pad join one local high-current thermal
  copper island; that island is not ground.

## Availability and cost screen

The three newly introduced BOM lines are active and visibly orderable as of
2026-08-18: `GRM188R60J106ME47D`, current amended
`GRM1555C1H221JA01D` and
`RC0402FR-072K2L`. Reused PPHV bulk dominates the incremental material. The
visible 100-to-reel screen is approximately `$1.15…1.45` per board; factory
quote, alternates and landed cost remain I8. This is not a dramatic BOM change.

Primary/reference sources:

- [TI TPS25751 Rev-A datasheet](https://www.ti.com/lit/ds/symlink/tps25751.pdf)
- [TI TIDA-050047 reference design](https://www.ti.com/lit/pdf/TIDUEY1)
- [TI EEPROM update over I2C application note](https://www.ti.com/lit/an/slvafl1/slvafl1.pdf)
- [TI clarification: a blank EEPROM requires initial programming](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1457483/tps25751-tps25751-and-tps26750-eeprom-update-over-i2c)
- [onsemi CAT24C512 datasheet](https://www.onsemi.com/download/data-sheet/pdf/cat24c512-d.pdf)

## Review result

The exact autonomous-start path, SafeMode straps, 17 physical support
components, unused-contact terminations, EEPROM protection and both complete
bus pull networks receive **«Проведено ревью»** at paper-schematic level.
Connector parasitics/protection, DC-bias and layout, blank-image boot, attach,
source transition, recovery and fault injection remain explicit HIL/I4 gates.
This does not authorize KiCad.
