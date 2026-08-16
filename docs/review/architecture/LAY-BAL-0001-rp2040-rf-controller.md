# LAY-BAL-0001 — modular RP2040 controller owns 3×nRF24

- Статус: **На ревью — static allocation complete; measurement/BOM/trust gates open**
- Demand revision: `DM-0001` + `BUD-0001` after `REV-0003F`
- Exact processors: S3 `ESP32-S3-WROOM-1U-N8R2/C3013944`; C5 `ESP32-C5-WROOM-1U-N8R8/C51950748`; RF controller `RP2040 QFN-56 + W25Q64JV 8 MiB`
- nRF owner: one dedicated RP2040 firmware domain on an internal replaceable RF mezzanine
- S3↔C5/RF transport: shared S3 SPI3 host bus with independent CS/DRDY endpoints
- Intent: isolate nRF real-time work and RF serviceability, explicitly measuring the price of a third controller

## Owner and transport map

| Domain | Owner/controller | Physical path |
|---|---|---|
| UI/storage/S3 Wi-Fi/BLE/display/CC/U214 | S3 | same SPI2/application boundary as `LAY-C5` |
| C5 Wi-Fi/802.15.4 + IR | C5 | local integrated RF/RMT; GP-SPI slave only |
| 3×nRF24 | RP2040 SPI1 | three direct CS, three direct CE and three direct IRQ; one scheduler/timebase |
| S3↔C5 | S3 SPI3 host / C5 SPI2 slave | shared clock/data group, own CS and DRDY |
| S3↔RF controller | S3 SPI3 host / RP2040 SPI0 slave | own CS and IRQ; typed frames, bounded local buffering |
| RF module recovery | RP2040 SWD + BOOTSEL/RUN service pads | bad firmware does not depend on S3/C5 application code |

The RF controller is part of the base product in this layout, not an optional accessory. The internal mezzanine may be replaceable, but all three nRF paths remain installed and available simultaneously.

## ESP32-S3 direct-pin allocation

Common assignments match `LAY-S3`: GPIO0 boot, 1 WS2812, 2/42/43/44 I²S, 4/5 I²C, 7 and strap-isolated 45 CC1101 events, 8..10 main CS decode, 11..13 SPI2, 14 LCD DC, 15 U214 BUSY, 16/17 voice UART, 18/47 GNSS UART, 19/20 USB, 21 U214 DIO1, 40/41 encoder, 48 control IRQ. Layout-specific pins are:

| GPIO | Target net | Note |
|---:|---|---|
| 3 | reserved strap | no external driver |
| 6 | `RFCTRL_CS` | pull-high; third controller endpoint |
| 35/36/37 | `AUX_SPI3_SCK/MOSI/MISO` | shared C5/RF-controller bus; requires N8R2 |
| 38/39 | `C5_CS/C5_DRDY` | C5 endpoint |
| 46 | `RFCTRL_IRQ` | input-only strap, reset-safe source |

All exposed S3 GPIO are allocated except reserved strap GPIO3; N8R8 is impossible because the shared auxiliary bus uses GPIO35..37.

## ESP32-C5 direct-pin allocation

| GPIO | Target net | Note |
|---:|---|---|
| 0/1 | `IR_RX_ROBUST/IR_RX_CARRIER` | both RMT RX |
| 2 | `IR_TX` | RMT TX, hardware-off default |
| 6/23/24 | `C5LINK_MISO/SCK/MOSI` | C5 GP-SPI slave on auxiliary bus |
| 8/9 | `C5LINK_CS/DRDY` | endpoint select/event |
| 13/14 | `USB_D-/D+` | native recovery |
| 26/28 | BOOT straps | physical recovery |
| 27 | strap pull | fixed safe state |
| 3/4/5/7/10/11/12/25 | reserve | strap restrictions remain on 3/25 |

## RP2040 allocation

| RP2040 GPIO/resource | Target |
|---|---|
| SPI0 GPIO0..3 | S3 auxiliary-bus slave `RX/CSn/SCK/TX` |
| GPIO4 | host IRQ/data-ready, reset-safe low/inactive |
| SPI1 GPIO10/11/12 | nRF `SCK/MOSI/MISO` |
| GPIO13/14/15 | `NRF1/2/3_CSN`, pull-high |
| GPIO16/17/18 | `NRF1/2/3_CE`, pull-low and `TX_KILL` clear |
| GPIO19/20/21 | individual nRF IRQ inputs |
| dedicated QSPI | W25Q64JV 8 MiB firmware A/B/recovery metadata |
| `RUN` | reset by `TX_KILL` and service header |
| SWD + BOOTSEL | independent recovery/test pads |

Local firmware owns radio roles, timestamps, CE/CS state and FIFO service. S3 receives typed events/capture records; it does not bit-bang nRF control through IPC.

## Traffic, memory, trust and power

- RP2040 reserves ≥96 KiB bounded nRF rings/metadata and keeps ≥64 KiB SRAM free at the largest radio scenario; host backpressure increments explicit loss/gap counters.
- Shared S3 SPI3 must deliver measured aggregate payload ≥4.2 MB/s so C5 `1.5+0.5 MB/s` and RF-controller `0.9 MB/s` reservations retain the common 30% headroom; endpoint control latency keeps the stricter C5/nRF deadlines.
- RP2040 local nRF IRQ service still meets p99≤250 µs/max≤400 µs independently of S3 display/SD.
- The added controller/flash/crystal/passives/mezzanine reserve ≤0.10 A on 3.3 V; total remains below the existing 3 A rail rating but reduces autonomy and thermal margin relative to two-MCU variants.
- The third image requires owner-controlled signing, A/B update, versioned protocol/SBOM and rollback. BOOTSEL/SWD preserves open developer recovery and avoids irreversible lockdown.
- `TX_KILL` resets all three MCUs and independently removes/inhibits every nRF TX path; a hung RP2040 cannot retain CE or PA power.

## UI and recovery

The same matrix/U14 alternatives are pin-compatible with this layout. S3 and C5 retain their native USB recovery; RP2040 adds SWD/BOOTSEL service pads. A firmware update is not accepted unless any one corrupted image can be recovered without working code on that same processor.

## Static hard-gate review

| Gate | Static result | Remaining proof |
|---|---|---|
| HF-01..05 | functions and single nRF owner allocated | third-domain firmware/scenario HIL |
| HF-06/07 | independent reset/power-clear path allocated | exact mezzanine gates/detectors |
| HF-08 | no duplicate/unavailable MCU pin | shared-bus electrical/strap fixture |
| HF-09 | S3 N8R2 and RP2040 are conditional | both measured memory floors |
| HF-10 | conditional pass only | ≥4.2 MB/s shared auxiliary-bus payload and failure recovery |
| HF-11 | three independent physical recovery paths allocated | signed A/B/recovery fixture for RP2040 |
| HF-12/13 | profiles retained; rail class still fits | exact current/RF/thermal/mezzanine evidence |
| HF-14 | topology uses public MCU interfaces | new bootloader/SBOM/version evidence required |

## Candidate conclusion

This layout is statically feasible and offers the strongest nRF ISR isolation and radio-module serviceability. It necessarily adds a third MCU trust/update domain, flash, clock, passives, connector/board and production test, while retaining S3 N8R2 memory risk. It cannot be a zero-loss cost recommendation unless measured two-MCU layouts fail their performance gates.

## Primary source

- [Raspberry Pi RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)

