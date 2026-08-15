# Leshy2 — Expansion sheet (Sheet 5)

*Read this in: **English** · [Русский](expansion.ru.md)*

Two pieces of "everything else": the **Grove-UART GPS port** (S3 UART2 broken out for an external M5 GPS Unit), and the **I²C bus** with its **address map** plus the **two Grove I²C ports** for plug-in M5/Grove units (RFID2 NFC, sensors). Both hang off the **S3** (main brain). GPS runs over UART on purpose — it keeps NMEA streaming off I²C so the shared bus stays light. The three **PCA9555** expanders ride this same I²C bus (drawn on [Sheet 2](../c5-buses/c5-buses.md)); Si4732 is on [Sheet 4](../audio/audio.md), the BQ25887 charger on [Sheet 1](../power/power.md).

> ♻️ **On-board GPS removed.** Earlier drafts soldered a u-blox **SAM-M8Q** (U40) with its own patch antenna and a backup supercap (BT40) onto the board. That is **gone** — GPS is now an **external M5 GPS Unit** (UART) that plugs into a **Grove-UART** port and carries its own antenna. The S3's freed **UART2** (GPIO18 = RX, GPIO47 = TX) is broken out to that Grove-UART header. The two I²C Grove ports are unchanged. The U40 / BT40 / GPS-decoupling rows below are **superseded** — kept for history until the two-board re-netlist drops them from the `.tsx`.

> ⚠️ Design stage. One pair of bus pull-ups for the whole I²C bus, `+3V3` signalling, `+3V3` power to Grove by default. Confirm each unit's I²C address before committing; collisions are resolved with a mux, not more pins.

## Blocks and parts

| Ref | Part | Role | Interface |
|-----|------|------|-----------|
| U40 | ~~u-blox SAM-M8Q (onboard)~~ | **removed — external M5 GPS Unit** on the Grove-UART port instead | — |
| BT40 | ~~Supercap + Schottky~~ | **removed** — the external M5 GPS Unit carries its own backup | — |
| J_GPS | **Grove HY2.0-4P** (UART) | Grove-UART port for the external M5 GPS Unit (S3 UART2) | `+3V3` · GND · RX · TX |
| J40 / J41 | **Grove HY2.0-4P** (I²C) ×2 | two plug-in ports for M5 I²C units | `+3V3` · GND · SDA · SCL (5 V via jumper) |
| U41 (opt.) | Grove I²C hub (passive) | fan several units onto one port | I²C |
| U42 (opt.) | **TCA9548A** mux | only if two units share an address | I²C `0x70` |
| — | RFID2 Unit (WS1850S) | example M5 unit: NFC 13.56 MHz | Grove I²C `0x28` |
| R40/R41 | 4.7 kΩ ×2 | single bus pull-ups (SDA/SCL to `+3V3`) | — |
| D40/D41 | ESD array ×2 | protect each Grove connector | — |
| U43 (opt.) | PCA9306 / TCA9517 | I²C level translator for a 5 V Grove unit | I²C |

## Key nets

```
GPS (external M5 GPS Unit on the Grove-UART port J_GPS — on-board U40 removed)
  UART2   : S3 GPIO18 ← J_GPS RX (GPS_UART_RX, NMEA, required)
            S3 GPIO47 → J_GPS TX (GPS_UART_TX, optional, config only)
  power   : Grove +3V3 · GND to the M5 GPS Unit
  antenna : external — the M5 GPS Unit carries its own antenna
  backup  : internal to the M5 GPS Unit (no on-board V_BCKP supercap)

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

Everything shares SDA (GPIO4) / SCL (GPIO5) with **one** pair of 4.7 kΩ pull-ups for the whole bus — not per device. **GPS is not here** — it lives on the separate Grove-UART port (external M5 GPS Unit), which keeps the constant NMEA traffic off this bus.

## GPS — external M5 Unit on Grove-UART

GPS is an **external M5 GPS Unit** (UART) that plugs into a **Grove-UART** port (`J_GPS`). The S3's **UART2** is broken out to that header: the S3 reads `GPS_UART_RX` (GPIO18) for the NMEA stream the unit **pushes** on power-up; the return line `GPS_UART_TX` (GPIO47) is optional, used only to send configuration (fix rate, message set). Running GPS on **UART rather than I²C** deliberately keeps the continuous NMEA stream off the shared I²C bus. The unit carries **its own antenna** and its own backup supply for hot-start, so the board needs neither a patch antenna nor a backup supercap. Both I²C Grove ports stay free for other units.

> ♻️ **Superseded — on-board GPS.** Earlier drafts put a **u-blox SAM-M8Q** (U40) on the board with its own patch antenna, a backup supercap + Schottky (BT40) on `V_BCKP`, and the datasheet GPS decoupling. All of that is **removed**. The U40 / BT40 rows in the tables above and below remain only until the two-board re-netlist drops them from the `.tsx`.

## Grove I²C ports — two expansion sockets

**Two** identical **Grove HY2.0-4P** connectors (J40, J41) each bring out **`+3V3`**, GND and the I²C pair with an ESD array — the S3 is not 5 V-tolerant, so the ports are 3.3 V by default (most M5/Grove I²C units run at 3.3 V). A `+5V` supply is a separate jumper option, and only behind a bidirectional I²C translator (PCA9306 / TCA9517, U43) so a 5 V unit can never pull SDA/SCL above 3.3 V. Both ports sit on the **same** I²C bus — the second one is a convenience socket, not a second bus, so it costs no extra GPIO. They accept M5 **I²C** units — RFID2 NFC, RTC, IMU/compass, environmental sensors — each at its own address. To plug several onto one connector, a passive **Grove I²C hub** (U41) fans it out; only if two units clash on an address does a **TCA9548A** mux (U42) become necessary.

## Fab realization (real parts)

`hardware/tscircuit/expansion.tsx` is fab-drafted (engine-pulled LCSC footprints);
KiCad DRC = **0 unconnected / 0 shorts / 0 schematic-parity**.

| Ref | Part | LCSC |
|-----|------|------|
| U40 | ~~u-blox SAM-M8Q GNSS~~ | ~~C5447387~~ — **removed (external M5 GPS); still in `.tsx` until re-netlist** |
| J_GPS · J40/J41 | Grove HY2.0-4P | C722729 |
| D40/D41 | PESD5V0S2UAT ESD | C552572 |
| D42 | ~~BAT54 Schottky~~ | ~~C466635~~ — **removed (GPS backup, external now)** |
| BT40 | ~~0.22 F supercap~~ | ~~C3019760~~ — **removed (GPS backup, external now)** |

*(Superseded — the on-board SAM-M8Q is removed; kept for history.)* A correction found while
realizing against the real module: the SAM-M8Q has a **separate `VCC_IO`
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
- **GPS is external now.** The M5 GPS Unit on the Grove-UART port carries its own antenna and its own backup, so there is no on-board `V_BCKP` supercap to hold up. A clear sky still helps the first fix; hot-start behaviour lives inside the unit.
- **DAC-output Grove units do not work** — the S3 has no DAC; nothing on Grove can restore that.
- **Hot-plug with care.** The Grove ports are not hot-swap-rated; power down before plugging a unit, or add series resistors on SDA/SCL to survive it.

---

*Next sheet: (6) indicators/IO (TX-live LEDs, WS2812, buzzer, IR, microSD, encoder). Previous: (4) [audio](../audio/audio.md).*
*Part of [Leshy2](../../README.md) · MIT.*
