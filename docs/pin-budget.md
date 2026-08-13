# Leshy2 — GPIO budget

*Read this in: **English** · [Русский](pin-budget.ru.md)*

Leshy2 is a **two-chip** design, and the two chips sit at opposite ends of the pin-pressure scale:

- **ESP32-S3-WROOM-1U-N8R2** — the main brain. It runs the UI, the display, **every wired radio**, the SD card and all the buses, plus native 2.4 GHz Wi-Fi + BLE. Its 36 usable GPIO are **all spoken for — 36 / 36, zero direct-pin spare.**
- **ESP32-C5-WROOM-1U** — the co-processor. It adds the one thing the S3 lacks (native **5 GHz** Wi-Fi, plus 802.15.4 / Zigbee / Thread) and talks to the S3 over a dedicated link. It uses only **~11 of ~20** GPIO — roomy.

Fitting this much radio onto the S3's 36 pins rests on one rule:

> **Buses and the CS decoder reuse across radios; per-chip timing lines do not.** Every SPI radio shares one 3-wire bus, and one 74HC138 turns 3 pins into 8 chip-selects — genuinely shared. But each radio's own timing-critical line (CC1101 `GDO0`, LoRa `BUSY`/`DIO1`, nRF24 `CE`/`IRQ`, IR TX/RX, encoder) runs to a different chip on its own trace, so those pins **add up** — they are not a reusable pool.

Three slow-signal **I²C expanders (PCA9555 ×3)** carry the low-speed control lines (resets, PTT, power-downs, rail gates, the band switch, the encoder button) for **0 host GPIO** — they ride the I²C bus. That is what lets 30-plus control signals live on a chip with no free pins.

> ⚠️ **Design stage. The GPIO numbers are a proposed map**, not yet confirmed against the datasheets. Functions are fixed; exact pin numbers may shift. The authoritative pin-by-pin table is [Sheet 2 — MCU + buses](../hardware/c5-buses/c5-buses.md).

## Why so much radio fits on one full chip

Nine antennas and seven radios do **not** cost seven radios' worth of pins, because most of the wiring is shared or offloaded:

| Mechanism | Pins it costs | What it carries |
|---|:--:|---|
| One shared **SPI2** bus | 3 | SD + CC1101 + 3× nRF24 + SX1262 + ST7796 display — six devices, three wires |
| **74HC138** CS decoder | 3 | 8 chip-selects from 3 pins (SD, CC1101, 3× nRF24, LoRa, display, spare) |
| One shared **I²C** bus | 2 | Si4732 · BQ25887 · 3× PCA9555 · 2× Grove · RFID2 |
| **3× PCA9555** slow-line expanders | **0** | ~30 resets / enables / PTT / T-R / rail gates / band-switch / buttons |
| The **C5 co-processor** | 7 (link block) | offloads all of 5 GHz / Zigbee to a second chip over one SPI3 link |

Only genuinely **timing-critical** lines get a dedicated host pin. Everything slow is either on a bus or on an expander.

## S3 budget — 36 / 36 (the ceiling)

The 36 usable pins (GPIO0–21, 35–48 — **GPIO33/34 are not bonded out on the WROOM-1U module**) split into five groups:

| Group | Pins | Lines |
|---|:--:|---|
| **Shared buses** | 12 | SPI2 `SCK/MOSI/MISO` (3) · I²C `SDA/SCL` (2) · `74HC138 A/B/C` (3) · SA868 `UART1 TX/RX` (2) · GPS `UART2 RX/TX` (2) |
| **Timing-critical direct** (they sum) | 11 | `WS2812` · `IR_TX` · `IR_RX` · `LoRa_DIO1` · `nRF24_CE` · `CC1101_GDO0` · `LoRa_BUSY` · `LCD_DC` · `LCD_TE` · `ENC_A` · `ENC_B` |
| **Two interrupts at the ceiling** | 2 | `CC1101_GDO2` (GPIO45) · `nRF24_IRQ` (GPIO46) — the last two pins, both straps (see below) |
| **C5-link block** (quad-freed 35–39) | 5 | SPI3 `SCK/MOSI/MISO/CS` · `DRDY` — `C5_EN`/`C5_BOOT` → **PCA9555 #2** (GPIO33/34 not bonded) |
| **USB · C5-flash bridge · boot · expander INT** | 6 | `USB D−/D+` (2) · `C5_FLASH TX/RX` (2) · `S3_BOOT` (1) · `PCA9555_INT` (1) |

```
Shared buses ...................... 12
Timing-critical direct ............ 11   (these add up, one per chip)
Interrupts at the ceiling ......... +2   (GPIO45/46, both straps)
C5-link block ..................... +5   (SPI3 + DRDY on 35–39; C5_EN/C5_BOOT → expander)
USB + flash bridge + boot + INT ... +6
                                    = 36 / 36 — no direct-pin spare
```

**Why the last two pins are strapping pins.** GPIO45 and GPIO46 are the only pins left, and both are boot straps — handled at the root, not worked around:

- **GPIO45** carries `CC1101_GDO2` (carrier-sense wake). It is **de-strapped by an eFuse** (`espefuse.py set_flash_voltage 3.3V`, burned once before first boot), so the ROM ignores its level at power-on — GDO2's idle state is then harmless. Only valid on the 3.3 V N8R2 part; never on a 1.8 V octal-PSRAM S3.
- **GPIO46** carries `nRF24_IRQ`. The three nRF24 IRQ outputs are combined by a **74AHC 3-input gate** into one **idle-low** interrupt, which is exactly what the GPIO46 boot strap wants to see.

The **quad-PSRAM** choice is load-bearing here: octal PSRAM (`R8`) steals GPIO33–37 for its data lines, but **quad PSRAM frees 35–37** — the window the SPI3 link sits in. (GPIO33/34 are *not bonded out on the WROOM-1U* at all, so the two C5-control lines ride PCA9555 #2.) The pin budget, not the RAM size, drives the N8R2 choice.

## C5 budget — ~11 / ~20 (roomy)

The C5 is a pure co-processor: an SPI slave on the dedicated link, plus its own flash and USB paths. Nothing touches the shared bus.

| Use | Pins | Lines |
|---|:--:|---|
| Dedicated **SPI3 link** to S3 | 5 | `SCK` · `MOSI` · `MISO` · `CS` · `DRDY` |
| **Reset / boot** from S3 | 2 | `EN` (pin) · `BOOT` (GPIO26+28 strap combo) |
| **Flash bridge** (auto-OTA from S3) | 2 | `U0TXD / U0RXD` |
| Own **USB-C** (brick-safe recovery) | 2 | `USB D− / D+` |

That is ~11 GPIO used, leaving ~9 spare for future co-processor duties. In-package flash occupies GPIO15–22 (minus 19), so the map is drawn around those; but with no shared-bus role and no mux, the C5 has no crowding to solve.

## The trade that made 36 fit

An earlier draft gave the C5 a **standalone display** (its own screen with a mode-slider mux). That was the most fragile node in the design, and it cost pins on both chips. Dropping it:

- removed both analog muxes and the slider, turning the C5 into a clean co-processor;
- freed S3 **GPIO3**, which now carries `LoRa_DIO1` — so **LoRa RX is interrupt-driven** instead of polled, cutting traffic on the shared bus.

Everything else that could be slow was pushed onto the **second PCA9555** (0x21) — PTT button, rail-enable gates, SP4T band-switch bit, headphone-jack detect — none of which cost a host pin. Direct GPIO is full at 36 / 36, but slow-line headroom is now generous.

## If a spare pin is ever needed

Direct GPIO is exhausted, but two levers each free a host pin without touching the radios:

- **Drop the C5 flash bridge** (GPIO43/44) — the C5 already has its own USB-C for flashing, so the S3-side UART bridge is optional. Frees **2 pins**.
- **Fixed-delay `LoRa_BUSY`** — poll a timer instead of the pin. Frees **1 pin**.

Neither is needed for the locked design; they are headroom, not compromises.

---

*The authoritative pin-by-pin tables (S3 map, C5 map, 74HC138, the three PCA9555, the S3↔C5 link) live in [Sheet 2 — MCU + buses](../hardware/c5-buses/c5-buses.md).*
*Part of [Leshy2](../README.md) · MIT.*
