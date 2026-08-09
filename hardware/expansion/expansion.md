# Leshy2 — Expansion sheet (Sheet 5)

*Read this in: **English** · [Русский](expansion.ru.md)*

The I²C bus and everything on it: the onboard **u-blox GPS**, the single **Grove I²C port** for M5 units (RFID2 NFC, sensors), and the consolidated **address map** of every device that shares SDA/SCL. The **PCA9555** expander lives on this bus too (drawn on [Sheet 2](../c5-buses/c5-buses.md)); Si4732 is on [Sheet 4](../audio/audio.md), the BQ25887 charger on [Sheet 1](../power/power.md). One bus, addressed by device — no second Grove port.

> ⚠️ Design stage. One set of bus pull-ups, `+3V3` signalling, `+5V` power to Grove. Confirm each unit's I²C address before committing; collisions are resolved with a mux, not more pins.

## Blocks and parts

| Ref | Part | Role | Interface |
|-----|------|------|-----------|
| U40 | **u-blox SAM-M8Q** (onboard) | GNSS with **integrated** antenna; position + time for Meshtastic | I²C (DDC) `0x42` |
| BT40 | Supercap + Schottky | GPS backup (hot-start) from `+3V3` | V_BCKP |
| J40 | **Grove HY2.0-4P** (I²C) | one plug-in port for M5 I²C units | `+5V` · GND · SDA · SCL |
| U41 (opt.) | Grove I²C hub (passive) | fan several units onto the one port | I²C |
| U42 (opt.) | **TCA9548A** mux | only if two units share an address | I²C `0x70` |
| — | RFID2 Unit (WS1850S) | example M5 unit: NFC 13.56 MHz | Grove I²C `0x28` |
| R40/R41 | 4.7 kΩ ×2 | single bus pull-ups (SDA/SCL to `+3V3`) | — |
| D40 | ESD array | protect the Grove connector | — |

## I²C address map

| Address | Device | Sheet |
|:--:|------|:--:|
| `0x11` / `0x63` | Si4732 receiver | 4 |
| `0x20` | PCA9555 slow-line expander | 2 |
| `0x28` | RFID2 NFC (Grove) | 5 |
| `0x42` | u-blox SAM-M8Q GPS | 5 |
| `0x6A` | BQ25887 charger | 1 |
| `0x70` | TCA9548A mux (only if used) | 5 |
| — | other Grove units | plug-in |

Everything shares SDA (GPIO0) / SCL (GPIO1) with **one** pair of 4.7 kΩ pull-ups for the whole bus — not per device.

## u-blox GPS — onboard, always available

The **SAM-M8Q** carries its own **integrated antenna**, so it solders straight to the board and needs only `+3V3`, the two I²C lines, and a **backup supply** (a supercap + Schottky from `+3V3`) on `V_BCKP` so ephemeris survives a power blip for a fast hot-start. It speaks I²C (DDC) with NMEA at up to 400 kbps, which is why it rides the existing bus for **0 extra GPIO**. The 1 PPS timepulse is left unconnected (no spare pin; NMEA time is enough). Being onboard means position is always there and the Grove port stays free for other units.

## Grove I²C port — the one expansion socket

A single **Grove HY2.0-4P** brings out `+5V`, GND, and the `+3V3` I²C pair with an ESD array. It accepts M5 **I²C** units — RFID2 NFC, RTC, IMU/compass, environmental sensors — each at its own address. To plug several at once, a passive **Grove I²C hub** fans the one port out; only if two units clash on an address does a **TCA9548A** mux (U42) become necessary. A second, independent Grove port was deliberately dropped — it would cost 2 GPIO the budget can't spare, and every unit we use is I²C anyway.

## Gotchas

- **Power is 5 V, signals are 3.3 V.** Grove carries `+5V` for units that need it, but SDA/SCL stay at `+3V3` (the C5 is not 5 V-tolerant). Do not let a 5 V unit pull the I²C lines to 5 V.
- **One set of pull-ups.** Adding a unit that also pulls up SDA/SCL over-loads the bus; prefer units with no pull-ups, or account for the parallel value.
- **Address collisions → mux, not pins.** Two 0x28 units (say two RFID2) need the TCA9548A; there is no pin budget for a second bus.
- **DAC-output units do not work** — the C5 has no DAC; nothing on Grove can restore that.
- **Hot-plug with care.** The Grove port is not hot-swap-rated; power down before plugging a unit, or add series resistors on SDA/SCL to survive it.

---

*Next sheet: (6) indicators/IO (TX-live LEDs, WS2812, buzzer, IR, microSD, encoder). Previous: (4) [audio](../audio/audio.md).*
*Part of [Leshy2](../../README.md) · MIT.*
