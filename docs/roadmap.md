# Leshy2 — Roadmap

*Read this in: **English** · [Русский](roadmap.ru.md)*

Where **Leshy2** is going — an open-source portable multiband RF handheld (a "field tool"). It is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). The reason for a new board is simple: DIV and leshy could not do 5 GHz Wi-Fi. Leshy2 fixes that by keeping the mature **ESP32-S3** brain and bolting on an **ESP32-C5** as a 5 GHz co-processor. Target: as capable as reasonable at a fair price — see the [cost breakdown](bom.md).

## 🧭 Where we are

- **Architecture is locked (2026-08-10): two chips.** This is still the **design stage** — **no hardware has been built yet**.
- The six schematic sheets exist as **transcribe-ready specs (Markdown)**; the SVG drawings are being redrawn to the two-chip layout.
- **Next:** capture the sheets in **KiCad**, then **PCB layout**.
- 🔴 **Gate before ordering any PCB:** prove **5 GHz deauth on a bare ESP32-C5 devkit**. If it can't deauth, the C5's headline feature shrinks to passive recon — we want that answered on a $10 board, not a $140 build.

## 🧠 The two-chip split

The single-chip idea (one C5 doing everything) was dropped. The C5 is young silicon with no LCD_CAM and a tight pin budget; the S3 is proven and already runs leshy. So the roles split:

| | **ESP32-S3-WROOM-1U-N8R2** — the brain | **ESP32-C5-WROOM-1U** — the co-processor |
|---|---|---|
| Cores / RAM | 2× Xtensa, QUAD-PSRAM | RISC-V |
| Owns | UI, display, **all wired radio**, SD, buses, 2.4 GHz Wi-Fi + BLE (native) | native **5 GHz** Wi-Fi (the only ESP32 that has it) + 2.4 / BLE / 802.15.4 (Zigbee/Thread) |
| Pins | **38 / 38 — full** | ~11 / 20 |
| Flashing | USB-C **J1** (charge + data) | flashed by the S3 over UART0 (auto-OTA) **and** its own USB-C **J2** (data-only, brick-safe) |

**Link:** a dedicated **SPI3 + DRDY** strobe (ready-line) between S3 and C5. The S3 stays the single point of control; the C5 is a pure 5 GHz agent.

## 🚦 Phases

### 1. Architecture — done

- [x] Two chips: **S3 brain** + **C5 5 GHz co-processor**, linked by dedicated SPI3 + DRDY
- [x] Shared **SPI2** bus (S3 FSPI, 80 MHz): microSD + CC1101 + 3× nRF24 + SX1262 + ST7796, chip-selects via a **74HC138** decoder
- [x] Slow control on **two PCA9555** expanders: 0x20 (radio / display control), 0x21 (PTT / rail-gates / SP4T / headphone jack)
- [x] Direct interrupt lines kept off the expanders: LoRa DIO1, nRF24 IRQ (via a 74AHC gate), CC1101 GDO2 carrier-sense (GPIO45 de-strapped via an eFuse flash-voltage set), CC1101 GDO0
- [x] RF set: **3× nRF24L01+PA/LNA** (2.4 raw), **CC1101** (bare + crystal + balun) → **SP4T PE42440** + 4 matching networks (315 / 433 / 868 / 915), **SX1262** (E22-900M22S, +22 dBm LoRa), **Si4732-A10** (HF/CB/FM, RX only), **SA868-U** (433 / 446 voice, 2 W)
- [x] Audio: analog mono → **PAM8302** class-D → speaker + headphone jack; the MCU is not in the audio path
- [x] **ST7796 320×480 IPS** display over SPI (not 8080 / AMOLED — the C5 has no LCD_CAM; the waterfall rides the panel's hardware vertical scroll)
- [x] **GPS** (u-blox, UART, onboard); **2× Grove I²C** + RFID2 unit
- [x] Power: **2S 2×18650**, BQ25887 boost (5 V→8.4 V, no PD), S-8252A protection, MP2315 +5 V, TLV62569 +3V3, TPS7A2033 +3V3A, master toggle; rails gated in idle
- [x] **9 antennas**, no RF switch between chains: S3 2.4 (external SMA), C5 dual 2.4/5, 3× nRF24, CC1101, Si4732 telescopic, SA868 UHF, SX1262 LoRa
- [x] Inputs: RESET, BOOT, **PTT**, rotary encoder; master toggle = power

### 2. KiCad schematic — next

Six sheets, already written as specs; capture them in KiCad in this order.

- [x] **Power** (Sheet 1, [hardware/power](../hardware/power/power.md))
- [x] **S3 + C5 + buses** (Sheet 2, [hardware/c5-buses](../hardware/c5-buses/c5-buses.md)): both MCUs, the SPI3+DRDY link, shared SPI2 + 74HC138, two PCA9555, UART, encoder + buttons, dual USB-C
- [x] **RF chains** (Sheet 3, [hardware/rf](../hardware/rf/rf.md)): 3× nRF24, CC1101 + SP4T + 4 match nets, SX1262
- [x] **Audio** (Sheet 4, [hardware/audio](../hardware/audio/audio.md)): Si4732 RX, SA868-U walkie, PAM8302 + speaker + jack
- [x] **Expansion + GPS** (Sheet 5, [hardware/expansion](../hardware/expansion/expansion.md)): onboard u-blox GPS, 2× Grove I²C, full I²C address map
- [x] **Indicators + I/O** (Sheet 6, [hardware/indicators](../hardware/indicators/indicators.md)): per-chain hardware TX-live LEDs (0 GPIO), WS2812, buzzer, IR TX/RX, microSD

### 3. 🔴 5 GHz deauth PoC — gate before PCB

- [ ] On a bare **C5 devkit**: scan / sniff 5 GHz, beacon + probe flood, and **attempt deauth**
- [ ] Record the honest answer (works / PoC-only / not at all) — it sets what the C5 is allowed to claim before we commit copper

### 4. PCB layout

- [ ] **4-layer** board (JLCPCB JLC7628, impedance ±10 %)
- [ ] Impedance-controlled RF traces; bulk caps right next to the nRF24 modules
- [ ] Placement: antennas on top; the external SMA for the S3 2.4 chain
- [ ] Power and RF grounding

### 5. First PCB spin

- [ ] Order, solder, assemble (maker steps)
- [ ] Bring-up: power rails, S3 boot, C5 boot, the SPI3 link, then each bus
- [ ] **Honest expectation: 1 working spin + 1 refinement spin**

### 6. Firmware

Three pieces: port the existing brain, add the 5 GHz agent, and glue them.

- [ ] **Port leshy** (the S3 codebase already runs — mostly bring-up on the new board)
- [ ] **C5 5 GHz agent**: scan / sniff / beacon-probe flood (+ deauth if the PoC says yes)
- [ ] **Link protocol** over SPI3+DRDY: the S3 drives, the C5 answers
- [ ] Drivers: 3× nRF24, CC1101 (+ SP4T band select), SX1262, Si4732, SA868-U, u-blox GPS, microSD PCAP
- [ ] Per-region LoRa power caps enforced in firmware (EU433 +10 dBm, EU868 +14 dBm, 869.4–869.65 MHz +27 dBm @ 10 % duty, US915 +30 dBm w/ hopping)
- [ ] BLE text entry (long text typed on a phone)

### 7. Antenna tuning (VNA)

- [ ] Tune each of the 9 antennas with a **VNA** (manual maker step)

### 8. Field testing

- [ ] Runtime (light ~9 h, active ~3.6 h, TX peaks ~2.5 h)
- [ ] Range: SA868 voice (~3–5 km open), Meshtastic (city 2–5 km, LOS 10–15 km)
- [ ] Real-world validation of every RF chain

## 🧠 Firmware roadmap — free features

The silicon is already paid for; these are software-only wins we plan to add over time.

- **Evil Portal / Karma / rogue-AP** — captive-portal and karma attacks on 2.4 GHz (S3)
- **BLE advertising flood + 802.15.4 / Zigbee sniff** (C5)
- **Auto-dim backlight** — the display is the biggest idle draw; dim it when nothing changes
- **LoRa Rx Boosted Gain** — SX1262 setting, +15–30 % range for free
- **Dirty-rect UI** — redraw only what changed on the ST7796
- **Shared-bus smoothing** — DMA + double buffer + a firmware **bus arbiter** (0 pins) + an **SD watchdog**; the shared SPI2 contention is a phantom (~11–21 %, almost all SD bursts), so the fix is software, not more copper

## 🧱 Deliberately out of scope — honest ceilings

- **5 GHz is recon-class only** — scan, sniff, beacon / probe flood; **deauth is a PoC question** (see phase 3). No injection, no WPA-handshake capture, no monitor+inject — those need Linux, which we avoid for battery life. **2.4 GHz deauth works** (on the S3).
- **Si4732 is receive-only** — HF / CB / FM listening, no TX there.
- **One radio at a time** — chains share the bus and the operator's attention; this is not a simultaneous multi-radio SDR.
- **Mono audio.**
- **Not a HackRF** — no continuous wideband capture, no arbitrary TX.
- **No wideband jamming** — it is illegal (US Communications Act §333, EU RED).

## 🤝 How you can help

Leshy2 is built openly and credits ESP32-DIV; the aim is collaborative development with the DIV community. To help with the schematic, the PCB, the firmware, or the 5 GHz PoC, start with **[CONTRIBUTING](../CONTRIBUTING.md)**.

---

*Part of [Leshy2](../README.md) · MIT. Per-sheet detail lives in [hardware/](../hardware).*
