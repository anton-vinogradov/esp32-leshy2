# Leshy2

*Read this in: **English** · [Русский](README.ru.md)*

**An open-source, portable, multiband RF handheld — a field tool you build yourself.**

Leshy2 is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), which is a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). The reason for a new device is simple: ESP32-DIV v2 has no 5 GHz Wi-Fi. Leshy2 fixes that **without throwing away the mature ESP32-S3 design** — it keeps the S3 as the main brain (UI, display, every wired radio, SD, buses, native 2.4 GHz Wi-Fi + BLE) and bolts on an **ESP32-C5 co-processor** for the one thing the S3 can't do: native **5 GHz** Wi-Fi (plus 2.4 GHz, BLE and 802.15.4 / Zigbee / Thread). Two chips, one field tool. The goal is to be as capable as is reasonable at a fair price — about **$135–160 built** (~$108–125 in electronics; see the [cost breakdown](docs/bom.md)). It keeps the DIV-style handheld shape, just modernized, and is built in the open so people can join in.

> 🛑 **Your own gear only.** This is an educational security-research and radio tool. Use it only on networks, devices, and radios you own or are explicitly authorized in writing to test. Radio law differs by country — it is on you to check and obey it.

## 🌳 Lineage

Leshy2 stands on two projects:

- **[ESP32-DIV](https://github.com/cifertech/ESP32-DIV)** by CiferTech (MIT) — the hardware concept and the origin of the whole line.
- **[esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy)** — the firmware predecessor (our ESP32-S3 take on DIV), which Leshy2's software is ported from.

## 📌 Status

**Design-stage open project — the full schematic is done on real parts; no hardware built yet.**

The hardware has been taken from idea to a **complete, real-parts schematic**, in stages:

1. **✅ Architecture locked** — two chips: ESP32-S3 brain + ESP32-C5 5 GHz co-processor.
2. **✅ Design docs** — all six sheets (power · MCU+buses · RF · audio · expansion · indicators) plus the [pin budget](docs/pin-budget.md), [BOM](docs/bom.md) and [hardware breakdown](docs/hardware.md), bilingual, in [hardware/](hardware/).
3. **✅ Schematic captured as code** — every sheet is [tscircuit](https://tscircuit.com) `.tsx` in [hardware/tscircuit/](hardware/tscircuit/) (one source → schematic image + netlist + KiCad PCB, nothing hand-drawn), then merged into a single [`board.tsx`](hardware/tscircuit/board.tsx).
4. **✅ Self-review #1 (logic)** — a multi-agent adversarial review; **8 fixes**, including a blocker (the +3V3 buck couldn't sit on the 8.4 V pack → swapped to a wide-Vin part).
5. **✅ Realized with real parts** — every IC/module now carries its **manufacturer-verified footprint + pinout**, pulled by LCSC part number. Going to real parts caught hardware bugs the ideal schematic can't show: a charger wired for the wrong topology, two MCU pins that aren't bonded out on the module, a single-supply walkie, a wrong level-shifter pinout, missing support networks. Each sheet passes KiCad DRC.
6. **✅ Self-review #2 (real board)** — **6 more fixes**, including 2 blockers (the charger's current-sense was shorted to the battery; the I²C ESD array was reversed).
7. **✅ One board** — all six sheets merged: **174 real components, connectivity proven** (KiCad `schematic_parity = 0`), ready to lay out. See [hardware/tscircuit/](hardware/tscircuit/).
8. **⏭ Next:** **PCB layout** in KiCad (placement, ground planes, RF feeds by hand) → gerbers → fab. A 5 GHz-deauth proof-of-concept on a C5 dev-kit precedes ordering the board.

Across the two reviews **~14 real defects were caught and fixed — 4 of them board-killers.** Nothing has been built or tested on real hardware yet. Follow along, comment, and contribute while it takes shape.

## 🧰 What it does

Grouped by what you actually do with it. Everything is meant for your own equipment.

**Recon / attacks**
- Wi-Fi 2.4 GHz (ESP32-S3): scan, **deauth**, beacon / probe flood, sniff management frames — Marauder-class.
- Wi-Fi 5 GHz (ESP32-C5): scan, sniff, beacon / probe flood — 5 GHz recon that DIV never had.
- 2.4 GHz raw (3× nRF24L01+PA/LNA): parallel whole-band scan, mousejack, channel analyzer.
- Sub-GHz (CC1101): capture and replay OOK / FSK remotes and sensors on 315 / 433 / 868 / 915 MHz; RSSI activity "geiger".
- BLE advertising flood + 802.15.4 / Zigbee sniff (ESP32-C5).
- NFC (RFID2 unit over Grove): read MIFARE / NTAG.

**Listen (by voice)**
- Si4732 (receive only): CB 27 MHz, full HF / shortwave, MW / LW (AM / SSB / CW), and FM broadcast 64–108 MHz.
- SA868-U: 433 / 446 MHz NBFM voice — you can both listen and talk.
- Real analog audio: mono line-out → PAM8302 class-D amp → speaker + headphone jack. The MCU is **not** in the audio path.

**Transmit**
- SA868-U walkie: talk on 433 / 446 MHz, RX and TX up to 2 W (PTT button, UART control). TX power is region / licence limited — 446 PMR max 0.5 W ERP; 5 W only on ham 70 cm with a licence.
- Meshtastic over LoRa (onboard SX1262 / E22-900M22S, +22 dBm): encrypted text mesh at kilometer range. Legal power caps are enforced per region in firmware.

**Spectrum view**
- 3.5″ IPS TFT (ST7796, 320×480) over SPI — a large color waterfall on hardware vertical scroll, with a bright backlight that stays readable outdoors.
- 2.4 GHz raw spectrum via the nRF24 chain; sub-GHz waterfall via CC1101.
- Per-antenna amber TX LED — a hardware envelope detector, honest "on air" even if firmware hangs, 0 GPIO. No RX LED (a detector would hurt receive sensitivity); the display shows the active chain.

**Aux (onboard)**
- microSD (SPI) for PCAP logging.
- WS2812 RGB status LED + buzzer.
- Buttons (RESET, BOOT, PTT) + rotary encoder; a master toggle is the only on/off.
- GPS (u-blox onboard over UART) for position / time.
- Long text is typed on your phone over BLE (Meshtastic app) — there is no onboard keyboard.

**Expandability (M5-compatible)**
- **2× Grove HY2.0-4P ports (I²C, 3.3 V).** Host M5 I²C Units — RFID2 NFC, RTC, IMU / compass, sensors — addressed individually. (The u-blox GPS is onboard on UART, not on this bus.)
- Supports M5 **Grove I²C Units** only. M5 **Caps**, **Modules** and StickC **HATs** use different connectors and are **not** supported.

## 📻 Frequency map

| Band | Chip | RX | TX | What you do |
|------|------|:--:|:--:|-------------|
| 2.4 GHz Wi-Fi + BLE | ESP32-S3 | ✓ | ✓ | scan, **deauth**, beacon / probe flood, sniff mgmt frames |
| 5 GHz Wi-Fi | ESP32-C5 | ✓ | ✓ | scan, sniff, beacon / probe flood (recon-only) |
| 802.15.4 / Zigbee + BLE | ESP32-C5 | ✓ | ✓ | Zigbee / Thread sniff, BLE adv flood |
| 2.4 GHz raw | 3× nRF24L01+ | ✓ | ✓ | parallel whole-band scan, mousejack, channel analyzer |
| 315 / 433 / 868 / 915 MHz | CC1101 | ✓ | ✓ | capture / replay OOK / FSK remotes & sensors, RSSI "geiger" |
| 433 / 446 MHz NBFM | SA868-U | ✓ | ✓ (≤2 W) | listen and talk (voice walkie, PTT) |
| 27 MHz CB + HF / MW / LW | Si4732 | ✓ | — | listen AM / SSB / CW shortwave and CB |
| 64–108 MHz FM | Si4732 | ✓ | — | listen to FM broadcast radio |
| LoRa (EU433 / EU868 / US915) | SX1262 (onboard) | ✓ | ✓ (+22 dBm) | Meshtastic encrypted text mesh, km range |
| GPS L1 ~1.575 GHz | u-blox (UART) | ✓ | — | position / time (NMEA over UART) |

Legal LoRa power caps enforced in firmware: EU433 +10 dBm, EU868 +14 dBm, 869.4–869.65 MHz sub-band +27 dBm at 10% duty, US915 +30 dBm with frequency hopping.

## 🧩 Architecture at a glance

![Leshy2 system architecture](docs/img/system-diagram.svg)

- **Two chips.** **ESP32-S3-WROOM-1U-N8R2** (dual-core, quad PSRAM) is the **main brain** — UI, display, all wired radios, SD, every bus, and native 2.4 GHz Wi-Fi + BLE, on a full 38 / 38 GPIO. **ESP32-C5-WROOM-1U** is a **pure co-processor** — the only ESP32 with native 5 GHz — adding 5 GHz / 2.4 GHz / BLE / 802.15.4, on its own dual-band antenna and ~11 / 20 GPIO. Firmware is ported from the ESP32-S3 (leshy) codebase.
- **Chip-to-chip link:** a dedicated **SPI3 + DRDY** strobe (the C5 is a clean SPI slave; DRDY signals when it has data). The C5 never touches the shared bus. The S3 can flash the C5 over UART0 (auto-OTA, keeps both images in sync); the C5 also has its own USB-C for brick-safe recovery.
- **Shared bus (S3 FSPI, 80 MHz):** microSD + CC1101 + 3× nRF24 + SX1262 + the ST7796 display — chip-selects via a 74HC138 decoder. Two I²C **PCA9555** expanders carry the slow control lines: 0x20 (radio / display control) and 0x21 (PTT, rail gates, SP4T select, audio jack). Interrupts stay on direct pins: LoRa DIO1, nRF24 IRQ, CC1101 carrier-sense.
- **9 antennas:** S3 2.4 GHz (external SMA), C5 dual-band 2.4 / 5, 3× nRF24, CC1101, Si4732 telescopic whip, SA868 UHF, SX1262 LoRa. There is no shared RF switch, so each chain has its own antenna (the sub-GHz band-select uses an SP4T + four matching networks behind the single CC1101 antenna).
- **Display:** ST7796 320×480 IPS over SPI (not 8080 / AMOLED — the C5 has no LCD_CAM), waterfall on hardware vertical scroll.
- **Two USB-C ports:** J1 → S3 (charge + data), J2 → C5 (data-only, brick-safe). One power source — the pack charges only through J1.
- **Power:** 2× 18650 in 2S with an onboard PMIC — **BQ25887 boost charger** (charges 2S from plain 5 V USB, no PD), MP2315 buck +5 V, a second wide-Vin MP2315 buck +3V3, a separate TPS7A2033 +3V3 analog rail, and rail gates that cut idle radios. A hard master toggle is the only on/off.

One radio runs at a time, so the shared SPI bus and the slow control lines fit this much radio into the pin budget. See [docs/pin-budget.md](docs/pin-budget.md).

## ⚖️ Honest limits

- **5 GHz is recon-only** — scan, sniff, beacon / probe flood. No injection, no WPA-handshake capture, no monitor+inject. That needs Linux, which is deliberately avoided to keep battery life. (2.4 GHz deauth works, on the S3.)
- **27 MHz (and all Si4732 HF) is receive-only.**
- **One radio at a time** — the RF chains share the SPI bus, so idle radios sleep while one is active.
- **Not a HackRF:** no continuous wideband capture and no arbitrary TX.
- **No wideband jamming** — it is illegal (US Communications Act §333, EU RED) and will not be built.
- **Hardware is not built yet** — this is a design-stage project.

## 🙏 Built on ESP32-DIV

Leshy2 stands on the shoulders of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV) by CiferTech (MIT) — a generous open-source multitool and the whole reason the leshy line exists. Leshy2 credits and builds on that work, and is developed in the open to invite collaboration with the DIV community. If you like this project, please star and support the original first.

## 📚 Docs

**Overview**
- [docs/hardware.md](docs/hardware.md) — full hardware breakdown (BOM, antennas, buses, power).
- [docs/bom.md](docs/bom.md) — **cost & bill of materials** (~$108–125 electronics).
- [docs/pin-budget.md](docs/pin-budget.md) — the GPIO budget for both chips and every pin's role.

**Schematic** — each sheet is a design doc (below) **and** live [tscircuit](https://tscircuit.com) code in [hardware/tscircuit/](hardware/tscircuit/) (real parts, LCSC part numbers, exports to KiCad). The whole device is one merged board: [`board.tsx`](hardware/tscircuit/board.tsx) → [`board.kicad_pcb`](hardware/tscircuit/board.kicad_pcb).
1. [Power](hardware/power/power.md) — 2S, BQ25887 boost charger, rails, master toggle
2. [MCU + buses](hardware/c5-buses/c5-buses.md) — S3 + C5, the SPI3 link, 74HC138, 2× PCA9555, USB
3. [RF chains](hardware/rf/rf.md) — 3× nRF24, CC1101 + SP4T, SX1262 (LoRa)
4. [Audio](hardware/audio/audio.md) — Si4732, SA868, analog path → PAM8302
5. [Expansion + GPS](hardware/expansion/expansion.md) — I²C, u-blox GPS, Grove
6. [Indicators / IO](hardware/indicators/indicators.md) — TX-live LEDs, microSD, encoder

**More**
- [docs/roadmap.md](docs/roadmap.md) — where this is heading.
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to get involved.

## License

[MIT](LICENSE) — same as upstream ESP32-DIV. Copyright © Anton Vinogradov ([anton-vinogradov](https://github.com/anton-vinogradov)).
