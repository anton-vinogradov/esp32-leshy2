# PIN-0001 — проверенный инвентарь pin/controller ceilings S3 и C5

- Статус: **Проведено ревью; allocation выполнен в трёх static layouts, owner decision открыт**
- Этап: 3 — системная архитектура и владение
- Дата: 2026-08-16
- Source baseline: ESP32-S3-WROOM-1/1U datasheet v1.8; ESP32-C5-WROOM-1/1U datasheet v1.2 от 2026-08-12; current legacy tsCircuit
- Связанные артефакты: `DM-0001`, `FND-0001`, `FND-0028`, `FND-0029`

## ESP32-S3 module ceiling

| Ресурс | Проверенный факт | Архитектурное следствие |
|---|---|---|
| Exposed GPIO | WROOM-1/1U exposes 36 GPIO: `0..21`, `35..48` except 22–34 | legacy uses every exposed pin; any new direct demand requires a real release/remap |
| Strapping | `GPIO0`, `GPIO3`, `GPIO45`, `GPIO46`; boot depends on `0/46` | external drivers, CE/IRQ and pull networks on these pins require reset-window proof |
| Native USB | `GPIO19/20` are D−/D+ | cannot be borrowed while product USB/recovery remains |
| Current module | legacy source selects `ESP32-S3-WROOM-1U-N8R2`: 8 MB flash, 2 MB Quad PSRAM | `GPIO35..37` remain available on this exact variant |
| 8 MB PSRAM variants | WROOM N*R8 uses Octal PSRAM; `GPIO35..37` unavailable | memory upgrade invalidates three lines of legacy `C5LINK`; no drop-in assumption |
| GP-SPI | SPI2 and SPI3 are general-purpose and DMA-capable | S3-heavy can separate high-bandwidth/display-storage and radio work in principle; exact routing and DMA contention still measured |
| UART | 3 controllers, shared FIFO/GDMA capabilities | SA51x, external GNSS and recovery/debug fit only after exact concurrent-role allocation |
| I²C | 2 controllers | internal control and external Unit profiles can be electrically/logically separated if pins permit |
| I²S | 2 full/half-duplex controllers with dedicated DMA | ES8311 four-signal S3 demand is controller-feasible; pins/buffers remain layout work |
| SD/MMC host | 1/4/8-bit, up to documented 80 MHz | candidate host for C5 SDIO or SD card; one controller cannot serve incompatible simultaneous topologies without proof |
| USB functions | USB OTG plus USB Serial/JTAG share integrated PHY by TDM unless external PHY used | product composite/recovery profile must be designed, not counted as two independent physical USB ports |

## Current S3 legacy allocation — evidence, not target

| GPIO class | Current nets | Accepted change pressure |
|---|---|---|
| `0..5` | boot, WS2812, legacy IR TX, LoRa DIO, I²C | IR move frees `2`; `3` remains conditional U214 demand |
| `6..15` | nRF CE, CC1101 event, CS decoder, shared SPI, LCD DC, LoRa BUSY | nRF ownership can free or retain `6`; U214 does not make `15` free while attached |
| `16..21` | voice UART, GNSS UART RX, USB, LCD TE | external GNSS still requires UART; USB fixed |
| `35..39` | legacy SPI C5 link + DRDY | unavailable in part on R8 PSRAM; transport is open |
| `40..48` | encoder, legacy IR RX, C5 flash UART, CC1101 event, nRF IRQ, GNSS TX, expander IRQ | IR move frees `42`; C5 native-recovery proof may free `43/44`; `45/46` are straps |

Every line in this table has either a current consumer or a conditional attachment/recovery role. “Onboard part removed” is not sufficient to call the signal free when the accepted external profile uses it.

## ESP32-C5 module ceiling

| Ресурс | Проверенный факт | Архитектурное следствие |
|---|---|---|
| Exposed GPIO | module exposes up to 22 GPIO; N8R8 has in-package PSRAM and therefore `GPIO15/SPICS1` is unavailable | selected N8R8 layout has at most 21 usable GPIO before straps/interfaces |
| Strapping | boot `GPIO26..28`; SDIO edge `GPIO25` and `MTDI/GPIO3`; JTAG source `GPIO7`; also MTMS/MTDI loads | these pins may be GPIO after reset, but attached logic must preserve sampled levels and recovery |
| GP-SPI | only SPI2 is general-purpose master/slave | cannot be inter-MCU SPI slave and nRF master at once; `FND-0001` remains hard |
| SDIO slave | one controller, fixed `CLK=9`, `CMD=10`, `DATA0=8`, `DATA1=7`, `DATA2=14`, `DATA3=13`; revision v1.0 required | 1-bit needs `7..10`; 4-bit adds `13/14`; pin mux and chip revision are hard gates |
| Native USB Serial/JTAG | fixed `GPIO13/14` | conflicts with 4-bit SDIO. Independent C5 USB recovery and 4-bit SDIO cannot both be assumed |
| UART | UART0 fixed IO-MUX `TX=11`, `RX=12`; plus UART1 and LP UART | legacy S3 flash bridge duplicates native USB/recovery and must justify its two pins |
| RMT | 2 TX + 2 RX channels sharing 192 words | accepted dual RX IR consumes both RX channels; TX still controller-feasible but memory/timing HIL required |
| GPIO matrix | GP-SPI/I²C/I²S/RMT and many controls routable | routability does not create more pins or controllers |
| Integrated radios | Wi-Fi 2.4/5, BLE, IEEE 802.15.4 share radio resources | C5 BLE remains default-off; Wi-Fi/802.15.4 concurrency is scheduled, not multiplied |

## Transport feasibility classes

| Class | C5 direct-pin cost | Recovery effect | nRF24 effect | Current disposition |
|---|---:|---|---|---|
| Legacy GP-SPI slave | clock/data/CS + DRDY | preserves C5 USB | consumes the only GP-SPI, hard-fails C5-owned nRF24 | allowed only in S3-owned nRF variant, still requires performance proof |
| SDIO 1-bit | `GPIO7..10` | can preserve `GPIO13/14` USB; exact simultaneous support/HIL required | frees GP-SPI for C5-owned nRF24 | primary C5-heavy transport candidate |
| SDIO 4-bit | `GPIO7..10,13,14` | collides with native USB pins | frees GP-SPI and offers wider bus | hard-fail unless an independently proven recovery architecture replaces C5 USB |
| UART link | 2–4 signals depending flow control | can preserve USB/GP-SPI | bandwidth/latency likely weakest for capture/update | fallback only after numeric traffic proof |

## Immediate hard constraints

1. S3 memory variant and S3↔C5 transport are one coupled decision.
2. C5 transport, C5 USB recovery and nRF ownership are one coupled decision.
3. `GPIO35..37` cannot appear in an S3 N*R8 layout.
4. `GPIO15` cannot appear in a C5 N8R8 layout.
5. No 4-bit C5 SDIO layout can claim native C5 USB simultaneously on `GPIO13/14`.
6. Strapping pins are not ordinary free GPIO until external reset-level analysis passes.
7. Both C5 RMT RX channels are reserved by accepted consumer IR; no additional C5 RMT-RX promise exists without reallocation.

## Primary sources

- [ESP32-S3-WROOM-1/1U datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [ESP32-C5-WROOM-1/1U datasheet v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf)
- [ESP32-C5 SDIO slave driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/peripherals/sdio_slave.html)
- [ESP32-C5 hardware checklist: fixed SDIO pins and revision](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html#sdio)
