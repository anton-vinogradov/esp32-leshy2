# Leshy2

*Read this in: **English** · [Русский](README.ru.md)*

**An open-source, portable, multiband RF handheld — a field tool you build yourself.**

Leshy2 is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), which is a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). The reason for a new device is simple: ESP32-DIV v2 has no 5 GHz Wi-Fi. Leshy2 fixes that by moving the whole design to a single **ESP32-C5** brain (native 2.4 **and** 5 GHz Wi-Fi + BLE) and adding a lot more radio around it. The goal is to be as capable as is reasonable at a fair price — target BOM about **115–150 USD**. It keeps the DIV-style handheld shape, just modernized. It is built in the open so people can join in.

> 🛑 **Your own gear only.** This is an educational security-research and radio tool. Use it only on networks, devices, and radios you own or are explicitly authorized in writing to test. Radio law differs by country — it is on you to check and obey it.

## 🌳 Lineage

Leshy2 stands on two projects:

- **[ESP32-DIV](https://github.com/cifertech/ESP32-DIV)** by CiferTech (MIT) — the hardware concept and the origin of the whole line.
- **[esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy)** — the firmware predecessor (our ESP32-S3 take on DIV), which Leshy2's software is ported from.

## 📌 Status

**Design-stage open project. No hardware exists yet.**

- Architecture is **locked** (2026-08-08).
- **Next step:** the KiCad schematic.
- Nothing has been built or tested on real hardware. Follow along, comment, and contribute while it takes shape.

## 🧰 What it does

Grouped by what you actually do with it. Everything is meant for your own equipment.

**Recon / attacks**
- Wi-Fi 2.4 + 5 GHz (ESP32-C5): scan, deauth, beacon/probe flood, sniff management frames — Marauder-class.
- 2.4 GHz raw (3× nRF24L01+PA/LNA): parallel whole-band scan, mousejack, channel analyzer.
- Sub-GHz (CC1101): capture and replay OOK/FSK remotes and sensors; RSSI activity "geiger".
- BLE (ESP32-C5).
- IR (TX/RX): clone and replay remotes.
- NFC (RFID2 unit over Grove): read MIFARE / NTAG.

**Listen (by voice)**
- Si4732 (receive only): CB 27 MHz, full HF / shortwave, MW / LW (AM / SSB / CW), and FM broadcast 64–108 MHz.
- SA868-U: 433 / 446 MHz NBFM voice — you can both listen and talk.
- Real analog audio: line-out → PAM8302 class-D amp → small speaker. The MCU is **not** in the audio path.

**Transmit**
- SA868-U walkie: talk on 433 / 446 MHz, RX and TX up to 2 W (PTT, UART control). TX power is region / licence limited — 446 PMR max 0.5 W ERP; 5 W only on ham 70 cm with a licence.
- Meshtastic over LoRa (SX1262 on the plug-in cap): encrypted text mesh at kilometer range (+22 dBm). Legal power caps are enforced per region in firmware.

**Spectrum view**
- Direct SPI-TFT (ST7789 / ILI9341) — fast enough for a real waterfall / spectrum.
- 2.4 GHz raw spectrum via the nRF24 chain; sub-GHz waterfall via CC1101.
- Per-antenna LEDs: blue RX (WS2812, firmware-driven) and amber TX (hardware envelope detector — honest "on air" even if firmware hangs).

**Aux (onboard)**
- microSD (SPI) for PCAP logging.
- IR TX / RX.
- WS2812 RGB + buzzer.
- Buttons + rotary encoder.
- Long text is typed on your phone over BLE (Meshtastic app) — there is no onboard keyboard.

**Expandability (M5-compatible)**
- **1× cap slot** — a faithful 1:1 replica of the Cardputer ADV EXT 2.54-14P bus. Hosts the M5 Cap LoRa-1262 (SX1262 +22 dBm + GNSS with internal ceramic antenna) for Meshtastic **and** GPS in one cap (~14.50 USD).
- **2× Grove HY2.0-4P** ports. Port 1 = I2C bus with a PCA9548 mux (RFID2 NFC + RTC + IMU / compass + future I2C units, no address clashes). Port 2 = flexible I2C / UART / GPIO / ADC.
- Supports M5 **Units** and **Caps** only. M5 Modules and StickC HATs use different connectors and are **not** supported. DAC-output units do not work (the C5 has no DAC).

## 📻 Frequency map

| Band | Chip | RX | TX | What you do |
|------|------|:--:|:--:|-------------|
| 2.4 GHz Wi-Fi + BLE | ESP32-C5 | ✓ | ✓ | scan, deauth, beacon/probe flood, sniff mgmt frames |
| 5 GHz Wi-Fi | ESP32-C5 | ✓ | ✓ | same Marauder-class tools on 5 GHz |
| 2.4 GHz raw | 3× nRF24L01+ | ✓ | ✓ | parallel whole-band scan, mousejack, channel analyzer |
| 300–928 MHz | CC1101 | ✓ | ✓ | capture / replay OOK / FSK remotes & sensors, RSSI "geiger" |
| 433 / 446 MHz NBFM | SA868-U | ✓ | ✓ (≤2 W) | listen and talk (voice walkie, PTT) |
| 27 MHz CB + HF / MW / LW | Si4732 | ✓ | — | listen AM / SSB / CW shortwave and CB |
| 64–108 MHz FM | Si4732 | ✓ | — | listen to FM broadcast radio |
| LoRa (EU433 / EU868 / US915) | SX1262 (cap) | ✓ | ✓ (+22 dBm) | Meshtastic encrypted text mesh, km range |

Legal LoRa power caps enforced in firmware: EU433 +10 dBm, EU868 +14 dBm, 869.4–869.65 MHz sub-band +27 dBm at 10% duty, US915 +30 dBm with frequency hopping.

## 🧩 Architecture at a glance

- **One brain:** ESP32-C5 (RISC-V) — native Wi-Fi 2.4 + 5 GHz and BLE in a single MCU. Firmware is ported from the ESP32-S3 (leshy) codebase.
- **All onboard RF** sits on shielded u.FL modules — chosen to de-risk the first PCB spin.
- **Shared buses:** SPI (TFT + microSD + cap, each with its own CS), I2C (both Grove ports + PCA9548 mux), UART (SA868 + cap).
- **7 onboard antennas:** C5 2.4/5 dual-band, 3× nRF24, CC1101, Si4732 telescopic whip, SA868 UHF. Antennas go on top; expander connectors on the sides or back. There is no shared RF switch, so each chain has its own antenna. (The plug-in cap adds its own LoRa RP-SMA + internal GPS ceramic.)
- **Expansion:** 1 cap slot + 2 Grove ports.
- **Power:** 2× 18650 in 2S (~7.4 V, ~18 Wh) with an onboard PMIC — BQ25xxx charger + USB-C PD (CH224K) + power-path (works while charging), buck 5 V/3 A + LDO 3.3 V. Runtime: light ~9 h, active ~3.6 h, TX peaks ~2.5 h.
- **PCB:** 4-layer (JLCPCB JLC7628), designed in KiCad. Antennas are tuned by hand with a VNA.

## ⚖️ Honest limits

- **5 GHz is Marauder-class only** — scan, deauth, beacon/probe flood, sniff. No WPA-handshake capture, no injection, no Pineapple-class. That needs Linux, which is deliberately avoided to keep battery life.
- **27 MHz (and all Si4732 HF) is receive-only.**
- **Voice-listening gaps:** ~108–430 MHz and ~480–860 MHz (airband AM 118–137, VHF/UHF NFM outside 433/446). Covering these would need an RTL-SDR + mini-Linux — out of scope.
- **Not a HackRF:** no continuous 1 MHz–6 GHz with arbitrary TX.
- **No wideband jamming** — it is illegal (US Communications Act §333, EU RED) and will not be built.
- **Hardware is not built yet** — this is a design-stage project.

## 🙏 Built on ESP32-DIV

Leshy2 stands on the shoulders of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV) by CiferTech (MIT, 3.7k stars) — a generous open-source multitool and the whole reason the leshy line exists. Leshy2 credits and builds on that work, and is developed in the open to invite collaboration with the DIV community. If you like this project, please star and support the original first.

## 📚 Docs

- [docs/hardware.md](docs/hardware.md) — full hardware breakdown.
- [docs/architecture.html](docs/architecture.html) — visual block diagrams (signal buses, audio path, power tree); open in a browser.
- [docs/roadmap.md](docs/roadmap.md) — where this is heading.
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to get involved.

## License

[MIT](LICENSE) — same as upstream ESP32-DIV. Copyright © Anton Vinogradov ([anton-vinogradov](https://github.com/anton-vinogradov)).
