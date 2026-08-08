# Draft — GitHub Discussion for ESP32-DIV

> **Draft for review — not posted.** Intended to be posted (only with the author's approval) as a
> GitHub Discussion in [cifertech/ESP32-DIV → Discussions](https://github.com/cifertech/ESP32-DIV/discussions).
> Russian version: [div-discussion.ru.md](div-discussion.ru.md).

**Suggested title:** Introducing Leshy2 — an ESP32-C5 field tool inspired by ESP32-DIV, and a hello about collaboration

---

## Hi cifertech and the ESP32-DIV community

First, a big thank you. ESP32-DIV is a wonderful project, and it is the reason I started building. I learned a lot from your work, and my firmware began as a fork of ESP32-DIV (MIT). All credit for the foundation goes to you and this community.

I want to introduce a project called **Leshy2** and, more importantly, ask if you would be open to working together in some way.

## Why I started

I love ESP32-DIV, but DIV v2 has no 5 GHz WiFi. The new **ESP32-C5** changes what is possible: it is a single RISC-V MCU with native WiFi **2.4 + 5 GHz** and BLE. That one chip removes the main gap, so I began porting the firmware from ESP32-S3 to C5 and grew the hardware around it.

Leshy2 is meant to stay in the same spirit as DIV: an open, portable, multiband RF field tool. It is not a replacement — it is a next step I would love to build **with** the community, not apart from it.

## What Leshy2 adds beyond DIV

- **ESP32-C5** single chip: native 2.4 + 5 GHz WiFi (5 GHz is Marauder-class: scan, deauth, beacon/probe flood, sniff management frames)
- **Si4732** receiver: CB 27 MHz + full HF/shortwave + MW/LW (AM/SSB/CW) + FM broadcast, with real analog audio out
- **SA868-U** UHF voice: NBFM walkie RX and TX (region/licence limited)
- **LoRa SX1262 / Meshtastic** for encrypted text at kilometer range
- **M5-compatible expansion**: a faithful Cardputer-ADV EXT 14P cap slot (hosts the LoRa + GPS cap) plus 2x Grove ports (NFC, RTC, IMU/compass, more)
- **2S 18650 power** (~7.4 V, ~18 Wh) with a proper PMIC and USB-C PD, so it runs while charging

Onboard RF is all self-built on shielded u.FL modules (3x nRF24L01+PA/LNA, CC1101, plus the above), direct SPI-TFT for a fast waterfall, microSD, IR TX/RX, WS2812 + buzzer, encoder. Target BOM is around 115-150 USD.

## Honest limits (so there is no hype)

- 5 GHz is **Marauder-class only** — no WPA handshake capture, no injection, not a WiFi Pineapple. That needs Linux, which I skip on purpose to keep battery life.
- It is **not a HackRF** — no continuous 1 MHz-6 GHz with arbitrary TX.
- 27 MHz and the HF/FM side are **receive only**. No wideband jamming (that is illegal under US Communications Act 333 and EU RED).

## The ask

Would you and the community be open to collaborating? I am flexible on the form, for example:

- Sharing design ideas and schematics openly (KiCad, 4-layer)
- Cross-pollinating firmware between DIV and the C5 port
- Or, if it fits your roadmap, helping DIV itself move toward some of these features (5 GHz, HF listening, expansion)

I do not want to pull attention away from DIV or push my project. I just think these ideas could help both, and I would rather build in the open with people I learned from.

Leshy2 is **MIT**, same as ESP32-DIV, and it credits DIV clearly. Architecture is locked and the next step is the KiCad schematic, so this is a good moment to align if there is interest.

Thank you again for ESP32-DIV and for reading. Whatever form (or none) feels right to you, I am grateful for the project and the community around it.

— Anton
