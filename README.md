# Leshy2

*Read this in: **English** · [Русский](README.ru.md)*

**An open-source, portable, multiband RF handheld — a field tool you build yourself.**

Leshy2 is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). It keeps the mature ESP32-S3 as the main brain and bolts on an **ESP32-C5 co-processor** for the one thing the S3 can't do — native **5 GHz** Wi-Fi. Two chips, one field tool, in the DIV-style handheld shape, built in the open for about **$135–160** (~$108–125 in electronics).

> 🛑 **Your own gear only.** An educational security-research and radio tool. Use it only on networks, devices, and radios you own or are explicitly authorized in writing to test. Radio law differs by country — it is on you to check and obey it.

---

## 📖 How to read this README

This README is the project's **source of truth**: the pipeline from idea to finished boards, **stage by stage**. Each stage sets a **Spec** (what and why), records the **Decisions** made in it, and produces **Artifacts** (files in this repo) that become the input to the next stage — so you can read it as *spec → decisions → result* and check each step.

**Status:** ✅ done · 🟡 in progress · ⏳ planned. Nothing is built on real hardware yet.

| # | Stage | Status |
|--:|-------|:------:|
| 1 | [Why a new device](#1-why-a-new-device--vision) | ✅ |
| 2 | [What it must do — capabilities](#2-what-it-must-do--capabilities) | ✅ |
| 3 | [Components](#3-components) | ✅ |
| 4 | [Architecture](#4-architecture) | ✅ |
| 5 | [External design & controls](#5-external-design--controls) | ✅ |
| 6 | [Schematic sheets](#6-schematic-sheets) | ✅ |
| 7 | [Merge, realize, review, complete](#7-merge-realize-review-complete) | 🟡 |
| 8 | [PCB layout](#8-pcb-layout) | 🟡 |
| 9 | [Firmware](#9-firmware) | ⏳ |
| 10 | [Validation gate — 5 GHz PoC](#10-validation-gate--5-ghz-poc) | ⏳ |
| 11 | [Fabrication & bring-up](#11-fabrication--bring-up) | ⏳ |

---

## 1. Why a new device — vision

**✅ Spec.** Take [ESP32-DIV](https://github.com/cifertech/ESP32-DIV) further: keep its mature ESP32-S3 design and **broaden what the handheld can do** — first the 5 GHz Wi-Fi DIV lacks, then a wider set of on-board radios and peripherals. Concretely, support:

- **5 GHz Wi-Fi + Zigbee / 802.15.4 / Thread** — via an **ESP32-C5** co-processor (the only ESP32 with native 5 GHz).
- **Bluetooth LE** — BLE advertising flood, and the phone-typed text keyboard / companion link (both MCUs have BLE).
- **2.4 GHz raw** — 3× nRF24L01+PA/LNA (parallel scan, mousejack, jammer).
- **Sub-GHz 315 / 433 / 868 / 915 MHz** — CC1101 + an SP4T multi-band front end.
- **LoRa / Meshtastic** — SX1262 / E22-900M22S (+22 dBm).
- **Voice walkie** — SA868-U, 2 W TX/RX 433 / 446 MHz NBFM.
- **HF / CB / FM receiver + real analog audio** — Si4732 + a PAM8302 amp → speaker + headphone jack.
- **GPS** (u-blox), **IR TX / RX**, **microSD** (PCAP logging).
- **2× Grove I²C** expansion for M5 Units (NFC / RFID2, RTC, IMU, sensors).
- **2S 18650 power** with an on-board balancing boost-charger.
- **A bigger, higher-res display** — a **4.0″ 320×480 IPS** panel vs DIV's 2.8″ 240×320 (ILI9341): same SPI interface, but **~2× the area and 2× the pixels** (~2× the waterfall on screen) and IPS for wider viewing angles. Same ~143 ppi — bigger and roomier, not sharper. Plus **capacitive touch** (DIV is button-only).
- **A proper control set** — a **5-way D-pad + BACK + OPTIONS + PTT + panic STOP + F1 / F2 + an encoder wheel** (DIV's buttons are minimal); long text is typed from a phone.
- **Honest "on-air" indicators** — a per-TX-chain amber TX LED (7 chains; a passive hardware envelope detector, 0 GPIO) that shows a chain is transmitting even if the firmware hangs.

The S3 stays the brain (UI, display, all wired radios, SD, buses, 2.4 GHz Wi-Fi + BLE); the C5 is a pure 5 GHz co-processor. DIV handheld shape, fair price (~$135–160), open so people can join in.

**This peripheral wishlist is the driver for everything downstream** — it sets the capabilities (stage 2), which pick the components (stage 3), which shape the architecture (stage 4) and the physical device (stage 5).

**Decisions.**

- **Two chips, not one.** The earlier single-**ESP32-C5** plan lost to its pin crunch (20/20) — and 5 GHz is the *only* thing the C5 does better than the S3. So the **S3** (mature, ~36 GPIO, the leshy firmware already runs on it) is the brain and the **C5** is a pure 5 GHz co-processor.
- **Extend DIV, don't reinvent it.** Keep DIV's proven S3 base and the firmware lineage; bolt radios and peripherals around it rather than a clean-sheet design.
- **Draw the scope boundary here** (the *out-of-scope* list below) so the later stages don't chase full-5 GHz monitor+inject, Linux-class analytics, HF-TX, wideband SDR, cellular or jamming — chip, budget and legal limits.

**Wanted, but out of scope (and why).** Some capabilities were dropped for reasons beyond our control or because they'd blow up the budget — the boundary is set here so the later stages don't chase them:

- **Full 5 GHz Wi-Fi (monitor + injection, WPA-handshake capture, Pineapple-class).** The C5 does only Marauder-class recon (scan / deauth / beacon / probe / sniff); raw monitor+inject on 5 GHz needs a Linux Wi-Fi stack no ESP32 has. *(chip / SDK limit)*
- **On-device Linux-class analytics (aircrack-ng, Kismet, WiFi Pineapple, handshake cracking).** Would need a Raspberry-Pi-class Linux SBC bolted on — blowing up budget, size, power and battery life. The point is a lean, all-day ESP32 handheld, not a Linux box: log PCAPs to SD and crunch them on a laptop. *(budget / complexity)*
- **HF / CB / shortwave transmit.** The Si4732 is receive-only and physically cannot transmit. *(chip limit)*
- **Continuous wideband SDR capture / arbitrary TX (HackRF-class).** No wideband IQ front end — a different, far pricier class of device. *(scope / budget)*
- **Cellular / GSM.** No modem. *(cost + legality)*
- **True simultaneous multi-radio.** With nine antennas in one small volume, keying every TX chain at once desenses the receivers, so the chains are time-shared (TDD arbitration in firmware; the 3× nRF24 parallel scan aside). *(RF coexistence — not the SPI bus, which sits at ~11–21 %.)*
- **Wideband jamming.** Deliberately not built — it is illegal (US §333, EU RED). *(legal — a "won't", not a "couldn't")*

**Artifacts.** This section, and the lineage it builds on:

- **[ESP32-DIV](https://github.com/cifertech/ESP32-DIV)** by CiferTech (MIT) — the hardware concept and the origin of the whole line.
- **[esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy)** — the firmware predecessor (our ESP32-S3 take on DIV), which Leshy2's software ports from.

If you like this project, please star and support the original ESP32-DIV first.

---

## 2. What it must do — capabilities

**✅ Spec.** Fix the feature set the hardware has to deliver (everything for your own equipment).

**Decisions.**

- **Marauder-class Wi-Fi, not Pineapple-class.** Both bands do the useful management-frame work — scan, sniff, deauth, beacon / probe flood — because that runs on the ESP32 radio directly. Full monitor + injection (WPA-handshake capture, aircrack) needs a Linux Wi-Fi stack no ESP32 has, so we don't claim it.
- **Analog receive audio, no MCU in the path.** No ESP32 has a real DAC, so sound never touches the chip: the radio's line-out goes through an analog mux into a PAM8302 class-D amp to the speaker / headphone jack. Clean audio, and the CPU stays free for the UI.
- **One TX chain at a time, not all radios at once.** Nine antennas share one small volume, so keying every transmitter together desenses the receivers. Firmware time-shares the TX chains; the only parallel exception is the 3× nRF24 receive-only band scan, which transmits nothing.

**Artifacts.** The capability list + the frequency map below.

**Recon / attacks**
- Wi-Fi 2.4 GHz (ESP32-S3): scan, **deauth**, beacon / probe flood, sniff management frames — Marauder-class.
- Wi-Fi 5 GHz (ESP32-C5): scan, sniff, beacon / probe flood — Marauder-class on the 5 GHz band DIV never had.
- 2.4 GHz raw (3× nRF24L01+PA/LNA): parallel whole-band scan, mousejack, channel analyzer.
- Sub-GHz (CC1101): capture and replay OOK / FSK remotes on 315 / 433 / 868 / 915 MHz; RSSI activity "geiger".
- BLE advertising flood + 802.15.4 / Zigbee sniff (ESP32-C5).
- NFC (RFID2 unit over Grove): read MIFARE / NTAG.

**Listen (by voice)**
- Si4732 (receive only): CB 27 MHz, full HF / shortwave, MW / LW (AM / SSB / CW), and FM broadcast 64–108 MHz.
- SA868-U: 433 / 446 MHz NBFM voice — listen and talk.
- Real analog audio: line-out → PAM8302 class-D amp → speaker + headphone jack. The MCU is **not** in the audio path.

**Transmit**
- SA868-U walkie: talk on 433 / 446 MHz, RX and TX up to 2 W (PTT). TX power is region / licence limited.
- Meshtastic over LoRa (SX1262 / E22-900M22S, +22 dBm): encrypted text mesh at kilometer range; power caps enforced per region in firmware.

**Spectrum view**
- 4.0″ IPS TFT (ST7796, 320×480) over SPI, **capacitive touch** — a large color waterfall on hardware vertical scroll.
- 2.4 GHz raw spectrum via the nRF24 chain; sub-GHz waterfall via CC1101.
- Per-TX-chain amber TX LED (7) — a hardware envelope detector, honest "on air" even if firmware hangs, 0 GPIO.

**Aux**
- microSD (SPI) for PCAP logging · WS2812 RGB status LED + buzzer · GPS (u-blox, UART) · IR TX/RX.
- **2× Grove HY2.0-4P (I²C, 3.3 V)** for M5 I²C Units (RFID2, RTC, IMU, sensors). Grove I²C Units only.
- Long text is typed on your phone (BLE / Wi-Fi) — no onboard keyboard (see stage 9).

### Frequency map

| Band | Chip | RX | TX | What you do |
|------|------|:--:|:--:|-------------|
| 2.4 GHz Wi-Fi + BLE | ESP32-S3 | ✓ | ✓ | scan, **deauth**, beacon / probe flood, sniff |
| 5 GHz Wi-Fi | ESP32-C5 | ✓ | ✓ | scan, sniff, beacon / probe flood |
| 802.15.4 / Zigbee + BLE | ESP32-C5 | ✓ | ✓ | Zigbee / Thread sniff, BLE adv flood |
| 2.4 GHz raw | 3× nRF24L01+ | ✓ | ✓ | whole-band scan, mousejack, analyzer |
| 315 / 433 / 868 / 915 MHz | CC1101 | ✓ | ✓ | capture / replay remotes, RSSI "geiger" |
| 433 / 446 MHz NBFM | SA868-U | ✓ | ✓ (≤2 W) | listen and talk (walkie, PTT) |
| 27 MHz CB + HF / MW / LW | Si4732 | ✓ | — | listen AM / SSB / CW and CB |
| 64–108 MHz FM | Si4732 | ✓ | — | listen to FM broadcast |
| LoRa (EU868 / US915) | SX1262 | ✓ | ✓ (+22 dBm) | Meshtastic encrypted text mesh |
| GPS L1 ~1.575 GHz | u-blox (UART) | ✓ | — | position / time |

**Honest limits.** 5 GHz is **Marauder-class only** (management-frame work — no full monitor + injection), all Si4732 HF is **receive-only**, and you **can't key every radio at once** (RF coexistence time-shares the chains — not a bus limit). For the full list of what's deliberately **out of scope and why** (raw 5 GHz, Linux-class analytics, wideband SDR, jamming…), see stage 1.

---

## 3. Components

**✅ Spec.** Choose the chips and modules that deliver the capabilities above, at a fair price.

**Decisions.**

- **Boost charger, not a buck or USB-PD.** The BQ25887 steps plain 5 V USB *up* to the 8.4 V a 2S pack needs, so no PD negotiation and no fragile high-voltage brick — any phone charger works. The trade-off: this chip has no power-path and no ship-mode, so a **hard master toggle is the only true off** (nothing sips the pack when it's off).
- **ST7796 on shared SPI, not AMOLED or a parallel panel.** The C5 has no `LCD_CAM` block and no spare pins for a parallel / QSPI bus, so the display shares the S3 SPI bus like every other wired part. SPI is enough because the waterfall rides the panel's **hardware vertical scroll** — per-frame writes stay tiny.
- **Wide-input bucks (MP2315) on both rails.** Both the +5 V and +3V3 bucks sit downstream of the 8.4 V BAT node, so each part must survive 8.4 V in. A 5.5 V-max part (e.g. TLV62569) would burn out there; the MP2315 takes the full 2S voltage.
- **Parts from LCSC / JLCPCB stock (assembly footprints).** Every choice is a real, in-stock, machine-placeable part rather than a datasheet ideal — so the BOM can actually be sourced and the board assembled without hand-soldering scarce chips.

**Artifacts.** The [**bill of materials & cost breakdown**](docs/bom.md) (~$108–125 in electronics) — every part, grouped by capability, with the biggest cost drivers.

---

## 4. Architecture

**✅ Spec.** Decide how the pieces connect: a two-chip topology, the shared bus and expanders, and a GPIO budget that fits this much radio.

**Decisions.**

- **S3 owns everything wired; the C5 does only 5 GHz.** All the wired radios, buses, SD, the display and native 2.4 GHz Wi-Fi hang off the S3 brain; the C5 handles only 5 GHz Wi-Fi and Zigbee / 802.15.4. There is no RF mode-switch to hand a shared antenna between chips, so splitting the radio work any other way would need parts and pins the board does not have.
- **Quad PSRAM, not octal.** Octal PSRAM would eat GPIO35–37; quad frees those three pins for the chip-to-chip link. GPIO33/34 are not broken out on the WROOM module, so the C5's EN and BOOT lines move onto a PCA9555 expander instead of costing S3 pins.
- **The chip-to-chip link is SPI3 + DRDY, not UART.** A dedicated SPI3 bus with a data-ready strobe keeps the C5 a clean SPI slave off the shared bus and gives real bandwidth for scan results; UART0 stays free for one job only — the S3 flashing the C5.
- **Expanders and a decoder beat the pin crunch.** The S3 is a full 36/36 chip, so ~30 slow signals (radio/display control, rail gates, UI buttons) go onto three I²C PCA9555 expanders at zero host pins, and one 74HC138 turns 3 pins into 8 chip-selects. Only timing-critical lines (encoder A/B, interrupts) keep direct S3 pins.
- **No standalone display on the C5.** Driving the panel from the C5 in a "C5-only" mode needed fragile Hi-Z and strapping-pin discipline on the shared bus for a low-value feature. Dropping it makes the C5 a pure co-processor and keeps the display firmly on the S3.

**Artifacts.** [system diagram](docs/img/system-diagram.svg) · [pin budget](docs/pin-budget.md) · [full hardware breakdown](docs/hardware.md).

![Leshy2 system architecture](docs/img/system-diagram.svg)

- **Two chips.** **ESP32-S3-WROOM-1U-N8R2** (dual-core, quad PSRAM) is the **main brain** — UI, display, all wired radios, SD, every bus, native 2.4 GHz Wi-Fi + BLE. **ESP32-C5-WROOM-1U** is a **pure co-processor** — the only ESP32 with native 5 GHz — on its own dual-band antenna.
- **Chip-to-chip link:** a dedicated **SPI3 + DRDY** strobe (the C5 is a clean SPI slave; it never touches the shared bus). The S3 flashes the C5 over UART0; the C5 also has its own USB-C for brick-safe recovery.
- **Shared bus (S3 FSPI):** microSD + CC1101 + 3× nRF24 + SX1262 + the display — chip-selects via a 74HC138. Three I²C **PCA9555** expanders carry the slow lines (radio/display control, rail gates, and the UI buttons); interrupts stay on direct pins.
- **Display:** the ST7796 **4.0″ 320×480 IPS** panel is on that shared SPI — the C5 has no `LCD_CAM` and there are no spare pins for a parallel / QSPI panel, so SPI it is; the waterfall rides the panel's **hardware vertical scroll** to keep per-frame updates tiny. The panel's **capacitive touch** rides the shared I²C bus (INT on the UI expander U14 — no host pin), a complement to the physical controls.
- **Human interface:** the D-pad, BACK / OPTIONS / STOP / F1 / F2 and the encoder push all read through the I²C **PCA9555** expanders (S3 GPIO is full and buttons are slow); only the encoder's A/B quadrature keeps two direct S3 pins (timing-critical). All buttons share one INT.
- **9 antennas** (S3 2.4, C5 2.4/5, 3× nRF24, CC1101, Si4732 whip, SA868, LoRa) — each chain its own antenna, on **9 removable board-mounted SMA jacks** along the top edge, the 3× nRF24 spread for isolation (details in stage 5).
- **Two USB-C:** J1 → S3 (charge + data), J2 → C5 (data-only). The pack charges only through J1.
- **Power:** 2× 18650 in 2S — **BQ25887 boost charger** (charges 2S from plain 5 V USB), MP2315 +5 V and +3V3 bucks, a TPS7A2033 +3V3 analog rail, rail gates that cut idle radios. A hard master toggle is the only on/off.

One radio runs at a time, so the shared bus and slow control lines fit the pin budget.

---

## 5. External design & controls

**✅ Spec.** From the components, settle the **physical device**: form factor (~80 × 170 mm, no case, DIV-style open frame), the control scheme, where the external interfaces sit, and the mechanical stack (display on the front over the electronics; 2× 18650 on the back; double-sided assembly — parts on both faces).

**Decisions.**

- **One board, not two.** Splitting the RF and the digital halves onto separate boards buys almost no isolation — with nine antennas this close, coupling is dominated by antenna-to-antenna paths in the air, not by traces on the board. And it would cost a shared solid ground, force fast buses like SPI2 across a connector (a signal-integrity risk), and double the NRE. So everything lives on one 80 × 170 mm board.
- **All nine antennas are board-SMA on the top edge.** Every radio ends in a removable SMA jack along the top, so antennas are swappable and stay away from the hand and the battery; the 3× nRF24 jacks are spread apart along the edge for the little isolation that physical distance does give. The Si4732 gets its own SMA plus a long telescopic whip for HF / CB.
- **No case — open frame, DIV-style.** Follow DIV: a bare double-sided board, ~80 × 170 mm, with the 2S 18650 cells in a plastic holder on the back (a keep-out, no parts under the cells) and the wired I/O on the bottom edge. It keeps the device thin, cheap and hackable, and leaves the whole front for the display.
- **Physical controls first, capacitive touch as a helper.** A full tactile set — D-pad + BACK / OPTIONS + PTT + panic-STOP + F1 / F2 + an encoder wheel — so the device is fully usable eyes-down and one-handed, with the buttons on a dedicated PCA9555 expander and the encoder A/B on direct GPIO for clean quadrature. The capacitive touchscreen is an addition on top, never the only way in; long text is still typed from a phone.

**Artifacts.** [**front & back layout**](docs/img/layout-front-back.en.svg) · [**controls & firmware conventions**](docs/firmware-controls.md).

![Leshy2 front & back layout](docs/img/layout-front-back.en.svg)

- **Front:** 4.0″ **capacitive-touch** display + D-pad (5-way) + BACK + OPTIONS.
- **Left edge:** IR TX/RX (top), encoder wheel (volume / value), F1 / F2, 3.5 mm jack.
- **Right edge:** PTT + panic STOP, 2× Grove (I²C).
- **Front (lower):** speaker + mic.
- **Bottom (on the back, facing down):** USB-C ×2, microSD, master toggle, RESET / BOOT.
- **Back:** 2× 18650 in clips (a keep-out zone — no parts under the cells).

The physical set is sufficient by a [scenario-coverage review](docs/firmware-controls.md); most of the usability lives in firmware conventions (stage 9).

---

## 6. Schematic sheets

**✅ Spec.** Capture each subsystem as its own sheet, transcribed from the architecture — as design docs **and** as live [tscircuit](https://tscircuit.com) code (real parts, LCSC numbers, exports to KiCad).

**Decisions.**

- **Schematic as code, not hand-drawn KiCad.** Each subsystem is one tscircuit `.tsx`; the schematic, PCB, netlist and KiCad export are *generated* from it — nothing is drawn by hand. So the source of truth is one file per sheet, edits regenerate every view, and connectivity is proven by netlist rather than by how a drawing looks.
- **Real footprints from the parts engine, not hand-entered pins.** Every IC pulls its manufacturer-verified footprint and pin names from its LCSC number (`jlcpcb:C…`); pins are never typed by hand. An early hand draft had wrong pin assignments — letting the engine own the pinout kills that whole class of error.
- **One sheet per subsystem.** Six sheets (power / buses / RF / audio / expansion / indicators) split along the architecture, so each is small enough to review on its own before the whole board is merged.
- **Realize against real modules to surface hidden blockers.** Drawing on the actual parts catches problems the logical schematic can't see: the C5's GPIO33/34 aren't broken out (so those control lines move onto a PCA9555 expander), the charger is a boost topology, and the sub-GHz SP4T needs three control lines, not one.

**Artifacts.** Six sheets — each a design doc in its own `hardware/<sheet>/` folder (linked below), with the live tscircuit `.tsx` and the exported schematic SVG in [`hardware/tscircuit/`](hardware/tscircuit/):

1. [Power](hardware/power/power.md) — 2S, BQ25887 boost charger, rails, master toggle
2. [MCU + buses](hardware/c5-buses/c5-buses.md) — S3 + C5, the SPI3 link, 74HC138, PCA9555, USB
3. [RF chains](hardware/rf/rf.md) — 3× nRF24, CC1101 + SP4T, SX1262 (LoRa)
4. [Audio](hardware/audio/audio.md) — Si4732, SA868, analog path → PAM8302
5. [Expansion + GPS](hardware/expansion/expansion.md) — I²C, u-blox GPS, Grove
6. [Indicators / IO](hardware/indicators/indicators.md) — TX-live LEDs, IR clone/replay, microSD, encoder

---

## 7. Merge, realize, review, complete

**🟡 Spec.** Merge the six sheets into one board on real, manufacturer-verified parts; review it adversarially; and finish the missing pieces so the schematic is complete before layout.

**Decisions.**

- **`board.tsx` is generated, not hand-merged.** `merge.py` assembles it from the six sheets + `integration.tsx`, so the sheets stay the single source of truth (edit a sheet, re-run the merge). A parts+nets diff-guard proved the generated board byte-identical to the hand-merged one it replaced — no silent drift when a sheet changes.
- **Review adversarially, before finishing.** Two whole-board self-reviews plus a per-sheet artifact pass ran *before* the completion work — they caught a real blocker (the PCA9555 has **no** internal pull-ups, so every switch input floated) and 5 major issues, all fixed. Cheaper to find on the schematic than at bring-up.
- **Antennas go to board-edge SMA, all on top.** Nine removable SMA jacks along the top edge instead of u.FL pigtails to a panel — one board, no fragile flying leads — and the 3× nRF24 are spread apart for receiver isolation.
- **Part swaps chosen by real stock + margin.** A 4 A PPTC (thermal headroom over the draw), a 20 mm on-board speaker, an LC balun into each SP4T arm, **two single 18650 holders** (to expose the pack mid-point the BQ25887 needs for balancing), and one 5-way nav switch under the D-pad — pick parts that are in stock and leave slack, not the tightest fit.
- **No blind edits — defer what needs measuring.** The Si4732 RCLK load-cap count is left as-is and flagged for an AN383 check at bring-up, rather than guessing a value on paper.

**Artifacts.** [`board.tsx`](hardware/tscircuit/board.tsx) — **generated** by [`merge.py`](hardware/tscircuit/merge.py) from the six sheets + [`integration.tsx`](hardware/tscircuit/integration.tsx) (223 parts) → [`board.kicad_pcb`](hardware/tscircuit/board.kicad_pcb) (connectivity proven, `schematic_parity = 0`).

Done:

- **✅ Merge** — `board.tsx` is *generated* from the sheets (single source of truth: edit a sheet or `integration.tsx`, then re-run `merge.py`). A parts+nets diff-guard proves it byte-identical to the hand-merged board it replaced.
- **✅ Realize** — every IC / module / connector rides a real LCSC footprint (tscircuit parts engine); only mechanical placeholders stay geometric.
- **✅ Review** — two adversarial whole-board self-reviews + a per-sheet artifact review (electrical + `.md`↔`.tsx`). Confirmed defects fed the fixes below.
- **✅ Electrical fixes (review)** — pull-ups on every PCA9555 switch input (10 UI buttons + encoder / card-detect / jack-detect / PTT — the part has **no** internal pull-ups); **J2 CC 5.1 kΩ** (C5 flash-over-USB); a pull-up on the wired-OR `PCA9555_INT`; **local decoupling** (100 nF per IC/module power pin + bulk); ~1 kΩ base resistors on the buzzer / IR drivers. TX-live LEDs set to minimal power (10 kΩ, ~0.1 mA). `.md`↔`.tsx` wording synced; netlist verified clean.

Remaining (🟡) — the completion list:
- **Part swaps (placeholder → real).** TVS/ESD, PPTC fuse, electret mic, speaker, buzzer, 3.5 mm jack, an 18650 holder with a reachable mid-point (the BQ25887 balances the 2S pack), RF balun, per-band matching networks, and one 5-way nav switch under the D-pad.
- **Stage-3 sub-circuits to draw.** The 7 RF envelope detectors (TX-live LEDs), the backlight driver (+ PWM dim), the Si4732 HF PIN-limiter.
- **Fab-verify.** "Confirm at layout / bring-up" items: Grove pin-1 orientation, supercap polarity / inrush, Si4732 bus-mode strap **and RCLK load-cap count** (AN383 — why the crystal cap wasn't blindly changed), boot-state pull-downs.

*Detail lands here as each item is done.*

---

## 8. PCB layout

**🟡 WIP.** Place the complete board (edge-aware zones, two-sided) on a 4-layer stack with a GND plane, route it (auto + hand-RF), add the mechanical → gerbers. *Detail is filled in as this stage is worked.*

**Decisions.**

- **Autoroute with Freerouting, not the earlier tool.** The earlier router stalled at ~45 % of the nets; Freerouting reached 85 % in one pass and 424/425 nets through a Specctra DSN/SES pipeline — so it does the bulk of the copper and leaves only the hard cases for hand-finishing.
- **4-layer stack with a solid GND plane (In1 = GND).** A dedicated ground layer gives short, clean return paths and one stable reference for the many radios — something a 2-layer board cannot hold on a device this dense.
- **RF feeders routed by hand.** The antenna feed lines need controlled impedance, coplanar geometry and antenna keep-outs, which an autorouter cannot honour — so the RF traces are drawn manually while Freerouting handles the rest.
- **Edge-aware placement.** Each connector sits on the edge it must reach and the antenna bank goes to the top — so cables and pigtails leave cleanly and the radios stay away from the digital noise.

---

## 9. Firmware

**⏳ WIP.** Port the S3 leshy code, write the C5 5 GHz agent + the S3↔C5 protocol, implement the [control conventions](docs/firmware-controls.md) + the two safety blockers. *Detail is filled in as this stage is worked.*

**Decisions.**

- **Port the S3 leshy firmware, don't rewrite it.** Most of the S3 side already runs there (UI, display, wired radios, buses, SD, 2.4 GHz Wi-Fi + BLE); reuse that lineage and grow the new peripherals around it instead of a clean-sheet start.
- **The C5 is a thin 5 GHz agent behind a narrow S3↔C5 protocol.** The S3 stays the brain and owns the UI; the C5 only does 5 GHz recon and answers a small command/event link over SPI3 + DRDY — keeps the two codebases decoupled and the C5 easy to bring up or replace on its own.
- **Orderly shutdown is a firmware feature, not the master switch.** The switch cuts the pack instantly (no ship-mode), so an in-flight PCAP / log would corrupt; **OPTIONS → Shut down** (and a long-BACK) flushes SD, parks all radios, stops S3 + C5, then shows a "safe to flip" screen.
- **long-BACK / STOP kills all TX, over any screen.** A stuck transmit (deauth, beacon spam, latched PTT, nRF24 / CC1101 / LoRa jam) with a hung UI must stop without pulling power; one core handler — reached from the hardware STOP key or a long-BACK — stops every chain.
- **Long text is typed on a paired phone over BLE.** There's no room for an onboard keyboard; a BLE companion is the primary path (keeps Wi-Fi free during attacks), a Wi-Fi captive portal is the app-less fallback, and the D-pad char-wheel stays for short offline entry.

---

## 10. Validation gate — 5 GHz PoC

**⏳ WIP.** Prove 5 GHz-deauth / recon on a C5 dev-kit before ordering — the riskiest premise, gated cheaply. *Detail is filled in as this stage is worked.*

**Decisions.**

- **Gate the whole 5 GHz bet on a bare ~$10 C5 devkit, before any copper.** The dual-chip design exists for one reason — 5 GHz usefulness. Answer that on a $10 board, not after a ~$140 build, so a bad result costs ten dollars, not a fab run.
- **Test only the open question — deauth.** Scan / sniff / beacon / probe flood are already known-good on the ESP-IDF Wi-Fi stack; the one thing nobody can promise up front is whether the C5 will actually send a 5 GHz deauth. The gate aims at that, not at the parts we already trust.
- **Prove the chip in isolation, not the board.** Run it on a stock devkit so the result reflects the C5's radio alone — no power rails, no SPI3 link, no our-own-layout risk mixed in. A clean yes/no on the silicon.
- **Record one honest verdict — works / PoC-only / not at all — and let it set the claim.** Whatever the devkit says is what the C5 is allowed to advertise before we commit to a PCB; no hopeful wording ahead of the proof.
- **A "no" here does not sink the board.** If 5 GHz deauth fails, the C5 falls back to passive recon and 2.4 GHz deauth still runs on the S3 — the gate trims what we claim, it does not cancel the build.

---

## 11. Fabrication & bring-up

**⏳ WIP.** Order (JLCPCB via a reshipper, or Rezonit), assemble, bring up, tune antennas on a VNA. *Detail is filled in as this stage is worked.*

**Decisions.**

- **Fab at JLCPCB through a reshipper, Rezonit as the fallback.** JLCPCB has no direct shipping to Russia, so the board goes via a reshipper (jlcpost-class); the JLC7628 4-layer stack and its in-house assembly are the cheapest way to get the impedance-controlled RF board built. Rezonit is the domestic Plan B if the reshipper route stalls.
- **Keep every part in LCSC stock.** The BOM is pinned to parts JLCPCB can actually place from the same catalog it fabs on — no chasing unobtainable substitutions mid-order, no hand-soldering surprises. Procurability wins over the "perfect" part.
- **Tune every antenna by hand on a VNA at bring-up.** Nine antennas share one small volume and each RF chain has its own match net; that interaction can't be simulated cleanly, so the match is trimmed on real hardware with a VNA rather than trusted to the layout.
- **Plan for two spins, not one.** Budget and schedule assume one working spin plus one refinement spin — an honest RF-board expectation, so the first order isn't treated as final copper. See [roadmap](docs/roadmap.md).

---

*Get involved: [CONTRIBUTING.md](CONTRIBUTING.md).*

## License

[MIT](LICENSE) — same as upstream ESP32-DIV. Copyright © Anton Vinogradov ([anton-vinogradov](https://github.com/anton-vinogradov)).
