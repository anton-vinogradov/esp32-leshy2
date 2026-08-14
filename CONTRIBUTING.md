# Contributing to Leshy2

*Read this in another language: [Русский](CONTRIBUTING.ru.md)*

## Welcome

Leshy2 is an open, **design-stage** project. It is a portable multiband RF handheld ("field tool"), and the successor to the [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) firmware (itself a fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV)). The architecture is locked, and the next step is the KiCad schematic. Nothing is set in silicon yet, so this is a great time to join.

Collaboration is very welcome — **especially from the ESP32-DIV community**. If you have built, hacked, or improved an ESP32-DIV, your experience is exactly what this project needs.

You do not need to be an RF expert to help. There is room for hardware people, firmware people, testers, and writers.

## Ways to help

- **Review the KiCad schematic.** Two MCUs: an **ESP32-S3** brain (Xtensa, native 2.4 GHz WiFi + BLE) that runs everything, plus an **ESP32-C5** co-processor (RISC-V) for native 5 GHz WiFi (and 2.4 / BLE / 802.15.4). All RF is self-built on shielded modules (3× nRF24L01+PA/LNA, CC1101, SX1262/LoRa, Si4732 RX-only, SA868-U). Extra eyes on nets, power, and pin choices are valuable.
- **Help with the firmware.** The main firmware is ported from the ESP32-S3 (leshy) codebase and stays on the S3; the C5 runs a small 5 GHz agent that talks to the S3 over the link. Help with drivers, peripheral bring-up, and the S3↔C5 protocol is welcome.
- **Review the PCB layout / RF layout.** The board is 4-layer (JLCPCB JLC7628, +-10% impedance), designed in KiCad. Good RF layout, grounding, and shielding review helps a lot.
- **Antenna tuning / VNA.** There are 9 onboard antennas, plus the GPS module's own antenna. Tuning each chain with a VNA is a manual step. If you know antenna matching, please share.
- **Testing.** Build it, run it, and report what works and what does not. Bug reports with clear steps are gold.
- **Docs.** Improve setup guides, wiring notes, and user docs. Simple, clear writing helps everyone.
- **Translations.** Help translate docs into more languages so more people can join.

## Relationship to ESP32-DIV

Leshy2 builds on and credits **ESP32-DIV** (by cifertech, MIT license). We want to grow the same idea, not fork away from it.

The main reason Leshy2 exists: ESP32-DIV v2 has **no 5 GHz WiFi**. The goals are to move the DIV idea toward:

- **5 GHz WiFi** (recon-class: scan, sniff management frames, beacon/probe flood; deauth is unproven until it's tested on hardware), and
- **legal long-range TX** (Meshtastic over onboard LoRa).

Where something we build is useful upstream, we want to **feed it back and collaborate** rather than split the community. If you are a DIV maintainer or user, please tell us how to keep the two projects friendly and compatible.

## How we discuss

- Use **GitHub Discussions** for ideas, design questions, and open talk.
- Use **GitHub Issues** for bugs and concrete tasks. Please include steps, expected result, and what you saw.

Keep it in the open when you can, so others can learn and join in.

## Licensing

Leshy2 is **MIT licensed**, the same as upstream ESP32-DIV.

By sending a contribution (code, schematic, docs, or other work), you agree that it is licensed under **MIT**. Please only submit work that you have the right to share.

## Ground rules

- **Be respectful.** Be kind and patient. We are all here to learn and build.
- **Keep RF legal.** No wideband jamming — it is illegal (US Communications Act section 333; EU RED).
- **Respect regional limits.** Honor the power and duty-cycle caps enforced per region in firmware, for example: LoRa EU433 +10 dBm, EU868 +14 dBm, the 869.4-869.65 MHz sub-band +27 dBm at 10% duty cycle, US915 +30 dBm with frequency hopping. SA868 TX is region/licence limited (446 PMR max 0.5 W ERP; 5 W only on ham 70 cm with a licence).
- Do not add or ask for features that break these rules.

Thank you for helping build Leshy2 in the open.
