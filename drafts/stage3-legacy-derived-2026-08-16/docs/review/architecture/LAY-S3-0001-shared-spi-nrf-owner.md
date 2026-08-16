> Архивировано решением DEC-0027: этот документ оптимизировал legacy-derived раскладку и не является входом новой архитектуры. Сохранён только как источник идей и отрицательных результатов.

# LAY-S3-0001 — S3 owns 3×nRF24 on shared SPI2

- Статус: **На ревью — static allocation complete; measurement/BOM gates open**
- Demand revision: `DM-0001` + `BUD-0001` после `REV-0003F`
- Exact MCU modules: S3 `ESP32-S3-WROOM-1U-N8R2/C3013944`; C5 `ESP32-C5-WROOM-1U-N8R8/C51950748`
- nRF owner: ESP32-S3
- S3↔C5 transport: dedicated S3 SPI3 ↔ C5 GP-SPI slave, 4-wire + DRDY
- Intent: minimum-change/cost candidate

## Owner and transport map

| Domain | Owner/controller | Physical path |
|---|---|---|
| UI/policy/storage, S3 Wi-Fi/BLE | S3 | application domain |
| display, microSD, CC1101, U214, 3×nRF24 | S3 SPI2 host | shared `MOSI/SCK/MISO`, bounded transactions, decoded CS |
| 3×nRF CE | S3 | SPI-fed output latch with independent Q0..Q2; latch/clear defaults all CE low and is dominated by `TX_KILL` |
| 3×nRF IRQ | S3 | qualified reset-safe IRQ aggregator; source identified by reading each STATUS |
| C5 Wi-Fi/802.15.4 and dual-path IR | C5 | local integrated radios + two RMT RX and one RMT TX |
| S3↔C5 | S3 SPI3 host / C5 SPI2 slave | dedicated bus; no C5-local nRF master, so `FND-0001` conflict is absent |
| ES8311 | S3 I²S0 + I²C | four direct signals, no MCLK |
| voice/GNSS | S3 UART1/UART2 | SA51x and one active external GNSS backend |
| recovery | native USB on each MCU | S3 GPIO19/20; C5 GPIO13/14; physical BOOT/RESET pads |

## ESP32-S3 direct-pin allocation

| GPIO | Target net | Reset/constraint note |
|---:|---|---|
| 0 | `S3_BOOT` | strap, physical recovery only |
| 1 | `WS2812` | output off/quiet until init |
| 2 | `I2S_DOUT` | freed by IR→C5 |
| 3 | reserved strap | no external driver |
| 4/5 | `I2C_SDA/SCL` | shared internal/qualified-accessory bus |
| 6 | `NRF_CE_LATCH` | pull-low; hardware clear by `TX_KILL` |
| 7 | `CC1101_GDO0` | direct FIFO/event input |
| 8/9/10 | `SPI2_CS_A/B/C` | 74HC138-class decoded CS; reset pulls choose no-device/disabled |
| 11/12/13 | `SPI2_MOSI/SCK/MISO` | display/SD/CC1101/U214/nRF shared bus |
| 14 | `LCD_DC` | direct display control |
| 15 | `EXT_RF_BUSY` | U214 profile; bounded when detached |
| 16/17 | `VOICE_UART_TX/RX` | SA518 or explicit SA868S stuffing |
| 18/47 | `GNSS_UART_RX/TX` | Unit GPS or U214 GNSS, one backend active |
| 19/20 | `USB_D-/D+` | fixed native USB/recovery |
| 21 | `EXT_RF_DIO1` | replaces strap-unsafe legacy GPIO3 use; LCD TE omitted |
| 35/36/37 | `C5LINK_SCK/MOSI/MISO` | requires N8R2; unavailable on N8R8 |
| 38/39 | `C5LINK_CS/DRDY` | dedicated link control/event |
| 40/41 | `ENC_A/B` | local control remains direct |
| 42 | `I2S_DIN` | freed by IR→C5 |
| 43/44 | `I2S_BCLK/WS` | ROM UART0 pins reused only after boot; codec held safe during reset |
| 45 | `CC1101_GDO2` | strap-isolated/high-Z until reset sampling completes |
| 46 | `NRF_IRQ_SUM` | input-only strap; aggregator output/reset pulls must preserve boot level |
| 48 | `CTRL_IRQ_SUM` | open-drain expander/touch interrupt aggregation |

No exposed S3 GPIO is double-booked. GPIO3 is the only unused exposed direct line and remains a strap reserve rather than claimed expansion margin.

## ESP32-C5 direct-pin allocation

| GPIO | Target net | Note |
|---:|---|---|
| 0/1 | `IR_RX_ROBUST/IR_RX_CARRIER` | both RMT RX channels |
| 2 | `IR_TX` | RMT TX; external driver default-off and `TX_KILL`-dominated |
| 6/23/24 | `C5LINK_MISO/SCK/MOSI` | sole GP-SPI used only as S3-link slave |
| 8/9 | `C5LINK_CS/DRDY` | link framing/event |
| 13/14 | `USB_D-/D+` | fixed independent recovery |
| 26/28 | `C5_BOOT` straps | physical BOOT path, safe pulls; no expander-only recovery |
| 27 | strap pull | no runtime consumer |
| 3/4/5/7/10/11/12/25 | reserve | GPIO3/25 retain strap/reset-load restrictions |

## Controller and shared-control allocation

| Resource | Allocation |
|---|---|
| S3 SPI2 | 3.2 MB/s display floor + bounded SD/CC/U214/nRF arbitration; non-preemptible chunk ≤4 KiB/1 ms |
| S3 SPI3 | C5 link only; measured ≥1.5 MB/s C5→S3 and ≥0.5 MB/s reverse simultaneously |
| S3 I²S0 | ES8311 48 kHz mono full-duplex DMA |
| S3 UART1/UART2 | voice and active GNSS profile; UART0 app pins consumed by I²S |
| S3 I²C0 | U12/U13, codec/Si4732/power/touch and qualified external I²C profiles with bus recovery |
| C5 SPI2 | S3-link slave only |
| C5 RMT | RX0 robust IR, RX1 carrier-learning IR, TX0 IR carrier |

Common UI candidate `IMP-0010/A` uses `U13.P10..P15` for a diode-isolated 3×3 ordinary-key matrix, `P16/P17` for the two analog-audio selectors, freed `U12.P12` for codec enable, freed target `U13.P06` for safe-default voice H/L, and an open-drain touch/expander IRQ aggregator. `C5_BOOT` becomes physical/recovery-only. Retaining U14 is pin-compatible and changes only BOM/test complexity, so UI choice does not bias nRF ownership.

## Memory, power, safety and recovery

- N8R2 passes only if the real S3 build proves ≥1,920 KiB usable PSRAM under `SCN-02`; failure rejects this layout rather than deleting features.
- 3.3 V architecture load stays within the 3 A rail class in `BUD-0001`; exact three PA/LNA modules still require stage-4 min/max qualification.
- `TX_KILL` clears the CE latch, inhibits nRF/CC/U214/IR/voice TX domains and resets both MCUs independently of SPI/I²C.
- C5 USB plus physical BOOT/RESET replaces the legacy S3↔C5 UART flash bridge; GPIO43/44 are not freed until that recovery fixture works with broken S3 firmware.
- Link loss cancels remote TX lease within 100 ms; hardware STOP is independent and faster.

## Static hard-gate review

| Gate | Static result | Remaining proof |
|---|---|---|
| HF-01..05 | no scope/owner/controller contradiction found | scenario firmware/HIL |
| HF-06/07 | target topology allocated | exact gates/detectors and fault injection |
| HF-08 | exact allocation has no duplicate/unavailable GPIO | GPIO45/46 reset-window fixture |
| HF-09 | conditional pass only | measured N8R2 usable-memory floor |
| HF-10 | conditional pass only | shared SPI2 and SPI3 latency/loss/goodput |
| HF-11 | recovery path allocated | bad-image USB/BOOT fixture for both MCUs |
| HF-12/13 | profiles and rail classes fit | exact connector/BOM/RF/power/thermal evidence |
| HF-14 | no unsupported API needed by topology | versioned implementation evidence |

## Candidate conclusion

This layout is statically feasible and has the fewest new active devices and the least rerouting. Its decisive risks are S3 N8R2 memory margin and shared-SPI nRF service latency under display/SD/U214 load. It receives no weighted score until those measurements and cost quotes exist.


