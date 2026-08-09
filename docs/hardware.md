# Leshy2 — Hardware

*Read this in: **English** · [Русский](hardware.ru.md)*

A detailed hardware reference for **Leshy2** — an open-source portable multiband RF handheld (a "field tool"). It is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), which is a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). The whole design moves to a single **ESP32-C5** brain (native Wi-Fi 2.4 **and** 5 GHz + BLE) with a lot more radio around it.

> 📌 **Design stage. No hardware exists yet.** Architecture is locked (2026-08-08); the next step is the KiCad schematic. Pin maps and exact values land once verified on real hardware. All onboard RF sits on shielded u.FL modules to de-risk the first PCB spin. The board is 4-layer (JLCPCB JLC7628), designed in KiCad; antennas are tuned by hand with a VNA.

## Bill of materials

Grouped by subsystem. **Prices are approximate** and not pinned at the design stage (shown as `—`); the two ballpark figures are the onboard LoRa module (~7 USD) and the I²C GPS module (~14 USD). The whole-build target BOM is about **115–150 USD**.

| Subsystem | Part | Role | Interface | Approx price (USD) |
|-----------|------|------|-----------|:--:|
| Brain | ESP32-C5 | Single RISC-V MCU; native Wi-Fi 2.4 + 5 GHz + BLE; runs all firmware. The **only** ESP32 with native 5 GHz. 5 GHz is Marauder-class (scan, deauth, beacon/probe flood, sniff mgmt frames) | native radios | — |
| 2.4 GHz raw | 3× nRF24L01+PA/LNA | Parallel whole-band scan, mousejack, channel analyzer | SPI | — |
| Sub-GHz | CC1101 | 300–928 MHz OOK/FSK: capture/replay remotes & sensors, RSSI activity "geiger" | SPI | — |
| Long-range mesh | SX1262 module (E22-900M class), **onboard** | Meshtastic text mesh 868/915 MHz, +22 dBm | SPI (own CS via 74HC138) + BUSY/DIO1 | ~7 |
| HF / CB / FM receiver | Si4732 | Receive-only: CB 27 MHz, full HF/shortwave, MW/LW (AM/SSB/CW), FM broadcast 64–108 MHz; analog line-out | I2C (control) | — |
| UHF voice | SA868-U | 433/446 MHz NBFM voice walkie, RX + TX up to 2 W, PTT (drop-in upgrade over SA818 1 W) | UART + PTT | — |
| Positioning | u-blox GPS (SAM-M8Q class) | GNSS with integrated ceramic antenna; rides the I²C bus (DDC/NMEA) — no UART needed | I2C (0x42) | ~14 |
| Audio | PAM8302 + small speaker | Class-D amplifier; drives the speaker from the analog line-out | analog | — |
| Display | IPS TFT (ST7796; ILI9488 alt) | 3.5″ 320×480 color; SPI, shares the radio bus (CS via 138, one DC line); PSRAM-equipped C5 holds the framebuffer | SPI | — |
| I/O expander | PCA9555 | 16 slow control lines over I²C (resets, PTT, power-downs, encoder button, charger INT/CE/QON) — 0 host GPIO | I2C | — |
| Storage | microSD | PCAP logging, profiles | SPI | — |
| IR | IR TX/RX | Clone/replay remotes | GPIO | — |
| CS decode | 74HC138 | 3-to-8 decoder: 3 GPIO become 8 chip-selects (SD, CC1101, 3× nRF24, LoRa, display) | GPIO (3) | — |
| Indicators | WS2812 RGB LED | General device / status indicator | GPIO (1-wire) | — |
| Indicators | TX-live LEDs (amber) | Hardware envelope detector — honest "on air" per transmit chain, **0 GPIO** | hardware (analog) | — |
| Alerts | Buzzer | Audible alerts / proximity "geiger" | GPIO | — |
| Input | Rotary encoder + buttons | Navigation and input (no onboard keyboard) | GPIO | — |
| Expansion | 1× Grove HY2.0-4P (I²C) | One expansion port for M5 I²C Units; several at once via a Grove I²C hub | I2C | — |
| Grove unit (opt.) | RFID2 Unit (WS1850S) | NFC 13.56 MHz, MIFARE / NTAG | I2C (0x28) | — |
| Grove unit (opt.) | RTC | Timestamp for PCAP logs | I2C | — |
| Grove unit (opt.) | IMU + compass | Direction finding | I2C | — |
| Power | 2× 18650 (2S) | Battery pack, ~7.4 V, ~18 Wh | power | — |
| Power | BQ25xxx | 2S battery charger | power | — |
| Power | CH224K | USB-C PD sink | power | — |
| Power | Buck 5 V/3 A + LDO 3.3 V + power-path | Rails; runs while charging | power | — |

## Antennas

Leshy2 has **8 onboard antennas**, one per RF chain. There is **no RF switch shared between chains**, so every chain keeps its own separate antenna — no folding of different chains onto one connector. The GPS module carries its **own** integrated antenna, separate from these eight.

**Onboard (8):**

1. **ESP32-C5** — 2.4 / 5 GHz dual-band Wi-Fi + BLE (one dual-band antenna; the C5 has a single RF port and uses one band at a time).
2. **nRF24 #1** — 2.4 GHz.
3. **nRF24 #2** — 2.4 GHz.
4. **nRF24 #3** — 2.4 GHz.
5. **CC1101** — sub-GHz 300–928 MHz. (An optional RF switch, the idea borrowed from the M5 Cap CC1101, can fold *the CC1101's own* bands into a single SMA — this is within one chain, not shared across chains.)
6. **Si4732** — large telescopic whip for HF / CB (receive only).
7. **SA868-U** — 433 / 446 MHz UHF.
8. **SX1262 (LoRa)** — 868 / 915 MHz, onboard.

**GPS:** the u-blox module's **integrated ceramic antenna** — on the module itself, over the I²C Grove connector.

**Placement:** the eight antennas go **on top**; expander connectors sit on the sides or the back.

**Si4732 HF input protection:** a passive **ESD/clamp** (optionally a back-to-back diode limiter) on the HF input. There is **no manual disconnect switch** — de-sense from our own transmitters is avoided by mode-exclusive operation (Si4732 is not listening while another radio transmits), and the antenna is removed by unscrewing its SMA.

**The 27 MHz antenna is large.** A quarter-wave at 27 MHz is about **2.75 m**, so a full-size whip is impractical on a handheld. The plan is a **telescopic 1–1.7 m whip**, or a **shortened / loaded whip**.

## Per-antenna indicators

Every **transmit** chain gets **one hardware TX-live LED** so you can see at a glance which antenna is actually radiating:

- **TX — amber (hardware envelope detector).** An **honest "on air" light**: it fires from the real RF emission, so it lights **even if the firmware hangs**. It is **not driven by software** and costs **0 GPIO**. Kept deliberately dim.

There is **no per-antenna RX LED** — a detector on a receive input would degrade its sensitivity, and the display already shows the active chain. Receive-only chains (Si4732) therefore have no LED at all. Overall device state is shown by the single general **WS2812** status LED and on the display.

| Chain | TX-live LED (amber) |
|-------|:--:|
| ESP32-C5 (Wi-Fi/BLE) | ✓ |
| nRF24 #1 | ✓ |
| nRF24 #2 | ✓ |
| nRF24 #3 | ✓ |
| CC1101 (sub-GHz) | ✓ |
| SA868-U (UHF voice) | ✓ |
| SX1262 (LoRa) | ✓ |
| Si4732 (HF/CB/FM, RX only) | — |

## Buses

The digital peripherals share the buses off the ESP32-C5. Because the C5 is a 3.3 V part, no level shifter is needed on the 3.3 V signals.

**SPI** — microSD, the 3× nRF24, the CC1101, the onboard SX1262 (LoRa), and the **ST7796 display**. Each device's chip-select is generated by a **74HC138** decoder (3 GPIO → 8 CS lines) instead of one GPIO each; the display adds one **DC** line. Because only one radio is active at a time, the display and a radio never contend for the bus. A PSRAM-equipped C5 holds the framebuffer (320×480×2 ≈ 300 KB).

**I2C** — the Si4732 control interface, the **u-blox GPS** (0x42), the **PCA9555 I/O expander** (slow control lines, see below), and the Grove port: RFID2 NFC (0x28), RTC, IMU / compass, and future units, addressed individually. Several units at once plug into a **Grove I²C hub** on the single port.

**UART** — the SA868-U (control). The SA868's **PTT** rides the PCA9555 expander. (GPS no longer uses a UART — it is on I²C.)

**GPIO (direct)** — IR TX/RX, the WS2812 status LED, encoder A/B, the CC1101 GDO0, the nRF24 CE, the LoRa BUSY line, the display DC, and the 74HC138 address lines. Slow control lines (encoder button, SA868 PTT / PD, Si4732 RST, LoRa NRESET, charger INT/CE/QON, buzzer) sit on the **PCA9555** over I²C, for 0 host GPIO; LoRa DIO1 is polled over SPI. See [pin-budget.md](pin-budget.md).

## Expansion

Leshy2 is **M5-compatible** for **M5 Grove I²C Units**. M5 **Caps** (Cardputer EXT bus), **Modules** (the M5Bus 16-pin stack) and **StickC HATs** use different connectors and are **not supported**. Two hard limits on the port: it is **I²C only**, and **DAC-output units do not work** because the C5 has no DAC.

### Onboard LoRa (SX1262)

Meshtastic long-range mesh is a **raw SX1262 module on the board** (E22-900M class, u.FL): the shared SPI bus, its **own CS via the 74HC138**, and two control lines — **BUSY** and **DIO1**. Being on the board, the mesh is always available, at the cost of one permanent antenna in the top array. GPS is kept off this chain and put on I²C (below) so it costs no extra GPIO; see [pin-budget.md](pin-budget.md).

### GPS (u-blox, I²C)

Position comes from a small **u-blox GPS** (SAM-M8Q class) on the Grove **I²C** bus, with its own integrated antenna. Speaking I²C (DDC/NMEA) instead of UART lets it ride the existing bus for **0 extra GPIO** — one of the moves that keeps the tight pin budget in range (see [pin-budget.md](pin-budget.md)).

### Grove port (1× I²C)

One **Grove HY2.0-4P** port, wired as the **I²C** bus (5 V power, 3.3 V signals). It hosts the u-blox GPS plus any M5 I²C Units — RFID2 NFC, RTC, IMU / compass, sensors — addressed individually, with a **Grove I²C hub** when several are plugged at once. A second, independent Grove port was dropped: it would cost 2 more GPIO the tight budget can't spare, and all our expansion is I²C anyway.

**Units reachable over Grove:**

- **NFC:** RFID2 Unit (WS1850S, 13.56 MHz, MIFARE / NTAG, I2C address 0x28).
- **RTC:** timestamps for PCAP logs.
- **IMU + compass:** direction finding.

## Audio path

Audio is **fully analog** and the MCU is **not in the path**:

```
Si4732 / SA868-U  →  line-out (analog)  →  PAM8302 class-D amp  →  small speaker
```

The Si4732 and the SA868-U produce real analog voice/audio on a line-out, which feeds a **PAM8302** class-D amplifier driving a small speaker. The ESP32-C5 has **no analog DAC**, so any MCU-generated sound could only come out over **I2S** — it is deliberately kept out of the receive audio chain.

## Power

Leshy2 runs on **2× 18650 cells in 2S** (about **7.4 V**, about **18 Wh**) with its **own PMIC**:

- **BQ25xxx** battery charger
- **USB-C PD** sink (**CH224K**)
- **Power-path**, so the device works while charging
- **Buck converter 5 V / 3 A** + **LDO 3.3 V** for the rails

**Why a custom PMIC:** off-the-shelf **M5 single-cell modules do not fit** — the design needs 2S and a PD sink. The **IP5306 was rejected** (weak boost, and it auto-shuts-down under a low load).

**nRF24 brownout fix:** the PA/LNA modules draw pulsed current, so each module gets **100–220 µF bulk + 100 nF at its VCC** to stop the supply from browning out.

**Runtime (approximate):**

| Use | Runtime |
|-----|--------|
| Light | ~9 h |
| Active | ~3.6 h |
| TX peaks | ~2.5 h |

---

*License: [MIT](../LICENSE), same as upstream ESP32-DIV. Copyright © Anton Vinogradov ([anton-vinogradov](https://github.com/anton-vinogradov)).*
