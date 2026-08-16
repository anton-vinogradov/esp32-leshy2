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
| optional deterministic controller | `RP2354A A4`, QFN60, exact order code required | official product table binds RP2354A to QFN60, 30 GPIO and stacked 2 MB flash; no carrier hides pins because candidate is bare IC on our PCB | `verified candidate`; exact A4 order identity/land pattern/prototype SWD+USB proof later |
| external LoRa/GNSS | M5Stack Cap LoRa-1262 `U214` | actual Cap-Bus exposes GPS TX/RX, SCL/SDA, LoRa RST/IRQ/BUSY/SCK/MOSI/MISO/NSS and power; body `84×24×15.2 mm` | `verified candidate`; mating connector/retention/hot-plug HIL later |
| generic Unit surface | actual HY2.0-4P base connector | M5 documents GND, 5V and two signals; colors are conventions, not automatic peripheral support | `verified connector class`; every advertised Unit SKU is separately blocking until checked |
| compact nRF reference | Ebyte `E01-ML01S`, 12×19 mm SMD, onboard antenna, 0 dBm | manufacturer product/manual expose `VCC/CE/CSN/SCK/MOSI/MISO/IRQ/GND` and identify nRF24L01P | `reference only`; lifecycle/source authenticity/RF HIL and whether 0 dBm meets product envelope open |
| high-power nRF reference | Ebyte `E01-2G4M27D`, 18×33.4 mm through-hole, 27 dBm | manufacturer product/manual expose `GND/VCC/CE/CSN/SCK/MOSI/MISO/IRQ`; size/power/antenna burden differs materially | `reference only`; not a default stuffing choice |
| three production nRF paths | exact module MPN/revision not selected | Nordic nRF24 interface is known, but Nordic marks nRF24 series not recommended for new designs; generic marketplace boards are not provenance | `open/blocking`; compare exact compact/PA options, authorised sourcing and qualified alternates |
| CC1101 path | `CC1101RGPR` VQFN20 bare-IC candidate | official TI pin table proves exact silicon contacts `SCLK/SI/SO/GDO0/GDO2/CSn/RF_P/RF_N`; current TI order page says `ACTIVE`; it still does not prove crystal, matching network or antenna connector | `verified active silicon candidate`; RF implementation remains `open/blocking`, see lifecycle correction `FND-0050` |
| analog voice | SA518 preferred / SA868S fallback family | command/function review exists, but exact orderable module revision/padout/body is not frozen | `open/blocking` |
| broadcast receiver | Si4732 family | function/patch contract reviewed; exact orderable suffix/package, required pins and RF network remain open | `open/blocking` |
| codec | ES8311 family | audio contract reviewed; exact MPN/package and accessible reset/control implementation remain open | `open/blocking` |
| IR RX/TX | `TSOP38238`, `TSMP95000`, `TSAL6200` first discrete candidates | manufacturer part-level functions/packages are known; exact optical/electrical stuffing and driver remain conditional | `candidate facts`; finish package/driver/availability and HIL before count becomes target |
| display/touch | Waveshare SKU 29318, Elecrow `DLS31040B1` and Riverdi `RVT35HITNWC00-B` references | exact module/FPC contacts, dimensions, controllers and power boundaries are recorded in `devices.json`; ST7796S references fail the historical 4.5 MB/s gate by datasheet | `verified references`; target performance/interface/optics remain `open/blocking`, see `DSP-0001/FND-0051/IMP-0036` |
| microSD | Hirose `DM3AT-SF-PEJM5` exact socket reference | all 8 card contacts, detect switch and body are verified; integrated display TF slots are shared-SPI and not SDMMC-equivalent | `verified candidate boundary`; width, protection, placement, card set and HIL remain `open/blocking` |
| slow control | `TCA9535PWR` TSSOP24 candidate | official TI package table exposes 16 ports, INT, address straps and I²C; power-on ports are inputs | `verified candidate`; every control needs external safe pull and STOP cannot depend on it |
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
- [Ebyte E01-2G4M27D actual module page](https://www.ebyte.com/product/449.html)
- [Raspberry Pi RP2350/RP2354 package pinout](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)
- [TI CC1101 exact silicon datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [TI TCA9535 exact package datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf)
- [TI SN74HC595 exact package datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf)
- [Display/touch/storage exact-device evidence](DSP-0001-display-storage-real-device-evidence.md)

## Machine-readable source and draft consumers

[`DEC-0042`](../decisions/DEC-0042-single-source-architecture-data.md) makes
`hardware/architecture/devices.json` the versioned representation of verified
rows above. The two first consumers are `G2F-2R` and `G2F-3D`; their generated
pin ledger is [`G2F-pin-ledger`](generated/G2F-pin-ledger.md). Passing its
validator proves contact existence/accounting only; it does not close rows that
remain `reference only` or `open/blocking` here.

## Mandatory per-candidate evidence columns

Каждая следующая строка complete pin map должна ссылаться на этот ledger и
содержать: exact MPN/revision, package/module pad number, exposed signal name,
internal reservation, boot/reset level, voltage/domain, owner peripheral
instance, physical connector/net, source document/version and prototype test ID.
Отсутствующая колонка делает строку provisional, даже если GPIO number выглядит
свободным.
