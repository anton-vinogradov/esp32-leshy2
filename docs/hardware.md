# Leshy2 — Hardware

*Read this in: **English** · [Русский](hardware.ru.md)*

A detailed hardware reference for **Leshy2** — an open-source portable multiband RF handheld (a "field tool"). It is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), which is a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). The whole design moves to a single **ESP32-C5** brain (native Wi-Fi 2.4 **and** 5 GHz + BLE) with a lot more radio around it.

> 📌 **Design stage. No hardware exists yet.** Architecture is locked (2026-08-08); the next step is the KiCad schematic. Pin maps and exact values land once verified on real hardware. All onboard RF sits on shielded u.FL modules to de-risk the first PCB spin. The board is 4-layer (JLCPCB JLC7628), designed in KiCad; antennas are tuned by hand with a VNA.

## Bill of materials

Grouped by subsystem. **Prices are approximate.** The source spec only fixes the plug-in cap price (~14.50 USD) and a whole-build target BOM of about **115–150 USD**; individual part prices are not pinned at the design stage, so they are shown as `—`.

| Subsystem | Part | Role | Interface | Approx price (USD) |
|-----------|------|------|-----------|:--:|
| Brain | ESP32-C5 | Single RISC-V MCU; native Wi-Fi 2.4 + 5 GHz + BLE; runs all firmware. 5 GHz is Marauder-class (scan, deauth, beacon/probe flood, sniff mgmt frames) | native radios | — |
| 2.4 GHz raw | 3× nRF24L01+PA/LNA | Parallel whole-band scan, mousejack, channel analyzer | SPI | — |
| Sub-GHz | CC1101 | 300–928 MHz OOK/FSK: capture/replay remotes & sensors, RSSI activity "geiger" | SPI | — |
| HF / CB / FM receiver | Si4732 | Receive-only: CB 27 MHz, full HF/shortwave, MW/LW (AM/SSB/CW), FM broadcast 64–108 MHz; analog line-out | I2C (control) | — |
| UHF voice | SA868-U | 433/446 MHz NBFM voice walkie, RX + TX up to 2 W, PTT (drop-in upgrade over SA818 1 W) | UART + PTT | — |
| Audio | PAM8302 + small speaker | Class-D amplifier; drives the speaker from the analog line-out | analog | — |
| Display | ST7789 / ILI9341 TFT | Direct SPI TFT — fast enough for a real waterfall/spectrum | SPI | — |
| Storage | microSD | PCAP logging, profiles | SPI | — |
| IR | IR TX/RX | Clone/replay remotes | GPIO | — |
| Indicators | WS2812 RGB LEDs | Status + per-antenna RX (blue) indicators | GPIO (1-wire) | — |
| Indicators | TX-live LEDs (amber) | Hardware envelope detector — honest "on air" per transmit chain | hardware (analog) | — |
| Alerts | Buzzer | Audible alerts / proximity "geiger" | GPIO | — |
| Input | Buttons + rotary encoder | Navigation and input (no onboard keyboard) | GPIO | — |
| Expansion | Cap slot (Cardputer ADV EXT 2.54-14P) | 1:1 replica bus for one M5 cap | SPI + I2C + UART | — |
| Expansion | 2× Grove HY2.0-4P | Universal expansion ports (Units) | I2C / UART / GPIO / ADC | — |
| Expansion | PCA9548 | I2C mux on Grove Port 1 (no address clashes) | I2C | — |
| Plug-in cap | M5 Cap LoRa-1262 | SX1262 +22 dBm (Meshtastic) + ATGM336H/AT6668 GNSS with internal ceramic antenna — mesh **and** GPS in one cap | SPI (shares SD bus, own CS) + GNSS | ~14.50 (approx) |
| Grove unit (opt.) | RFID2 Unit (WS1850S) | NFC 13.56 MHz, MIFARE / NTAG | I2C (0x28) | — |
| Grove unit (opt.) | RTC | Timestamp for PCAP logs | I2C | — |
| Grove unit (opt.) | IMU + compass | Direction finding | I2C | — |
| Power | 2× 18650 (2S) | Battery pack, ~7.4 V, ~18 Wh | power | — |
| Power | BQ25xxx | 2S battery charger | power | — |
| Power | CH224K | USB-C PD sink | power | — |
| Power | Buck 5 V/3 A + LDO 3.3 V + power-path | Rails; runs while charging | power | — |

## Antennas

Leshy2 has **7 onboard antennas**, one per RF chain, plus the plug-in cap's own antennas. There is **no RF switch shared between chains**, so every chain keeps its own separate antenna — no folding of different chains onto one connector.

**Onboard (7):**

1. **ESP32-C5** — 2.4 / 5 GHz dual-band Wi-Fi + BLE.
2. **nRF24 #1** — 2.4 GHz.
3. **nRF24 #2** — 2.4 GHz.
4. **nRF24 #3** — 2.4 GHz.
5. **CC1101** — sub-GHz 300–928 MHz. (An optional RF switch, the idea borrowed from the M5 Cap CC1101, can fold *the CC1101's own* bands into a single SMA — this is within one chain, not shared across chains.)
6. **Si4732** — large telescopic whip for HF / CB (receive only).
7. **SA868-U** — 433 / 446 MHz UHF.

**On the plug-in cap:**

- **LoRa RP-SMA** for the SX1262.
- **Internal GPS ceramic** antenna for the GNSS (inside the cap).

**Placement:** antennas go **on top**; expander connectors sit on the sides or the back.

**Si4732 HF input protection:** the HF input has a **disconnect + ground switch** and **ESD protection**, so the front-end can be safely isolated and grounded.

**The 27 MHz antenna is large.** A quarter-wave at 27 MHz is about **2.75 m**, so a full-size whip is impractical on a handheld. The plan is a **telescopic 1–1.7 m whip**, or a **shortened / loaded whip**.

## Per-antenna indicators

Every antenna gets **two LEDs**, so you can see at a glance which chain is receiving and which is actually radiating:

- **RX — blue (WS2812, firmware-driven).** The MCU knows which chain is active and lights the blue LED for it.
- **TX — amber (hardware envelope detector).** This is an **honest "on air" light**: it fires from the real RF emission, so it lights **even if the firmware hangs**. It is not driven by software.

**Receive-only chains have no TX LED.** The Si4732 chain (HF / CB / FM, receive only) gets a blue RX LED but no amber TX LED.

| Chain | RX LED (blue) | TX LED (amber) |
|-------|:--:|:--:|
| ESP32-C5 (Wi-Fi/BLE) | ✓ | ✓ |
| nRF24 #1 | ✓ | ✓ |
| nRF24 #2 | ✓ | ✓ |
| nRF24 #3 | ✓ | ✓ |
| CC1101 (sub-GHz) | ✓ | ✓ |
| Si4732 (HF/CB/FM, RX only) | ✓ | — |
| SA868-U (UHF voice) | ✓ | ✓ |

## Buses

The digital peripherals share three buses off the ESP32-C5. Because the C5 is a 3.3 V part, no level shifter is needed on the 3.3 V signals.

**SPI** — TFT display, microSD, the 3× nRF24, the CC1101, and the plug-in cap's SX1262. Each device has its own chip-select (CS). The **cap's SPI shares the onboard microSD SPI bus** (the same trick the Cardputer uses), on a **separate CS**.

**I2C** — the Si4732 control interface, the PCA9548 mux on Grove Port 1, and the I2C Grove units behind the mux (RFID2 NFC at 0x28, RTC, IMU / compass). Grove Port 2 can also carry I2C.

**UART** — the SA868-U (control), the cap's UART pins, and the cap's GNSS. Grove Port 2 can also carry UART. The SA868's **PTT** is a separate GPIO line.

**GPIO** — IR TX/RX, WS2812 LEDs, buzzer, buttons and the rotary encoder, the SA868 PTT, the cap's RESET / INT / BUSY lines, and Grove Port 2 when used for GPIO / ADC.

## Expansion

Leshy2 is **M5-compatible**, but only for **M5 Units and Caps**. M5 **Modules** (the M5Bus 16-pin stack) and **StickC HATs** use different connectors and are **not supported**. One hard limit on any port: **DAC-output units do not work**, because the C5 has no DAC.

### Cap slot — Cardputer ADV EXT-14P replica

The single cap slot is a **faithful 1:1 replica of the Cardputer ADV EXT 2.54-14P bus** — a 100% electrical and connector copy. "Full support" for a cap means this replica bus plus a firmware driver written for that cap.

Pinout (2.54 mm, 14 pins):

| Pin | Signal | Pin | Signal |
|:--:|--------|:--:|--------|
| P1 | RESET | P2 | 5V_IN |
| P3 | INT | P4 | GND |
| P5 | BUSY | P6 | 5V_OUT |
| P7 | SPI_SCK | P8 | I2C_SDA |
| P9 | SPI_MOSI | P10 | I2C_SCL |
| P11 | SPI_MISO | P12 | UART_RX |
| P13 | SPI_CS | P14 | UART_TX |

**Reference cap: M5 Cap LoRa-1262** (~14.50 USD). It carries an **SX1262** (+22 dBm, for Meshtastic) **and** an **ATGM336H / AT6668 GNSS** with an internal ceramic antenna — so one cap gives both **Meshtastic and GPS**. Its SPI shares the onboard microSD SPI bus on a separate CS, exactly as the pinout above allows.

### Grove ports (2×)

Two **Grove HY2.0-4P** ports, made as universal as possible. Both provide **5 V power** and **3.3 V signals**.

- **Port 1 — I2C bus behind a PCA9548 mux.** The mux hosts the I2C units (RFID2 NFC, RTC, IMU / compass, and future I2C units) with **no address clashes**.
- **Port 2 — flexible I2C / UART / GPIO / ADC.** It accepts M5 Unit types **A / B / C**.

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
