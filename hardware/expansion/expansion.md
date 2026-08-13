# Leshy2 — Expansion + GPS sheet (Sheet 5)

*Read this in: **English** · [Русский](expansion.ru.md)*

Two pieces of "everything else": the onboard **u-blox GPS** on its own **UART**, and the **I²C bus** with its **address map** plus the **two Grove I²C ports** for plug-in M5/Grove units (RFID2 NFC, sensors). Both hang off the **S3** (main brain). GPS runs over UART on purpose — it keeps NMEA streaming off I²C so the shared bus stays light. The three **PCA9555** expanders ride this same I²C bus (drawn on [Sheet 2](../c5-buses/c5-buses.md)); Si4732 is on [Sheet 4](../audio/audio.md), the BQ25887 charger on [Sheet 1](../power/power.md).

> ⚠️ Design stage. One pair of bus pull-ups for the whole I²C bus, `+3V3` signalling, `+3V3` power to Grove by default. Confirm each unit's I²C address before committing; collisions are resolved with a mux, not more pins.

## Blocks and parts

| Ref | Part | Role | Interface |
|-----|------|------|-----------|
| U40 | **u-blox SAM-M8Q** (onboard) | GNSS with its **own patch antenna**; position + time for Meshtastic | **UART** (NMEA) |
| BT40 | Supercap + Schottky | GPS backup (hot-start) on `V_BCKP` from `+3V3` | V_BCKP |
| J40 / J41 | **Grove HY2.0-4P** (I²C) ×2 | two plug-in ports for M5 I²C units | `+3V3` · GND · SDA · SCL (5 V via jumper) |
| U41 (opt.) | Grove I²C hub (passive) | fan several units onto one port | I²C |
| U42 (opt.) | **TCA9548A** mux | only if two units share an address | I²C `0x70` |
| — | RFID2 Unit (WS1850S) | example M5 unit: NFC 13.56 MHz | Grove I²C `0x28` |
| R40/R41 | 4.7 kΩ ×2 | single bus pull-ups (SDA/SCL to `+3V3`) | — |
| D40/D41 | ESD array ×2 | protect each Grove connector | — |
| U43 (opt.) | PCA9306 / TCA9517 | I²C level translator for a 5 V Grove unit | I²C |

## Key nets

```
GPS (U40, onboard)
  UART2   : S3 GPIO18 ← U40.TXD (GPS_UART_RX, NMEA, required)
            S3 GPIO47 → U40.RXD (GPS_UART_TX, optional, config only)
  power   : VCC = +3V3 ; V_BCKP ← supercap + Schottky (BT40) for hot-start
  antenna : own GNSS patch antenna (integrated in SAM-M8Q)
  1PPS    : timepulse left unconnected (no spare pin; NMEA time is enough)

I²C bus (shared, S3 host)
  lines   : SDA = GPIO4 · SCL = GPIO5 ; one pair of 4.7 kΩ pull-ups → +3V3 (R40/R41)
  onboard : Si4732 0x11 · PCA9555 #1 0x20 · PCA9555 #2 0x21 · PCA9555 #3 0x22 · touch ~0x38 · BQ25887 0x6A
  Grove   : J40 + J41 → SDA/SCL/GND/+3V3 + ESD (D40/D41)
  opt     : TCA9548A 0x70 only for address collisions ; PCA9306 for a 5 V unit
```

## I²C address map

| Address | Device | Sheet |
|:--:|------|:--:|
| `0x11` | Si4732 receiver (SEN = GND) | 4 |
| `0x20` | PCA9555 #1 slow-line expander | 2 |
| `0x21` | PCA9555 #2 slow-line expander | 2 |
| `0x22` | PCA9555 #3 (UI buttons) | 2 |
| `0x28` | RFID2 NFC (Grove) | 5 |
| `0x6A` | BQ25887 charger | 1 |
| `0x70` | TCA9548A mux (only if used) | 5 |
| — | other Grove units | plug-in |

Everything shares SDA (GPIO4) / SCL (GPIO5) with **one** pair of 4.7 kΩ pull-ups for the whole bus — not per device. **GPS is not here** — it moved to UART, which frees the bus of the constant NMEA traffic.

## u-blox GPS — onboard, over UART

The **SAM-M8Q** carries its **own patch antenna**, so it solders straight to the board and needs only `+3V3`, one UART line in, an optional line out, and a **backup supply** (a supercap + Schottky from `+3V3`) on `V_BCKP` so ephemeris survives a power blip for a fast hot-start. It **pushes NMEA** out of the box on power-up — the S3 only has to read `GPS_UART_RX` (GPIO18); the return line `GPS_UART_TX` (GPIO47) is optional, used only to send configuration (fix rate, message set). Running it on **UART2 rather than I²C** deliberately keeps the continuous NMEA stream off the shared I²C bus. The 1 PPS timepulse is left unconnected (no spare pin; NMEA time is enough). Being onboard means position is always there, and both Grove ports stay free for other units.

## Grove I²C ports — two expansion sockets

**Two** identical **Grove HY2.0-4P** connectors (J40, J41) each bring out **`+3V3`**, GND and the I²C pair with an ESD array — the S3 is not 5 V-tolerant, so the ports are 3.3 V by default (most M5/Grove I²C units run at 3.3 V). A `+5V` supply is a separate jumper option, and only behind a bidirectional I²C translator (PCA9306 / TCA9517, U43) so a 5 V unit can never pull SDA/SCL above 3.3 V. Both ports sit on the **same** I²C bus — the second one is a convenience socket, not a second bus, so it costs no extra GPIO. They accept M5 **I²C** units — RFID2 NFC, RTC, IMU/compass, environmental sensors — each at its own address. To plug several onto one connector, a passive **Grove I²C hub** (U41) fans it out; only if two units clash on an address does a **TCA9548A** mux (U42) become necessary.

## Fab realization (real parts)

`hardware/tscircuit/expansion.tsx` is fab-drafted (engine-pulled LCSC footprints);
KiCad DRC = **0 unconnected / 0 shorts / 0 schematic-parity**.

| Ref | Part | LCSC |
|-----|------|------|
| U40 | u-blox SAM-M8Q GNSS | C5447387 |
| J40/J41 | Grove HY2.0-4P | C722729 |
| D40/D41 | PESD5V0S2UAT ESD | C552572 |
| D42 | BAT54 Schottky | C466635 |
| BT40 | 0.22 F supercap | C3019760 |

Correction found by realizing against the real module: the SAM-M8Q has a **separate `VCC_IO`
supply pad** the logical placeholder lacked — tied to +3V3, plus the datasheet GPS decoupling
(100 nF + 10 µF + VCC_IO 100 nF). The DDC (`SDA`/`SCL`) pins are left open on purpose (UART-only,
to keep NMEA off the shared I2C bus).
Before fab: confirm the Grove pin-1 orientation / signal order against the plugged unit; the
Grove "5 V" pin carries **+3V3** (the S3 is not 5 V-tolerant — a 5 V unit needs a level
translator); the RFID2 (`U44`) is an external plug-in unit, not a populated part.

## Gotchas

- **3.3 V ports by default.** SDA/SCL are `+3V3` (the S3 is not 5 V-tolerant). Grove power is `+3V3`; a `+5V` unit needs the jumper **and** the I²C translator (U43) so it can't pull the lines above 3.3 V.
- **One set of pull-ups for the whole bus.** Both Grove ports and every onboard device share the single R40/R41 pair. A unit that also pulls up SDA/SCL over-loads the bus; prefer units with no pull-ups, or account for the parallel value.
- **Address collisions → mux, not pins.** Two `0x28` units (say two RFID2) need the TCA9548A; there is no pin budget for a second bus. **Each used TCA9548A downstream channel needs its own pull-up pair** — the mux's FET switches isolate the channels, so the single bus pull-ups don't reach them.
- **GPS wants a clear sky and a good backup cap.** Without `V_BCKP` held up, every start is a cold start (30–60 s); the supercap + Schottky buy a hot-start across a power blip.
- **DAC-output Grove units do not work** — the S3 has no DAC; nothing on Grove can restore that.
- **Hot-plug with care.** The Grove ports are not hot-swap-rated; power down before plugging a unit, or add series resistors on SDA/SCL to survive it.

---

*Next sheet: (6) indicators/IO (TX-live LEDs, WS2812, buzzer, IR, microSD, encoder). Previous: (4) [audio](../audio/audio.md).*
*Part of [Leshy2](../../README.md) · MIT.*
