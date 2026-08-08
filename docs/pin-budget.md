# Leshy2 — GPIO budget by usage mode

*Read this in: **English** · [Русский](pin-budget.ru.md)*

Leshy2 runs **one radio mode at a time**, so the radios share a small pool of GPIO. The peak pin count is the heaviest single mode, not the sum of all radios. The ESP32-C5 gives about **19 usable GPIO** after flash/PSRAM and USB.

![GPIO budget by mode](img/pin-budget.svg)

**Base — always used (11 pins):** SPI ×3, 74HC138 chip-selects ×3, I²C ×2, encoder ×2, WS2812 ×1. **Display:** 1-bit SPI +1 · QSPI +5. **Mode pool:** up to 4 shared pins, reused across mutually-exclusive modes.

Below: for every mode, what each pin does **in that mode**. With a 1-bit SPI display every mode has margin; with QSPI, `LoRa + GPS` overflows (20 > 19) and several modes sit at the ceiling.

### Menu / idle

Pins: **SPI 12 / QSPI 16** (of 19)

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool` | — |

### WiFi 2.4/5 (Marauder)

Pins: **SPI 12 / QSPI 16** (of 19)

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → microSD (PCAP) |
| `74HC138 A/B/C` (3) | chip-select decoder → SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool` | — |

> The 2.4/5 GHz radio lives inside the C5 — no external control pins.

### 2.4 scan (nRF24×3)

Pins: **SPI 13 / QSPI 17** (of 19)

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → nRF24 ×3 + microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → nRF24 ×3, SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool · CE` | arm RX on the mousejack-capable module; the other two hold CE high (pure RX) |

### Mousejack (nRF24×3 TX)

Pins: **SPI 15 / QSPI 19** (of 19) ⚠️

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → nRF24 ×3 + microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → nRF24 ×3, SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool · CE1` | arm/TX module #1 |
| `pool · CE2` | arm/TX module #2 |
| `pool · CE3` | arm/TX module #3 |

### Sub-GHz (CC1101)

Pins: **SPI 14 / QSPI 18** (of 19) ⚠️

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → CC1101 + microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → CC1101, SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool · GDO0` | packet / data-ready interrupt from CC1101 |
| `pool · GDO2` | async-serial stream / RSSI strobe |

### Walkie (SA868)

Pins: **SPI 14 / QSPI 18** (of 19) ⚠️

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool · UART TX` | commands + channel/power control to SA868 |
| `pool · UART RX` | status back from SA868 |

> PTT and power-band select sit on the I²C hub (slow, event-driven).

### LoRa + GPS

Pins: **SPI 16 / QSPI 20** (of 19) ❌

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → LoRa SX1262 (cap) + microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → LoRa cap, SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool · BUSY` | SX1262 busy line — wait before each SPI transfer |
| `pool · DIO1` | RX-done / TX-done interrupt (or polled) |
| `pool · GPS-TX` | NMEA stream in from the GNSS |
| `pool · GPS-RX` | config out to the GNSS |

### Listen HF/FM (Si4732)

Pins: **SPI 12 / QSPI 16** (of 19)

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool` | — |

> Si4732 is controlled over I²C and outputs analog audio — no SPI or pool pins.

### Keys (RFID2)

Pins: **SPI 12 / QSPI 16** (of 19)

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool` | — |

> RFID2 is an I²C Grove unit — no dedicated pins.

### IR remotes

Pins: **SPI 14 / QSPI 18** (of 19) ⚠️

| Pin | Role in this mode |
|---|---|
| `SPI SCK/MOSI/MISO` (3) | SPI bus → microSD |
| `74HC138 A/B/C` (3) | chip-select decoder → SD |
| `I²C SDA/SCL` (2) | sensors · RTC · RFID · buttons (via hub) |
| `Encoder A/B` (2) | menu navigation |
| `WS2812` (1) | per-antenna status LEDs |
| `Display` (SPI +1 / QSPI +5) | draw this mode's UI |
| `pool · IR-TX` | 38 kHz carrier out (RMT) to the IR LED |
| `pool · IR-RX` | demodulated edges in from the IR receiver |

---
*An interactive version (click a mode) is available in chat; GitHub renders the static tables above.*
*Part of [Leshy2](../README.md) · MIT.*
