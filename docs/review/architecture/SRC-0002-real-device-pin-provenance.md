# SRC-0002 — real-device pin provenance ledger

- Статус: **В работе; machine-readable compute/control pass проведён ревью**
- Дата: 2026-08-17
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
| codec | ES8311 family | audio contract reviewed; exact MPN/package and accessible reset/control implementation remain open | `open/blocking` |
| IR RX/TX | `TSOP38238`, `TSMP95000`, `TSAL6200` first discrete candidates | manufacturer part-level functions/packages are known; exact optical/electrical stuffing and driver remain conditional | `candidate facts`; finish package/driver/availability and HIL before count becomes target |
| display/touch | Waveshare SKU 29318, Elecrow `DLS31040B1` and Riverdi `RVT35HITNWC00-B` references | exact module/FPC contacts, dimensions, controllers and power boundaries are recorded in `devices.json`; `DEC-0043` replaces the invalid historical 4.5 MB/s gate with task/dirty-region acceptance | `verified references`; performance contract reviewed, exact MPN/interface/optics and HIL remain `open/blocking`, see `DSP-0001/FND-0051/DEC-0043` |
| microSD | Hirose `DM3AT-SF-PEJM5` exact socket reference | all 8 card contacts, detect switch and body are verified; integrated display TF slots are shared-SPI and not SDMMC-equivalent | `verified candidate boundary`; width, protection, placement, card set and HIL remain `open/blocking` |
| slow control | `TCA6424ARGJR` UQFN32 leading reference; `TCA9535PWR` TSSOP24 smaller alternative | official TI package tables expose respectively 24 and 16 ports, open-drain INT and I²C; all ports power up as inputs | `G2F-3I` accounts 23 used + 1 reserve under `DEC-0044`; exact electrical/MPN freeze remains open, see `NIF-0001/FND-0052` |
| external I²C fault boundary | `TCA4307DGKR` VSSOP8 reference | exact EN/SCLIN/SCLOUT/READY/SDAIN/SDAOUT contacts, powered-off high-Z and stuck-bus recovery verified from TI datasheet | `reference only`; can isolate U214/Port-A I²C, but does not qualify U214 SPI/UART/power hot-plug |
| radio output compression | `SN74HC595PWR` TSSOP16 candidate for `G2F-2R` | official TI package table exposes QA…QH, SER/SRCLK/RCLK, OE and SRCLR | `verified candidate`; OE/reset/pull truth table and shared-data timing remain schematic/HIL gates |
| non-programmable safety/power | exact latch/supervisor/converter set not selected | semantic endpoints are known; TCA9535/SN74HC595 do not implement the accepted latched hard STOP by themselves | `open/blocking` |
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
- [TI TCA9535 exact package datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf)
- [TI TCA6424A exact package datasheet](https://www.ti.com/lit/ds/symlink/tca6424a.pdf)
- [TI TCA4307 hot-swap/stuck-bus buffer datasheet](https://www.ti.com/lit/ds/symlink/tca4307.pdf)
- [TI SN74HC595 exact package datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf)
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
