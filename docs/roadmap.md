# Leshy2 — Roadmap

*Read this in: **English** · [Русский](roadmap.ru.md)*

A pragmatic plan for **Leshy2** — an open-source portable multiband RF handheld (a "field tool"). It is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), which is a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). The reason for a new board: ESP32-DIV v2 has no 5 GHz Wi-Fi. Goal: as capable as reasonable at a fair price, target BOM about **115-150 USD**.

## Where we are

- **Architecture is locked (2026-08-08).** This is still the **design stage** — **no hardware has been built yet**.
- The brain is the **ESP32-C5** (a single RISC-V MCU with native Wi-Fi 2.4 + 5 GHz and BLE). The firmware will be ported from the ESP32-S3 (leshy) codebase.
- The next concrete step is the **KiCad schematic**.

## Phases

### 1. Architecture — done

- [x] Pick the brain: **ESP32-C5** (one chip, native 2.4 + 5 GHz Wi-Fi + BLE)
- [x] Lock the onboard RF set: **3x nRF24L01+PA/LNA**, **CC1101**, **Si4732**, **SA868-U**
- [x] Lock the audio path: analog line-out (Si4732 / SA868) -> **PAM8302** class-D amp -> small speaker
- [x] Lock long-range TX: **Meshtastic over LoRa SX1262**, onboard
- [x] Lock the display: **3.5″ IPS TFT (ST7796, 320×480) over SPI** (shares the radio SPI bus, CS via 138 + DC)
- [x] Lock expansion: **1× Grove HY2.0-4P (I²C)** port (M5 I²C Units)
- [x] Lock power: **2S 18650**, own PMIC (BQ25xxx charger + CH224K USB-C PD + power-path, buck 5V/3A, LDO 3.3V)
- [x] Lock antennas: **8 onboard** (LoRa now on the board); one hardware TX-live LED per transmit chain (no RX LED); the GPS antenna sits on the u-blox module

### 2. KiCad schematic — next

Built sheet by sheet. Start with power, then the MCU and its buses, then each RF chain.

- [ ] **Power first:** 2S 18650 -> BQ25xxx charger + CH224K USB-C PD + power-path -> buck 5V/3A -> LDO 3.3V
- [x] **C5 + buses** (Sheet 2, [hardware/c5-buses](../hardware/c5-buses/c5-buses.md)): ESP32-C5 (PSRAM), SPI (microSD + SX1262 + CC1101 + 3× nRF24 + ST7796, chip-selects via a 74HC138 decoder), I2C (Si4732 + u-blox GPS + PCA9555 expander + Grove), UART (SA868), rotary encoder + buttons, native USB
- [x] **RF chain — 3x nRF24L01+PA/LNA** (Sheet 3, [hardware/rf](../hardware/rf/rf.md)): brownout fix = 100-220 µF bulk + 100 nF at each module VCC; CSN via 138, tied CE, IRQ polled
- [x] **RF chain — CC1101** sub-GHz (Sheet 3): 300-928 MHz OOK/FSK; CS via 138, GDO0 direct; optional RF switch to fold its bands into one SMA
- [x] **RF chain — SX1262 (LoRa)** onboard (Sheet 3): E22-900M22S +22 dBm; NSS via 138, BUSY direct, DIO1 polled, NRESET on the PCA9555
- [x] **Audio — Si4732** receiver (Sheet 4, [hardware/audio](../hardware/audio/audio.md)): HF input with an ESD/clamp protector, no manual disconnect (mode-exclusive sleep), analog line-out, RST on the PCA9555
- [x] **Audio — SA868-U** walkie (Sheet 4): UART control, PTT/PD on the PCA9555, analog AF-out, electret mic + 1 µF
- [x] **Audio path** (Sheet 4): 2:1 analog mux → PAM8302 class-D → speaker; the MCU is not in the audio path
- [ ] **Expansion:** 1× Grove I²C port (M5 I²C Units; Grove I²C hub for several at once)
- [ ] **Indicators + I/O:** WS2812 status LED, hardware TX-live envelope detectors (transmit chains only, 0 GPIO), buzzer, IR TX/RX, microSD

### 3. PCB layout

- [ ] **4-layer** board (JLCPCB JLC7628, impedance +-10%)
- [ ] **All RF on shielded u.FL modules** — this de-risks the first spin
- [ ] Impedance-controlled RF traces
- [ ] Placement: **antennas on top**, expander connectors on the sides or back
- [ ] Power and RF grounding; bulk caps placed right next to the nRF24 modules

### 4. First PCB spin

- [ ] Order the PCB (maker step)
- [ ] Solder and assemble (maker step)
- [ ] Bring-up: check power rails, C5 boot, and each bus
- [ ] **Honest expectation: 1 working spin + 1 refinement spin**

### 5. Firmware port (S3 -> C5)

- [ ] Port the leshy codebase from ESP32-S3 (Xtensa) to **ESP32-C5 (RISC-V)**
- [ ] Wi-Fi 2.4 + 5 GHz — 5 GHz is **Marauder-class** (scan, deauth, beacon / probe flood, sniff management frames)
- [ ] Drivers for each RF chain: 3x nRF24, CC1101, Si4732, SA868-U
- [ ] Per-region LoRa power caps: EU433 +10 dBm, EU868 +14 dBm, 869.4-869.65 MHz +27 dBm at 10% duty cycle, US915 +30 dBm with frequency hopping
- [ ] Onboard SX1262 LoRa driver, u-blox GPS (I²C NMEA), microSD PCAP logging, Grove units (RFID2 NFC, RTC, IMU / compass)
- [ ] BLE text entry (long text is typed on a phone in the Meshtastic app)

### 6. Antenna tuning (VNA)

- [ ] Tune each of the 8 onboard antennas with a **VNA** (manual maker step)

### 7. Field testing

- [ ] Runtime check (light about 9 h, active about 3.6 h, TX peaks about 2.5 h)
- [ ] Range check: SA868 voice (about 3-5 km open terrain), Meshtastic (city 2-5 km, line of sight 10-15 km)
- [ ] Real-world validation of every RF chain

## What is deliberately out of scope

- **5 GHz WPA handshake capture / injection / Pineapple-class.** That needs Linux, which we avoid on purpose to keep battery life. 5 GHz stays Marauder-class only.
- **Full-spectrum SDR voice listening.** The voice gaps at about 108-430 MHz and 480-860 MHz (airband AM 118-137, VHF/UHF NFM outside 433/446) would need an RTL-SDR plus a mini-Linux.
- **Wideband jamming.** It is illegal (US Communications Act section 333, EU RED).
- **27 MHz TX.** The Si4732 is receive-only.
- This is **not a HackRF** — no continuous 1 MHz-6 GHz coverage with arbitrary TX.

## How you can help

Leshy2 is built openly and credits ESP32-DIV; the aim is collaborative development with the DIV community. If you want to help with the schematic, the PCB, the firmware port, or testing, start with **[CONTRIBUTING](../CONTRIBUTING.md)**.
