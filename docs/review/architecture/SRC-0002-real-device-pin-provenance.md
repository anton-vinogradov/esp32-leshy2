# SRC-0002 — real-device pin provenance ledger

- Статус: **В работе; machine-readable compute/control pass проведён ревью**
- Дата: 2026-08-18
- Gate: `FLOW-0001/G2F`, шаг 2
- Решение: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Finding: [`FND-0049`](../findings/FND-0049-exact-pin-map-lacked-device-provenance.md)

## Как читать статус

- `verified candidate` — точный MPN/variant и его реально доступные контакты
  проверены по первичным manufacturer documents; это ещё не target choice;
- `reference only` — реальное устройство проверено для сравнения, но не выбрано;
- `open/blocking` — family/function известны, но считать его pins, размеры,
  питание или footprint в complete map нельзя;
- `prototype gate` — бумажные слои закрыты, specimen verification возможна
  только после закупки/сборки.

## Compute and attached-device ledger

| Function | Exact candidate / real boundary | Provenance result | Статус и следующий gate |
|---|---|---|---|
| application/native 2.4/BLE | `ESP32-S3-WROOM-1U-N16R2` soldered module | official module v1.8 lists exact N16R2, 41 module pads and exposed GPIO0…21/35…48; module, not SoC maximum, is counted | `verified candidate`; exact order/marking + prototype boot report later |
| dual-band/802.15.4 | `ESP32-C5-WROOM-1U-N8R8` soldered module | official module v1.2 lists exact N8R8 and WROOM-1U pads; PSRAM consumes `GPIO15/SPICS1`, leaving GPIO0…14/23…28 before reservations | `verified candidate`; silicon revision/marking and errata floor remain lot gates |
| deterministic radio controller | `RP2354B A4`, QFN80 leading; `RP2354A A4` rejected-layout reference | official datasheet binds B-package to 48 GPIO/10×10 mm and A-package to 30 GPIO/7×7 mm; RP2354 adds stacked 2 MB flash and no carrier hides pins | B `verified candidate` for `G2F-3I`; exact A4 lot identity/land pattern/prototype SWD+USB proof later |
| external LoRa/GNSS | M5Stack Cap LoRa-1262 `U214` | actual Cap-Bus exposes GPS TX/RX, SCL/SDA, LoRa RST/IRQ/BUSY/SCK/MOSI/MISO/NSS and power; body `84×24×15.2 mm` | `verified candidate`; mating connector/retention/hot-plug HIL later |
| generic Unit surface | actual HY2.0-4P base connector | M5 documents GND, 5V and two signals; colors are conventions, not automatic peripheral support | `verified connector class`; every advertised Unit SKU is separately blocking until checked |
| compact nRF reference | Ebyte `E01-ML01S`, 12×19 mm SMD, onboard antenna, 0 dBm | manufacturer product/manual expose `VCC/CE/CSN/SCK/MOSI/MISO/IRQ/GND` and identify nRF24L01P | `reference only`; lifecycle/source authenticity/RF HIL and whether 0 dBm meets product envelope open |
| compact external-antenna nRF reference | Ebyte `E01-ML01IPX`, 12×19 mm SMD, manufacturer-labelled `IPX`, 0 dBm | 2025 specification exposes eight pads, 2.0–3.6 V, 13 mA TX, 12 mA RX, `12×19×2.0 mm` and ~50 Ω antenna interface, but no mating family/generation/MPN/dimensions | `verified reference`; `FND-0057` forbids assuming U.FL/MHF I until specimen gate; production source/lot and HIL open |
| high-power nRF reference | Ebyte `E01-2G4M27D`, 18×33.4 mm through-hole, 27 dBm | manufacturer product/manual expose `GND/VCC/CE/CSN/SCK/MOSI/MISO/IRQ`; size/power/antenna burden differs materially | `reference only`; not a default stuffing choice |
| three production nRF paths | three identical compact 0 dBm IPEX→SMA paths; `E01-ML01IPX` reference | Nordic nRF24 interface is known, but Nordic marks nRF24 series not recommended for new designs; generic marketplace boards are not provenance | direction accepted `DEC-0048`; exact production MPN/revision, authorised sourcing, lot identity and qualified alternate remain `open/blocking` |
| CC1101 path | `CC1101RGPR` VQFN20 bare-IC candidate | official TI pin table proves exact silicon contacts `SCLK/SI/SO/GDO0/GDO2/CSn/RF_P/RF_N`; current TI order page says `ACTIVE`; it still does not prove crystal, matching network or antenna connector | `verified active silicon candidate`; RF implementation remains `open/blocking`, see lifecycle correction `FND-0050` |
| analog voice | NiceRF `SA518` rev 1.1 preferred / SA868S fallback | current manufacturer sheet exposes 20 physical contacts, one 50-ohm `ANT` on pin 7, UART/PTT/PD/H-L/audio functions and 136–174/400–470 MHz; it exposes no dedicated `SQ`, while pin 17 `UPDATE` has a direction/description conflict | `verified candidate boundary`; `FND-0056` neutralizes the false SQ mapping, while production source/lot, activity semantics, update fixture, footprint and RF HIL remain `open/blocking` |
| broadcast receiver | Skyworks `Si4732-A10-GS`, SOIC16 | manufacturer ordering guide and physical pin table expose `FMI=1`, `RFGND=2`, `AMI=3`; block diagram assigns FM/SW to FMI and AM/LW to AMI | `verified candidate boundary`; two input domains proven and two ports accepted `DEC-0049`; exact lifecycle/AVL/frontends remain open |
| codec/audio path | Everest Semiconductor `ES8311`, QFN-20 3×3 mm with exposed pad; TI `TAC5111IRGER` comparison reference; exact selector/buffer/logic/amp candidates in `devices.json` | ES8311 all 20 contacts+EPAD and exact S3 I2C/I2S fit are verified; complete-path review additionally verifies all exposed contacts of `TAC5111IRGER`, `TMUX1136DGSR`, `TS5A63157DCKR`, `TLV9061IDBVR`, `SN74LVC2G08DCUR`, existing `SN74LVC1G3157DBVR` and `PAM8302AASCR` | `DEC-0054` accepts the ES8311 active-buffer prototype topology, exact selector/gate/amp ICs and direct reset arm; passive values, power, common mode, RF and HIL remain blocking |
| IR RX/TX | `TSOP38238`, `TSMP95000`, `TSAL6200` first discrete candidates | manufacturer part-level functions/packages are known; exact optical/electrical stuffing and driver remain conditional | `candidate facts`; finish package/driver/availability and HIL before count becomes target |
| display/touch | Waveshare SKU 29318, Elecrow `DLS31040B1` and Riverdi `RVT35HITNWC00-B` references | exact module/FPC contacts, dimensions, controllers and power boundaries are recorded in `devices.json`; `DEC-0043` replaces the invalid historical 4.5 MB/s gate with task/dirty-region acceptance | `verified references`; performance contract reviewed, exact MPN/interface/optics and HIL remain `open/blocking`, see `DSP-0001/FND-0051/DEC-0043` |
| microSD | Hirose `DM3AT-SF-PEJM5` exact socket reference | all 8 card contacts, detect switch and body are verified; integrated display TF slots are shared-SPI and not SDMMC-equivalent | `verified candidate boundary`; width, protection, placement, card set and HIL remain `open/blocking` |
| slow control | `TCA6424ARGJR` UQFN32 leading reference; `TCA9535PWR` TSSOP24 smaller alternative | official TI package tables expose respectively 24 and 16 ports, open-drain INT and I²C; all ports power up as inputs | `G2F-3I` now accounts `24 used / 0 reserved / 0 free` after `FND-0067` assigns P27 to the omitted RX-audio source selector; exact electrical/MPN freeze remains open, see `NIF-0001/FND-0052/FND-0067` |
| external I²C fault boundary | `TCA4307DGKR` VSSOP8 reference | exact EN/SCLIN/SCLOUT/READY/SDAIN/SDAOUT contacts, powered-off high-Z and stuck-bus recovery verified from TI datasheet | `reference only`; can isolate U214/Port-A I²C, but does not qualify U214 SPI/UART/power hot-plug |
| radio output compression | `SN74HC595PWR` TSSOP16 candidate for `G2F-2R` | official TI package table exposes QA…QH, SER/SRCLK/RCLK, OE and SRCLR | `verified candidate`; OE/reset/pull truth table and shared-data timing remain schematic/HIL gates |
| non-programmable safety | `TPS3808G33DBVR`, `SN74LVC1G74DCUR`, `74LVC2G14GW,125`, 2×`74LVC1G32GV,125`, `SN74LVC3G34DCUR`, 2×`SN74LVC08APWR`; exact evidence devices in `SAFE-0002/devices.json` | official pinouts, partial-power-down behavior, three reset outputs, nine gate functions and eight evidence channels are machine-instantiated | `I2 reviewed DEC-0061/REV-0005O`; exact rail source/load switches are I3 |
| supervised 2S manager circuit | `MAX17320G20+T`, `MSPM0C1104SDGS20R`, `CSD87313DMST`, 2×`0451005.MRL`, `WSL25125L000FEA`, 2×`B57332V5103F360`, `2N7002DW-7-F`, `BAV70LT1G`, `BAT54-7-F`; diagnostic `TPUL2G223BQBR`, `DMN2056U-7`, 2×`CRM2512-FX-20R0ELF` and exact dual-channel timing/divider/filter passives | manufacturer package tables prove every exposed contact; TPUL WQFN contact 5 is `2Q` and contact 16 is `VCC`; channel 1 is non-retriggerable and channel 2 independently holds its clear during the refractory interval; exact MSPM0 DGS20 exposes PA25/A2 pin 20 and PA26/A1 pin 1, while PA24 permits no injection current | `DEC-0067/REV-0005X` manager circuit and `DEC-0078/REV-0005AI` corrected diagnostic hardware reviewed; PA24 mismatch closed by `FND-0078`, TPUL pin/repetition gap by `FND-0082`; exact-cell droop, mechanical/hot/source-handover HIL remain I3 |
| replaceable 2S cells | 2×`XTAR 18650 4000mAh` protected button-top assemblies | official exact datasheet gives both physical terminals, max 18.7×69.7-mm envelope, 4000/3800-mAh capacity, 10-A discharge, 2-A standard charge, <=40-mOhm initial resistance and 11…14-A protection trip; raw and USB-equipped variants are different devices | `DEC-0079/REV-0005AJ` exact first target reviewed; assembly-matching UN38.3/certification evidence, authenticity, received fit, droop/thermal/protection HIL remain blocking |
| downstream rail tree | `TPS629203DRLR`, `TPS3808G33DBVR`, 3×`TPS564252DRLR`, `TPS25961DRVR`, 2×`TPS25974LRPWR`, `WPN201612H2R2MT`, 2×`MWSA0503S-3R3MT`, `MWSA0503S-4R7MT`, 5×`TPS22919DCKR`, 2×`MMBT3904-7-F`, `TPS259470LRPWR`, 24 exact converter energy/configuration/feedback passives, 10 exact control/POR resistors and exact post-buck ILIM/ILM/OVLO/dVdt/ITIMER/PGTH/output parts | official package tables prove every real IC pin; independent fixed feedback removes the SA518 selector fault; `PWR-0011/0012/0019/0020` verify exact passive MPNs, physical instances, source sequence, raw/protected split and protected-side PG | `DEC-0068…0081` review active topology, external latch-off, optional-PG qualification, source sequencing and independent AON/main/voice high-side-short containment; hot/transient/destructive-fault HIL remains I3 |
| high-throughput external tier | no exact accessory/transport/connector | current requirement intentionally rejects generic host and cannot name pins without an RF profile | `open/blocking` for final architecture, isolated reopen gate for base candidate comparison |

## Primary sources used in this pass

- [ESP32-S3-WROOM-1/WROOM-1U datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [ESP32-C5-WROOM-1/WROOM-1U datasheet v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf)
- [ESP32-C5 SoC datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.pdf)
- [Raspberry Pi RP2350/RP2354 product facts](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html)
- [M5Stack U214 actual Cap pin map and dimensions](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [M5Stack Grove/HY2.0 connector definitions](https://docs.m5stack.com/en/learn/interface/grove)
- [Nordic nRF24 lifecycle page](https://www.nordicsemi.com/Products/nRF24-series)
- [Ebyte E01-ML01S actual module page](https://www.ebyte.com/product/45.html)
- [Ebyte E01-ML01IPX actual module page/specification](https://www.ebyte.com/product/47.html)
- [Ebyte E01-2G4M27D actual module page](https://www.ebyte.com/product/449.html)
- [Raspberry Pi RP2350/RP2354 package pinout](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)
- [TI CC1101 exact silicon datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [Skyworks Si4732-A10 exact SOIC16 boundary](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [NiceRF SA518 rev 1.1 exact module boundary](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
- [Everest Semiconductor ES8311 product brief rev 17.0](https://www.everest-semi.com/pdf/ES8311%20PB.pdf)
- [ES8311 user guide exact QFN-20 contact map](https://files.waveshare.com/wiki/common/ES8311.user.Guide.pdf)
- [TI TAC5111 exact VQFN-24 contact map](https://www.ti.com/lit/ds/symlink/tac5111.pdf)
- [TI TMUX1136 exact VSSOP-10 contact map](https://www.ti.com/lit/ds/symlink/tmux1136.pdf)
- [TI TS5A63157 exact SC70-6 contact map](https://www.ti.com/lit/ds/symlink/ts5a63157.pdf)
- [TI TLV9061 exact SOT-23-5 contact map](https://www.ti.com/lit/ds/symlink/tlv9061.pdf)
- [TI SN74LVC2G08 exact VSSOP-8 contact map](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf)
- [TI SN74LVC1G3157 exact SOT-23-6 contact map](https://www.ti.com/lit/ds/symlink/sn74lvc1g3157.pdf)
- [Diodes PAM8302A exact MSOP-8 contact map](https://www.diodes.com/datasheet/download/PAM8302A.pdf)
- [TI TCA9535 exact package datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf)
- [TI TCA6424A exact package datasheet](https://www.ti.com/lit/ds/symlink/tca6424a.pdf)
- [TI TCA4307 hot-swap/stuck-bus buffer datasheet](https://www.ti.com/lit/ds/symlink/tca4307.pdf)
- [TI SN74HC595 exact package datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf)
- [TI MSPM0C1104 exact DGS20 and injection-current limits](https://www.ti.com/lit/ds/symlink/mspm0c1104.pdf)
- [TI TPUL2G223 non-retriggerable one-shot](https://www.ti.com/lit/ds/symlink/tpul2g223.pdf)
- [Diodes DMN2056U exact SOT-23 switch](https://www.diodes.com/datasheet/download/DMN2056U.pdf)
- [Vishay D/CRCW-IF pulse-proof resistor family](https://www.vishay.com/docs/20024/dcrcwife3.pdf)
- [Murata GRM31C5C1H224JE02L exact 220-nF C0G timing capacitor](https://www.murata.com/en-us/products/productdetail?partno=GRM31C5C1H224JE02%23)
- [XTAR exact protected 18650 4000mAh product and datasheet](https://www.xtar.cc/product/xtar-18650-4000mah-10a-battery.html)
- [Display/touch/storage exact-device evidence](DSP-0001-display-storage-real-device-evidence.md)

## Machine-readable source and draft consumers

[`DEC-0042`](../decisions/DEC-0042-single-source-architecture-data.md) makes
`hardware/architecture/devices.json` the versioned representation of verified
rows above. Consumers are `G2F-2R`, `G2F-3D` and the leading paper map
`G2F-3I`; their generated pin ledger is
[`G2F-pin-ledger`](generated/G2F-pin-ledger.md). Passing its validator proves
contact existence/accounting and, where declared, complete slow-contact and
resource-contract accounting; it does not close rows that remain `reference
only` or `open/blocking`. [`NIF-0001`](NIF-0001-digital-noninterference-layout.md)
reviews the `G2F-3I` digital boundary and keeps physical RF/electrical/HIL open.

## Mandatory per-candidate evidence columns

Каждая следующая строка complete pin map должна ссылаться на этот ledger и
содержать: exact MPN/revision, package/module pad number, exposed signal name,
internal reservation, boot/reset level, voltage/domain, owner peripheral
instance, physical connector/net, source document/version and prototype test ID.
Отсутствующая колонка делает строку provisional, даже если GPIO number выглядит
свободным.
