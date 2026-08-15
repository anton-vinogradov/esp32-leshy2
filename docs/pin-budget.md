# Leshy2 — GPIO budget

*Read this in: **English** · [Русский](pin-budget.ru.md)*

Leshy2 is a **two-chip** design, and the split (stage 5) moved the 2.4 GHz-raw and IR work onto the co-processor, so the two chips now sit closer on the pin-pressure scale:

- **ESP32-S3-WROOM-1U-N8R2** — the main brain. It runs the UI, the display, **every wired radio**, the SD card and all the buses, plus native 2.4 GHz Wi-Fi + BLE. Handing the **3× nRF24 and the IR** to the C5 frees four direct pins, and dropping the S3→C5 UART flash bridge frees two more, so it now sits at **30 / 36 — six direct-pin spare** (it was 36 / 36 before the split).
- **ESP32-C5-WROOM-1U** — the co-processor. Native **5 GHz** Wi-Fi (plus 802.15.4 / Zigbee / Thread), and it now **drives the 3× nRF24 and the IR** on its own GPIO, talking to the S3 over a dedicated link. That takes it to **~17 of ~20** GPIO — snug but it fits.

Fitting this much radio onto the two chips rests on one rule:

> **Buses and the CS decoder reuse across radios; per-chip timing lines do not.** Every SPI radio shares one 3-wire bus, and one 74HC138 turns 3 pins into 8 chip-selects — genuinely shared. But each radio's own timing-critical line (CC1101 `GDO0`, LoRa `BUSY`/`DIO1`, the encoder — and, on the C5, the nRF24 `CE`/`IRQ` and IR TX/RX) runs to a different chip on its own trace, so those pins **add up** — they are not a reusable pool.

Three slow-signal **I²C expanders (PCA9555 ×3)** carry the low-speed control lines (resets, PTT, power-downs, rail gates, the band switch, the encoder button) for **0 host GPIO** — they ride the I²C bus. That is what lets 30-plus control signals live on a chip with no free pins.

> ⚠️ **Design stage. The GPIO numbers are a proposed map**, not yet confirmed against the datasheets. Functions are fixed; exact pin numbers may shift. The authoritative pin-by-pin table is [Sheet 2 — MCU + buses](../hardware/c5-buses/c5-buses.md).

## Why so much radio fits on two chips

Nine antennas and seven radios do **not** cost seven radios' worth of pins, because most of the wiring is shared or offloaded:

| Mechanism | Pins it costs | What it carries |
|---|:--:|---|
| One shared **SPI2** bus (S3) | 3 | SD + CC1101 + SX1262 + ST7796 display — three wires (the 3× nRF24 moved to the C5's own SPI) |
| **74HC138** CS decoder (S3) | 3 | 8 chip-selects from 3 pins (SD, CC1101, LoRa, display + spares) |
| One shared **I²C** bus (S3) | 2 | Si4732 · BQ25887 · 3× PCA9555 · 2× Grove · RFID2 |
| **3× PCA9555** slow-line expanders | **0** | ~30 resets / enables / PTT / T-R / rail gates / band-switch / buttons |
| The **C5 co-processor** | 5 (link block) | offloads 5 GHz / Zigbee **and now the 3× nRF24 + IR** to the second chip over one SPI3 link |

Only genuinely **timing-critical** lines get a dedicated host pin. Everything slow is either on a bus or on an expander.

## S3 budget — 30 / 36 (six spare after the split)

The 36 usable pins (GPIO0–21, 35–48 — **GPIO33/34 are not bonded out on the WROOM-1U module**) now split into:

| Group | Pins | Lines |
|---|:--:|---|
| **Shared buses** | 12 | SPI2 `SCK/MOSI/MISO` (3) · I²C `SDA/SCL` (2) · `74HC138 A/B/C` (3) · SA868 `UART1 TX/RX` (2) · Grove-UART GPS `UART2 RX/TX` (2) — broken out to a Grove-UART header for an external M5 GPS Unit |
| **Timing-critical direct** (they sum) | 8 | `WS2812` · `LoRa_DIO1` · `CC1101_GDO0` · `LoRa_BUSY` · `LCD_DC` · `LCD_TE` · `ENC_A` · `ENC_B` |
| **One interrupt** | 1 | `CC1101_GDO2` — no longer forced onto a strap pin (see below) |
| **C5-link block** (quad-freed 35–39) | 5 | SPI3 `SCK/MOSI/MISO/CS` · `DRDY` — `C5_EN` → **PCA9555 #2** (GPIO33/34 not bonded) |
| **USB · boot · expander INT** | 4 | `USB D−/D+` (2) · `S3_BOOT` (1) · `PCA9555_INT` (1) |

```
Shared buses ...................... 12
Timing-critical direct ............ +8   (these add up, one per chip)
One interrupt ..................... +1   (CC1101_GDO2)
C5-link block ..................... +5   (SPI3 + DRDY on 35–39; C5_EN → expander)
USB + boot + INT .................. +4
                                    = 30 / 36 — six direct-pin spare
```

**The strapping-pin crunch is gone.** At 36 / 36 the last two pins were forced onto boot straps (GPIO45/46); freeing six pins removes that pressure:

- **GPIO46** carried `nRF24_IRQ`. That line now lives on the C5 — GPIO46 is free, and the 74AHC gate that combines the three nRF24 IRQs moves to the C5 side.
- **GPIO45 / `CC1101_GDO2`** can now move to any freed non-strap pin, so the `espefuse.py set_flash_voltage 3.3V` de-strap burn is **no longer required** — keep it only if the final map still lands GDO2 on 45.

The **quad-PSRAM** choice is still load-bearing: octal PSRAM (`R8`) steals GPIO33–37 for its data lines, but **quad PSRAM frees 35–37** — the window the SPI3 link sits in. (GPIO33/34 are *not bonded out on the WROOM-1U* at all, so the C5_EN line rides PCA9555 #2.) The pin budget, not the RAM size, drives the N8R2 choice.

## C5 budget — ~17 / ~20 (snug)

The C5 is no longer a bare co-processor: it drives the whole 2.4 / 5 GHz + IR block. It stays an SPI **slave** on the link to the S3, but it is also an SPI **master** to the three nRF24 and runs the IR carrier itself.

| Use | Pins | Lines |
|---|:--:|---|
| Dedicated **SPI3 link** to S3 (slave) | 5 | `SCK` · `MOSI` · `MISO` · `CS` · `DRDY` |
| **3× nRF24** (SPI master) | 7 | SPI `SCK/MOSI/MISO` (3) · shared `CE` (1) · combined `IRQ` (1) · 3× CS via a **74HC139** (2) |
| **IR** TX / RX | 2 | 38 kHz carrier (RMT) + receiver |
| **Reset / boot** | 1 | `EN` from S3, plus a physical **RESET + BOOT** button pair — no S3-driven `C5_BOOT` *line* (that was for UART flashing), but a user BOOT button on the download-strap for recovery (no usable-GPIO cost) |
| Own **USB-C** (flash + brick-safe) | 2 | `USB D− / D+` |

That is ~17 GPIO used, ~3 spare. The S3→C5 **UART flash bridge is dropped** — the C5 flashes over its own USB-C and takes firmware as OTA over the link — which is exactly what frees the two C5 pins the nRF / IR need. In-package flash occupies GPIO15–22 (minus 19), so the map is drawn around those.

## The trade that made it fit

An earlier draft gave the C5 a **standalone display** (its own screen with a mode-slider mux). That was the most fragile node in the design, and it cost pins on both chips. Dropping it turned the C5 into a clean co-processor and freed S3 **GPIO3**, which now carries `LoRa_DIO1` — so **LoRa RX is interrupt-driven** instead of polled.

The stage-5 split then went further: moving the nRF24 + IR to the C5 took the S3 from 36 / 36 down to 30 / 36 and cleared both strap pins, at the cost of filling the C5 to ~17 / 20. Everything else that could be slow still rides the **PCA9555** expanders — PTT button, rail-enable gates, SP4T band-switch bit, headphone-jack detect — none of which cost a host pin.

## If a spare pin is ever needed

The S3 is comfortable at 30 / 36. The pressure, such as it is, is now on the **C5** at ~17 / 20:

- The S3→C5 UART flash bridge is already spent — dropping it is what made room for the nRF / IR on the C5, so it is no longer a lever.
- On the C5, **fixed-delay nRF handling** (poll instead of the combined IRQ) frees 1 pin; the 74HC139 can grow to a 74HC138 if a fourth nRF-side select is ever needed.
- On the S3, **fixed-delay `LoRa_BUSY`** frees a pin it no longer needs — pure headroom.

None is needed for the locked design; they are headroom, not compromises.

---

*The authoritative pin-by-pin tables (S3 map, C5 map, 74HC138, the three PCA9555, the S3↔C5 link) live in [Sheet 2 — MCU + buses](../hardware/c5-buses/c5-buses.md).*
*Part of [Leshy2](../README.md) · MIT.*
