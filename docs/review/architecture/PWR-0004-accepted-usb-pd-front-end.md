# PWR-0004 — accepted sink-only USB-PD frontend

> Later allocation: the frontend still consumes no dedicated GPIO;
> `DEC-0086` subsequently uses the former GPIO47 reserve for encoder phase B.

- Статус: **Проведено ревью exact paper fit; electrical/HIL остаток отделён**
- Дата: 2026-08-18
- Decision: [`DEC-0063`](../decisions/DEC-0063-sink-only-30w-usb-pd-power-path.md)
- Finding corrected: [`FND-0074`](../findings/FND-0074-tps25751-requires-external-boot-image.md)

## Accepted contract

| Property | Accepted value |
|---|---|
| USB role | sink only; never source/power bank |
| fixed PDOs | 5-V fallback at advertised Type-C current (max 3 A), 9 V/3 A, 15 V/2 A |
| maximum | 30 W; 20-V and PPS disabled |
| USB2 | S3 GPIO19/20 direct to product receptacle |
| first charge limit | <=2 A until exact cell/thermal qualification |
| controller boot | autonomous dedicated EEPROM before S3 is assumed |
| failure state | no high-voltage negotiation and charge held disabled |

The 30-W number is an input contract, not a continuous load promise. Existing
12-W continuous/15-W transient device-load planning remains the starting
thermal envelope; spare input power may charge the accepted pack only inside
source, cell and temperature limits.

## Exact selected devices and real exposed contacts

| Physical device | Package/contact facts | Role |
|---|---|---|
| `TPS25751DREFR` | 38-pin REF QFN, 4×6 mm; VBUS_IN 23–25, PPHV 20–22, CC1 28, CC2 29, I2Ct 8/9/10, I2Cc 16/17/18 | sink policy, CC/PD and integrated protected path |
| `BQ25798RQMR` | 29-pin RQM VQFN-HR, 4×4 mm; VBUS 2–3, SCL/SDA 14/15, INT 21, BAT 22–23, SYS 25 | buck-boost charger and NVDC system path configured for the accepted 2S battery |
| `CAT24C512WI-GT3` | SOIC-8; SDA 5, SCL 6, WP 7; 64 kB | dedicated patch/config EEPROM at 0x50 |
| `TVS2200DRVR` | 6-pin DRV WSON, 2×2 mm; GND 1–3/pad 7, protected IN 4–6 | shunt VBUS surge clamp at receptacle |

These are actual orderable package contacts, not family-level pins. Full maps
are in `hardware/architecture/devices.json` and generated into the living pin
atlas.

## Electrical/control topology

- USB-C VBUS connects to TPS VBUS_IN and separately to the TVS2200 shunt;
  the TVS is not drawn or routed in series.
- TPS PPHV feeds BQ VBUS. TPS I2Cc owns both BQ and the dedicated EEPROM;
  BQ open-drain INT returns to TPS I2Cc_IRQ.
- S3 SYS_I2C0 reaches TPS I2Ct on existing GPIO1/2. TPS active-low pulled-up
  IRQ shares S3 GPIO37 with TCA6424 `INT`; both sources are read after wake.
- TPS GPIO0 controls EEPROM WP with a reset-high pull. TPS GPIO1 controls
  active-low BQ CE with a reset-high charge-disable pull.
- TPS pins 26/27 are tied low because BC1.2/liquid sensing is not used. BQ
  DP/DM pins 6/7 remain disconnected and DPDM behavior is disabled. Product
  D-/D+ therefore remains an unbranched S3 USB2 pair, subject only to the exact
  connector/USB2 ESD network selected in I4.

No S3 GPIO is consumed beyond the already scheduled system I2C/IRQ contacts;
S3 GPIO47 remains the explicit direct-pin reserve.

## Configuration, recovery and openness

The checked TPS datasheet requires a >=36-kB external EEPROM and one EEPROM per
controller. The selected 64-kB device supports a fail-safe two-region policy:

1. factory/recovery fixture can program a blank EEPROM directly while TPS is
   held inactive;
2. source JSON/tool inputs, generated binary, version, hash and compatibility
   metadata are reproducible repository artifacts;
3. S3 verifies an owner-signed manifest before lowering WP and writing the
   inactive region;
4. power loss leaves the previous region intact; boot/readback and rollback are
   verified before the old region is retired;
5. recovery pads remain usable without a healthy application image.

TPS does not provide the project's owner signature policy. That verification
belongs to the open owner-controlled updater; EEPROM contents are not treated
as a secret or a vendor lock.

## Availability and visible price snapshot

Checked 2026-08-18 because exact MPNs are now selected. Counts/prices are
distributor snapshots, not a production allocation or RFQ.

| MPN | Lifecycle/orderability evidence | Visible stock | Unit price / 100 |
|---|---|---:|---:|
| `TPS25751DREFR` | TI active; Mouser orderable | 4,815 | $2.99 / $1.84 |
| `BQ25798RQMR` | TI active; DigiKey orderable | 11,866 | $5.51 / $3.514 |
| `CAT24C512WI-GT3` | onsemi active; DigiKey orderable | 101,930 | $0.82 / $0.7133 |
| `TVS2200DRVR` | TI active/production; DigiKey orderable | 29,220 | $1.10 / $0.4493 |

Visible 100-piece subtotal is about `$6.52`. Exact alternate/equivalence,
factory quote, taxes, yield and lead-time proof remain `I8`.

Primary/reference sources:

- [TI TPS25751 product](https://www.ti.com/product/TPS25751) and
  [datasheet](https://www.ti.com/lit/ds/symlink/tps25751.pdf)
- [TI BQ25798RQMR](https://www.ti.com/product/BQ25798/part-details/BQ25798RQMR)
  and [datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf)
- [TI integrated PD/charger reference](https://www.ti.com/tool/USB-PD-CHG-EVM-01)
  and [design guide](https://www.ti.com/lit/ug/tiduey1c/tiduey1c.pdf)
- [onsemi CAT24C512](https://www.onsemi.com/pdf/datasheet/cat24c512-d.pdf)
- [TI TVS2200](https://www.ti.com/product/TVS2200/part-details/TVS2200DRVR)

## Open proof matrix

| Proof | Required result |
|---|---|
| cable/source matrix | 5-V fallback and 9/15-V contracts never exceed declared current; 20 V never accepted |
| image faults | blank, corrupt and interrupted update cannot enable charge/high V; direct fixture recovery succeeds |
| USB2 | high-speed eye/ESD and recovery remain valid with the final receptacle; no PD/charger branch exists |
| IRQ | shared wired-low sources are identified without missed 256-us charger fault indications |
| power | no-battery USB service, admitted-pack supplement, deep-cell refusal, removal/bounce and reverse-current paths pass |
| thermal/fault | connector, TPS, BQ, inductor and cells derate safely under 30-W input and all product loads |

These are explicit prototype/electrical gates. They do not reopen the accepted
sink-only product role unless a pass condition cannot be achieved.
