> Архивировано решением DEC-0027: этот документ оптимизировал legacy-derived раскладку и не является входом новой архитектуры. Сохранён только как источник идей и отрицательных результатов.

# LAY-C5-0001 — C5 owns 3×nRF24 with 1-bit SDIO link

- Статус: **На ревью — static allocation complete; measurement/BOM gates open**
- Demand revision: `DM-0001` + `BUD-0001` after `REV-0003F`
- Exact MCU modules: S3 `ESP32-S3-WROOM-1U-N8R8`; C5 `ESP32-C5-WROOM-1U-N8R8/C51950748`, exact SDIO-capable silicon revision required
- nRF owner: ESP32-C5
- S3↔C5 transport: S3 SD/MMC host ↔ fixed C5 1-bit SDIO slave
- Intent: isolate nRF from display/storage bus and maximize S3 PSRAM

## Owner and transport map

| Domain | Owner/controller | Physical path |
|---|---|---|
| UI/storage, display, CC1101, U214, S3 Wi-Fi/BLE | S3 | SPI2/application domain |
| 3×nRF24 | C5 SPI2 host | dedicated local SPI; decoded CS, latched independent CE, aggregated IRQ |
| C5 Wi-Fi/802.15.4 and dual-path IR | C5 | integrated radios + RMT; scheduled with local nRF service |
| S3↔C5 | S3 SD/MMC host / C5 1-bit SDIO slave | fixed C5 GPIO7..10; preserves C5 USB13/14 |
| ES8311, voice and GNSS | S3 | same I²S/UART boundaries as `LAY-S3` |
| recovery | native USB on both MCUs | 4-bit SDIO prohibited because it would consume C5 USB13/14 |

## ESP32-S3 direct-pin allocation

| GPIO | Target net | Reset/constraint note |
|---:|---|---|
| 0 | `S3_BOOT` | physical recovery strap |
| 1 | `WS2812` | safe init |
| 2/42/43/44 | `I2S_DOUT/DIN/BCLK/WS` | UART0 bridge removed only after C5 USB recovery proof |
| 3 | reserved strap | no external driver |
| 4/5 | `I2C_SDA/SCL` | internal + qualified accessory profiles |
| 6 | `C5_SDIO_CLK` | S3 SD/MMC host output |
| 7 | `CC1101_GDO0` | direct event |
| 8/9/10 | `SPI2_CS_A/B/C` | main-bus decoder |
| 11/12/13 | `SPI2_MOSI/SCK/MISO` | display/SD/CC1101/U214; no nRF payload |
| 14 | `LCD_DC` | display control |
| 15 | `EXT_RF_BUSY` | U214 |
| 16/17 | `VOICE_UART_TX/RX` | exact stuffing manifest |
| 18/47 | `GNSS_UART_RX/TX` | one active backend |
| 19/20 | `USB_D-/D+` | fixed S3 recovery |
| 21 | `EXT_RF_DIO1` | LCD TE omitted |
| 35/36/37 | unavailable | consumed internally by N8R8 Octal PSRAM |
| 38/39 | `C5_SDIO_CMD/D0` | bidirectional host signals |
| 40/41 | `ENC_A/B` | direct controls |
| 45 | `CC1101_GDO2` | reset-window isolation required |
| 46 | `C5_SDIO_INT` | input-only strap; C5 DATA1 interrupt through reset-safe path |
| 48 | `CTRL_IRQ_SUM` | open-drain control/touch aggregation |

N8R8 provides comfortable PSRAM but leaves no generic direct-output GPIO reserve after the accepted attachments; GPIO3/46 are strap/input restricted.

## ESP32-C5 direct-pin allocation

| GPIO | Target net | Note |
|---:|---|---|
| 0/1/2 | `NRF_SCK/MOSI/MISO` | sole GP-SPI as nRF master |
| 3 | reserved MTDI strap | no external driver |
| 4/5 | `NRF_CS_A/B` | 2→4 decoder; reset pulls select unused output/all radios deselected |
| 6 | `NRF_CE_LATCH` | SPI-fed CE latch, hardware clear under `TX_KILL` |
| 7 | `SDIO_DATA1/INT` | fixed 1-bit SDIO interrupt |
| 8 | `SDIO_DATA0` | fixed bidirectional data |
| 9 | `SDIO_CLK` | fixed input from S3 |
| 10 | `SDIO_CMD` | fixed bidirectional command |
| 11 | `NRF_IRQ_SUM` | UART0 abandoned; native USB is recovery |
| 12 | `IR_RX_ROBUST` | RMT RX0 |
| 13/14 | `USB_D-/D+` | fixed native recovery; forbids 4-bit SDIO |
| 23 | `IR_RX_CARRIER` | RMT RX1 |
| 24 | `IR_TX` | RMT TX; driver default-off/STOP-dominant |
| 25 | reserved SDIO-edge strap | no runtime load until reset proof |
| 26/28 | `C5_BOOT` straps | physical recovery path |
| 27 | strap pull | no runtime consumer |

There is no unrestricted spare C5 GPIO. This is not a hard failure, but any new direct C5 demand reopens the layout.

## Controller and control allocation

| Resource | Allocation |
|---|---|
| S3 SPI2 | display/SD/CC1101/U214; lower contention than `LAY-S3` |
| S3 SD/MMC host | C5 1-bit SDIO only; microSD remains SPI |
| C5 SPI2 | 3×nRF master only; no double booking |
| C5 SDIO slave | revision-qualified fixed 1-bit mode on GPIO7..10 |
| C5 RMT | two RX + one TX for IR; all accepted RX channels consumed |
| C5 integrated RF | Wi-Fi/802.15.4 scheduled against nRF/IR ISR budget; no false simultaneity |

The same optional `IMP-0010/A` U13 matrix/audio map as `LAY-S3` fits because it does not consume C5 direct GPIO. C5 BOOT is physical-only; U13.P06 becomes the fail-safe voice H/L control candidate.

## Memory, traffic, power, safety and recovery

- S3 N8R8 removes the N8R2 memory-floor risk but permanently removes GPIO35..37.
- 1-bit SDIO must meet `BUD-0001`: ≥1.5 MB/s C5→S3 and ≥0.5 MB/s reverse simultaneously, 2 MB/s 500 ms burst, control p99≤10 ms/max≤20 ms.
- C5 must service nRF IRQ p99≤250 µs while its integrated radio scheduler and dual IR paths are active; raw frames cross IPC, unlike `LAY-S3`.
- `TX_KILL` clears C5 CE latch, powers/inhibits nRF and IR TX, and resets both MCUs independent of SDIO.
- C5 native USB13/14 plus physical BOOT/RESET is mandatory; 4-bit SDIO is excluded from this layout.
- Power remains inside the 3 A 3.3 V rail class, but C5 local RF/coexistence peaks require exact transient and antenna-isolation HIL.

## Static hard-gate review

| Gate | Static result | Remaining proof |
|---|---|---|
| HF-01..05 | accepted owners/functions allocated | C5 concurrency firmware/HIL |
| HF-06/07 | target safety paths allocated | exact detector/gate fault injection |
| HF-08 | no duplicate/unavailable pin; GPIO15 unused | C5 strap and SDIO revision fixtures |
| HF-09 | static memory margin strongest | measured internal DMA floors |
| HF-10 | conditional pass only | 1-bit SDIO throughput/latency and raw nRF IPC loss |
| HF-11 | both native USB paths preserved | bad-image/empty-flash procedure |
| HF-12/13 | attachment/power classes fit | exact nRF modules and RF/thermal coexistence |
| HF-14 | topology needs only public controllers | versioned driver evidence |

## Candidate conclusion

This layout is statically feasible and gives S3 the best memory and main-bus margin. It pays with zero unrestricted C5 GPIO margin, exact C5-revision dependence, complete nRF rerouting, a new SDIO transport, and raw-frame IPC. It receives no weighted score until those measurements and cost quotes exist.


