# Leshy2 — MCU + buses sheet (Sheet 2)

*Read this in: **English** · [Русский](c5-buses.ru.md)*

The two MCUs and how every bus fans out from them. Leshy2 is a **dual-MCU** design: an **ESP32-S3** main brain that runs the UI, the display, all wired radios, the SD card and every bus; and an **ESP32-C5** **co-processor** that adds the one thing the S3 lacks — native **5 GHz Wi-Fi** (plus 2.4 GHz, BLE and **802.15.4** / Zigbee / Thread). The C5 is a *pure co-processor*: it talks to the S3 over a dedicated link and never touches the shared bus. There is **no mode switch** — the S3 always owns the device.

> ⚠️ Design stage. **GPIO numbers are a proposed map**, not yet confirmed against the ESP32-S3 / ESP32-C5 datasheets. Before capture, confirm: strapping-pin boot levels on both chips, which pins reach FSPI/SPI3/RMT/I²C through the GPIO matrix, that the C5 module actually bonds out the pins used for the link, and the N8R2 (quad-PSRAM) part number. Functions are fixed; exact pin numbers may shift.

> 🗂️ *The folder is named `c5-buses/` for historical reasons (the earlier single-chip design). It now covers both MCUs.* The transcribe-ready schematic drawing for this sheet is being redrawn for the two-chip layout.

## The two MCUs

**U10 — ESP32-S3-WROOM-1U-N8R2** (main brain): dual-core Xtensa, 8 MB flash + **2 MB quad PSRAM**, native 2.4 GHz Wi-Fi + BLE, u.FL → external SMA.

- **Quad PSRAM is deliberate.** Octal PSRAM (the `R8` parts) steals GPIO33–37 for its extra data lines; **quad PSRAM leaves 33–37 free**, and that is exactly where the C5-link block sits. We only need ~300 KB for the 320×480×16 framebuffer (double-buffered ~600 KB), so 2 MB quad is plenty — the pin budget, not the RAM size, drives the choice.
- Native USB is on GPIO19/20. The serial **console runs over the USB-Serial-JTAG** peripheral (not a UART), which frees UART0 for the C5 flash bridge.

**U20 — ESP32-C5-WROOM-1U** (co-processor): single RISC-V core, in-package flash, native **2.4 + 5 GHz Wi-Fi + BLE + 802.15.4**, u.FL → its own external dual-band SMA. It is the *only* ESP32 with native 5 GHz. In-package flash occupies **GPIO15,16,17,18,20,21,22** (so **GPIO19 is free, GPIO15 is not** — the opposite of what earlier drafts said); native USB is on GPIO13/14. All of the C5's radios are on-chip; it never uses the external SPI bus.

## S3 GPIO map (proposed)

38 usable GPIO (0–21, 33–48, minus USB pair use). **Used: 36 / 38**, with GPIO45/46 as strap-only pulldown reserves.

| S3 GPIO | Net | Dir | Peripheral / note |
|:--:|------|:--:|-------|
| GPIO0 | `S3_BOOT` (button) | in | ⚠ strap, pull-up; recovery button |
| GPIO1 | `WS2812` | out | RMT; 3.3→5 V buffer 74AHCT1G125 (Sheet 6) |
| GPIO2 | `IR_TX` | out | RMT/LEDC 38 kHz carrier (not a strap on S3) |
| GPIO3 | `LoRa_DIO1` | in | ⚠ strap (JTAG-sel, boot don't-care); SX1262 RxDone/timeout IRQ → **LoRa RX is interrupt-driven** |
| GPIO4 | `I2C_SDA` | o-d | 4.7 kΩ; Si4732 / PCA9555 / BQ25887 / Grove |
| GPIO5 | `I2C_SCL` | o-d | 4.7 kΩ |
| GPIO6 | `nRF24_CE` | out | shared across all 3× nRF24 (timing → direct) |
| GPIO7 | `CC1101_GDO0` | i/o | RMT: raw OOK RX / replay |
| GPIO8 | `HC138_A` | out | CS decoder 3→8 |
| GPIO9 | `HC138_B` | out | |
| GPIO10 | `HC138_C` | out | |
| GPIO11 | `SPI_MOSI` | out | **FSPID, IOMUX 80 MHz**: SD + CC1101 + 3× nRF24 + SX1262 + ST7796 |
| GPIO12 | `SPI_SCK` | out | FSPICLK, IOMUX |
| GPIO13 | `SPI_MISO` | in | FSPIQ, IOMUX; 8+ dummy clocks after SD deselect |
| GPIO14 | `LCD_DC` | out | per-byte data/command (timing → direct) |
| GPIO15 | `LoRa_BUSY` | in | polled before each SX1262 command |
| GPIO16 | `SA868_UART_TX` | out | UART1 → walkie |
| GPIO17 | `SA868_UART_RX` | in | UART1 ← walkie |
| GPIO18 | `GPS_UART_RX` | in | UART2, NMEA (required) |
| GPIO19 | `USB_D−` | io | native USB + **console via USB-Serial-JTAG** |
| GPIO20 | `USB_D+` | io | native USB |
| GPIO21 | `LCD_TE` | in | tearing/vsync from ST7796 (timing → direct) |
| GPIO33 | `C5_EN` | out | *(quad-freed)* C5 reset, open-drain; not gated in normal use |
| GPIO34 | `C5_BOOT` | out | *(quad-freed)* → C5 GPIO26 **and** GPIO28 (download strap combo) |
| GPIO35 | `C5LINK_SCK` | out | *(quad-freed)* **SPI3** dedicated link, S3 = master |
| GPIO36 | `C5LINK_MOSI` | out | SPI3 |
| GPIO37 | `C5LINK_MISO` | in | SPI3; carries the whole C5→S3 stream |
| GPIO38 | `C5LINK_CS` | out | select C5 slave + wake it from light-sleep |
| GPIO39 | `C5LINK_DRDY` | in | C5→S3 interrupt **and** ready-strobe (see link section) |
| GPIO40 | `ENC_A` | in | pull-up, quadrature |
| GPIO41 | `ENC_B` | in | pull-up (encoder `SW` → PCA9555) |
| GPIO42 | `IR_RX` | in | RMT; TSOP38238 |
| GPIO43 | `C5_FLASH_TX` | out | U0TXD → C5 U0RXD (C5 flash bridge) |
| GPIO44 | `C5_FLASH_RX` | in | U0RXD ← C5 U0TXD |
| GPIO47 | `GPS_UART_TX` | out | UART2, optional (config only) |
| GPIO48 | `PCA9555_INT` | in | expander interrupt |
| GPIO45 | — reserve | — | ⚠ strap VDD_SPI: hold **LOW** (high = brick); pulldown line only |
| GPIO46 | — reserve | — | ⚠ strap: LOW at boot |

The 16 slow control lines (radio resets, backlight/amp/decoder enables, PTT, audio mux, CC1101 band switch, LoRa T/R, buzzer, charger `CD`, encoder `SW`, SD card-detect) ride the **PCA9555 (0x20)** — 0 host GPIO. Battery gauge is read from the **BQ25887's own I²C ADC** (no ADC pin).

*Dropping the C5-standalone-display capability freed GPIO3 (formerly the mode-slider sense); it now carries `LoRa_DIO1`, so LoRa RX is interrupt-driven instead of polled — less traffic on the shared bus.*

## C5 GPIO map (proposed — confirm against datasheet)

~20 usable GPIO. **Used ~11**, roomy — the C5 is only a co-processor now (no shared-bus role, no mux, no standalone mode).

| C5 GPIO | Net | Dir | Note |
|:--:|------|:--:|-------|
| EN (pin) | `C5_EN` ← S3 | in | reset + RC; not gated in normal use |
| GPIO26 + GPIO28 | `C5_BOOT` ← S3 | in | ⚠ strap: **both = 0 → download, both = 1 → normal**; tie together to S3 GPIO34 |
| GPIO27 | (strap) | — | ⚠ must be pulled **high** for a valid boot; not driven |
| GPIO23 | `LINK_SCK` ← S3 | in | SPI slave clock (dedicated SPI3 link) |
| GPIO24 | `LINK_MOSI` ← S3 | in | |
| GPIO6 | `LINK_MISO` → S3 | out | carries the C5→S3 data stream |
| GPIO8 | `LINK_CS` ← S3 | in | slave select |
| GPIO9 | `DRDY` → S3 | out | the one async line C5→S3 |
| GPIO11 | `U0TXD` → S3 | out | UART0, flash path + bench test-pad |
| GPIO12 | `U0RXD` ← S3 | in | UART0, flash path + bench test-pad |
| GPIO13 / GPIO14 | `USB_D− / D+` | io | native USB → **dedicated C5 USB-C port** (brick-safe recovery/flash/debug) |

The C5 is a clean SPI slave on the dedicated link plus its flash/USB paths — nothing on the shared bus, so there is no non-strap constraint to juggle and no bus-contention risk from the C5 side. ~9 GPIO spare for future co-processor duties.

## The S3↔C5 link — dedicated SPI3

The link is on the S3's **second free SPI host (SPI3)**, kept off the shared radio/SD/display bus so the C5's 5 GHz capture stream never competes with radio or display traffic, and so there is never a two-master contention on the main bus. The C5's single SPI controller is dedicated to this link (there is no mux — the standalone-display capability that once needed one was dropped).

| Signal | Direction | S3 / C5 |
|---|---|---|
| `C5LINK_SCK` | **S3 → C5** | 35 / 23 |
| `C5LINK_MOSI` | **S3 → C5** | 36 / 24 |
| `C5LINK_MISO` | **C5 → S3** | 37 / 6 |
| `C5LINK_CS` | **S3 → C5** | 38 / 8 (+ wake) |
| `C5LINK_DRDY` | **C5 → S3** | 39 / 9 |
| `C5_EN` | **S3 → C5** | 33 / EN |
| `C5_BOOT` | **S3 → C5** | 34 / 26+28 |

**No reverse wire beyond DRDY is needed.** The whole C5→S3 payload rides `MISO` (the S3 always clocks); `DRDY` is the single asynchronous "I have data / an event" line. One catch: an ESP32 SPI-slave must pre-load its TX buffer before the master starts clocking, so **`DRDY` doubles as a ready-strobe** — the S3 begins the clock only after the C5 raises `DRDY`. No separate `ACK`/`HOST_READY` line.

## Flashing both chips

- **S3:** over its native USB (GPIO19/20). Console shares the same port via USB-Serial-JTAG. `S3_BOOT` (GPIO0) + `RESET` (EN) buttons force download. The **main USB-C** connector serves the S3 (charging + S3 flash/console); the C5 has its own separate port (below). There is no USB mux.
- **C5 has its own USB-C port** (the simplest recovery path): the C5's native USB (D−/D+, GPIO13/14) wires to a **dedicated connector**. **Brick-safe** — the C5's USB-Serial-JTAG lives in mask ROM, so this port reflashes the C5 even if its firmware is dead. Flash, console and JTAG-debug any C5 firmware straight from a PC — this is how you run your own 5 GHz / Zigbee experiments and rescue a bad flash. VBUS on this port is used only for USB-detect + ESD, **not** as a power/charge input.
- **C5 automatic OTA (optional):** the **S3 can also flash the C5** over UART0 — `C5_FLASH_TX/RX` (GPIO43/44) → C5 `U0RXD/U0TXD` (GPIO11/12), `C5_BOOT` (26+28) low + an `EN` pulse — so an S3 update carries a matched C5 image and keeps both chips in sync without plugging in. Version/CRC-gated. *(Now optional given the C5 USB port; dropping this bridge would free 2 S3 pins.)*

## 74HC138 — chip-select map

| Output | Chip-select | On the SPI sheet |
|:--:|------|------|
| Y0 | `SD_CS` | microSD |
| Y1 | `CC1101_CS` | sub-GHz |
| Y2 | `nRF24_1_CSN` | 2.4 raw #1 |
| Y3 | `nRF24_2_CSN` | 2.4 raw #2 |
| Y4 | `nRF24_3_CSN` | 2.4 raw #3 |
| Y5 | `LoRa_NSS` | SX1262 |
| Y6 | `LCD_CS` | ST7796 display |
| Y7 | (none) | idle / deselect-all address |

`G1` = +3V3, `G2B` = GND, **`G2A` = `HC138_EN`** (a PCA9555 output, pulled high = disabled at boot) — it stays disabled through the strap window and is a boot-gate only, not a per-transaction gate (I²C is too slow for that). Fast deselect = park `A/B/C` on **Y7**; step through Y7 between any two selects to avoid a glitch on an intermediate address.

## PCA9555 — slow-signal map (I²C 0x20, 0 host GPIO)

| Port | Signal | Dir | Port | Signal | Dir |
|:--:|------|:--:|:--:|------|:--:|
| P0.0 | `ENC_SW` | in | P1.0 | `BQ_INT` | in |
| P0.1 | `SA868_PTT` | out | P1.1 | `BQ_CD` | out |
| P0.2 | `SA868_PD` | out | P1.2 | `LoRa_TR` | out |
| P0.3 | `Si4732_RST` | out | P1.3 | `PAM_SD` | out |
| P0.4 | `LoRa_NRESET` | out | P1.4 | `LCD_BL_EN` | out |
| P0.5 | `BUZZER` | out | P1.5 | `RFSW_CTL` | out |
| P0.6 | `LCD_RESX` | out | P1.6 | `HC138_EN` | out |
| P0.7 | `MUX_SEL` | out | P1.7 | `SD_CD` | in |

Timing-critical lines never go here — only resets, enables, PTT, mux selects and buttons.

## Reset & boot buttons

Two physical buttons on the S3; power on/off is the **master switch** (Sheet 1) — there is no soft power button and no mode switch.

- **RESET** — momentary across S3 **EN**–GND (10 kΩ pull-up + 1 µF RC).
- **BOOT** — momentary from S3 **GPIO0** to GND; hold BOOT and tap RESET to force USB download.

The C5 has no buttons — the S3 drives its `EN`/`BOOT`; its own USB-C port is the manual recovery path (mask-ROM USB-JTAG, brick-safe).

## Shared-bus notes (firmware, not hardware)

The one SPI2 bus is shared by SD + radios + display, serviced one device at a time. Measured worst-case utilisation is ~11–21% (almost all of it bursty SD writes; radios + waterfall < 0.5%), so contention is not a hardware problem — it is handled in firmware:

- **DMA + double-buffer** the full-frame blits (the only real cost: a 30–60 ms CPU busy-wait) so the UI never stalls. DMA unloads the CPU; the bus stays serial, and smoothness rides the radios' own FIFOs.
- **Bus arbiter:** one mutex, radio reads and waterfall scroll take priority over full redraws; preempt SD/display transfers at a CS/chunk boundary (deassert, service the radio, resume).
- **Watchdog the SD transactions:** a card stuck in a GC stall could hold the shared `MISO` and break radio reads — time out and re-init the card.

## Gotchas

- **Quad PSRAM is load-bearing.** Only the N8R2 (quad) frees GPIO33–37; an octal-PSRAM S3 does not fit the link.
- **Strap discipline.** S3 straps {0, 3, 45, 46} — keep GPIO45 low (high bricks VDD_SPI); GPIO3 is JTAG-sel (boot don't-care), fine for `LoRa_DIO1`. C5 straps {26, 27, 28} — tie 26+28 to `C5_BOOT`, pull 27 high.
- **Tight S3 budget.** 36/38, two strap-reserve pins. A new fast signal means a second PCA9555 or dropping an existing direct line.
- **Polled vs interrupt.** `LoRa_DIO1` is now a real interrupt (GPIO3); `LoRa_BUSY` and the nRF24 IRQs stay polled over SPI to save pins.
- **Two USB-C ports, one power source.** The C5 port is data-only (VBUS → USB-detect/ESD, not the system rail); the pack charges only through the S3 port's BQ25887. No two-source conflict.
- **Confirm before KiCad:** the S3 is really an `N8R2`; the C5 module bonds out GPIO23/24; the exact C5 strap table; RMT/FSPI/SPI3/UART matrix routing.

---

*Next sheets: (3) RF chains, (4) audio, (5) expansion, (6) indicators/IO. Previous: (1) [power](../power/power.md).*
*Part of [Leshy2](../../README.md) · MIT.*
