# Leshy2 — Hardware

*Read this in: **English** · [Русский](hardware.ru.md)*

A hardware overview for **Leshy2** — an open-source portable multiband RF handheld (a "field tool"). It is the successor to [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy), a firmware fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV). Leshy2 is a **two-chip** design: a mature **ESP32-S3** brain that runs everything, plus an **ESP32-C5** co-processor bolted on for the one thing the S3 cannot do — native **5 GHz** Wi-Fi.

This page is the **map**, not the detail. Each subsystem has its own transcribe-ready sheet under [hardware/](../hardware/); the links point there.

> 📌 **Design stage. No hardware exists yet.** Architecture is locked (2026-08-10); the next step is capturing the sheets in KiCad. Pin maps are a proposed map, not yet confirmed against the datasheets. All onboard RF sits on shielded modules to de-risk the first PCB spin.

## Why two chips

esp32-leshy (and DIV before it) were single **ESP32-S3** builds. The S3 is a proven brain — two cores, native 2.4 GHz Wi-Fi + BLE, and enough I/O for the whole wired-radio stack — but it has **no 5 GHz radio**. Rather than throw that mature design away, Leshy2 keeps the S3 as the brain and adds the **ESP32-C5** — the only ESP32 with native 5 GHz — as a dedicated **co-processor**.

| MCU | Role | Radios | I/O |
|-----|------|--------|-----|
| **ESP32-S3-WROOM-1U-N8R2** (quad-PSRAM, dual-core) | **Main brain** — UI, display, all wired radios, SD, every bus | native 2.4 GHz Wi-Fi + BLE | **38 / 38** GPIO — full |
| **ESP32-C5-WROOM-1U** (single RISC-V) | **Co-processor** — 5 GHz recon offload | native **2.4 + 5 GHz** Wi-Fi, BLE, **802.15.4** (Zigbee / Thread) | ~11 / 20 GPIO |

The C5 is a **pure co-processor**: it owns only its own on-chip radios and never touches the shared bus. There is **no mode switch** — the S3 always owns the device. Quad-PSRAM on the S3 is deliberate: octal PSRAM would steal the GPIOs the C5 link needs. Details on [Sheet 2](../hardware/c5-buses/c5-buses.md).

## Buses

Everything digital hangs off the **S3** at 3.3 V. See [Sheet 2](../hardware/c5-buses/c5-buses.md) for the full pin map.

- **SPI2 (shared, FSPI @ 80 MHz)** — microSD, CC1101, 3× nRF24, SX1262 (LoRa) and the ST7796 display all ride one bus. Chip-selects come from a **74HC138** (3 GPIO → 8 CS) instead of one GPIO each. Only one radio is active at a time, so a radio and the display never fight for the bus. See [Sheet 3](../hardware/rf/rf.md) for the RF devices, [Sheet 6](../hardware/indicators/indicators.md) for the SD.
- **I²C** — Si4732 control, the **two PCA9555** expanders, the BQ25887 charger, and the Grove ports. **PCA9555 #1 (0x20)** carries radio + display slow control; **#2 (0x21)** carries PTT, the rail gates, the SP4T band select and the headphone-jack detect.
- **UART ×3** — SA868 walkie control (UART1), u-blox **GPS** (UART2), and **UART0** as the field flash bridge to the C5. See [Sheet 5](../hardware/expansion/expansion.md) for GPS.
- **S3 ↔ C5 link** — a dedicated **SPI3** plus a **DRDY** ready-strobe. The C5 is flashed by the S3 over UART0 (auto-OTA in the field) and has its own USB-C for brick-safe recovery on the bench.
- **Direct interrupts** — the four timing-critical lines stay on real GPIO, not the expanders: **LoRa DIO1**, the wired-OR **nRF24 IRQ** (through a 74AHC gate), **CC1101 GDO2** carrier-sense, and **CC1101 GDO0**.

## RF chains

Detail lives on the [RF sheet](../hardware/rf/rf.md) (data radios) and the [audio sheet](../hardware/audio/audio.md) (voice radios); this is the roster.

| Chain | Part | Band / use | Sheet |
|-------|------|-----------|:--:|
| 2.4 GHz raw | 3× nRF24L01+PA/LNA | parallel whole-band scan, mousejack, channel analyzer | [3](../hardware/rf/rf.md) |
| Sub-GHz | bare CC1101 + balun + **SP4T (PE42440)** + 4 matched nets | 315 / 433 / 868 / 915 MHz OOK/FSK capture & replay | [3](../hardware/rf/rf.md) |
| Long-range mesh | SX1262 / E22-900M22S, onboard | Meshtastic 868 / 915, +22 dBm | [3](../hardware/rf/rf.md) |
| HF / CB / FM | Si4732-A10 | **RX only**: CB 27 MHz, full HF/SW, MW/LW (AM/SSB/CW), FM 64–108 | [4](../hardware/audio/audio.md) |
| UHF voice | SA868-U | 433 / 446 MHz NBFM walkie, RX + TX up to 2 W (PTT) | [4](../hardware/audio/audio.md) |

Audio is **fully analog** — the MCU is not in the path. Si4732 / SA868 line-out → 2:1 analog mux → **PAM8302** class-D amp → speaker + headphone jack. See [Sheet 4](../hardware/audio/audio.md).

## Display

A **3.5″ ST7796 320×480 IPS TFT over SPI**, sharing the radio bus (CS via the 138, one DC line). It is **SPI, not 8080/AMOLED** — the C5 has no `LCD_CAM` peripheral, and keeping the panel on plain SPI keeps it on the S3's shared bus. The waterfall scrolls on the ST7796's **hardware vertical scroll**; the S3's quad-PSRAM holds the double-buffered framebuffer. See [Sheet 2](../hardware/c5-buses/c5-buses.md).

## Antennas (9)

Nine onboard antennas, **one per RF chain — there is no RF switch shared between chains**. The u-blox GPS carries its own antenna on the module, separate from these nine.

1. **ESP32-S3** — 2.4 GHz Wi-Fi + BLE (external SMA).
2. **ESP32-C5** — dual-band 2.4 / 5 GHz.
3–5. **nRF24 ×3** — 2.4 GHz.
6. **CC1101** — sub-GHz (the SP4T folds its own four bands onto this one antenna).
7. **Si4732** — telescopic whip for HF / CB (RX only; a ¼-wave at 27 MHz is ~2.75 m, so a 1–1.7 m telescopic is the plan).
8. **SA868-U** — 433 / 446 MHz UHF.
9. **SX1262** — 868 / 915 MHz LoRa.

## Power

**2S 2× 18650** (~7.4 V, ~18 Wh) with its own PMIC. A **BQ25887** boost charger takes plain 5 V USB to 8.4 V (no PD). Rails: **MP2315** +5 V, **TLV62569** +3V3, and a separate **TPS7A2033** +3V3A for the analog side (fed from +5 V, interlocked). A hard **master toggle** is the only on/off; rails are gated in idle. Two USB-C ports: **J1 → S3** (charge + data), **J2 → C5** (data-only). See [Sheet 1](../hardware/power/power.md).

## Indicators & I/O

Per-transmit-chain **hardware TX-live LEDs** (amber RF envelope detectors — honest "on air" even if firmware hangs, **0 GPIO**), one **WS2812** status LED, a buzzer, **IR** TX/RX, microSD, a rotary encoder, and the physical **RESET / BOOT / PTT** buttons. Receive-only chains (Si4732) get no LED. See [Sheet 6](../hardware/indicators/indicators.md).

## Expansion

M5-compatible for **I²C Grove Units** only (M5 Caps / Modules / HATs use other connectors and are not supported). **Two Grove HY2.0-4P ports** on the I²C bus (5 V power, 3.3 V signals), plus an onboard **RFID2** NFC unit (WS1850S, 0x28). Units are addressed individually. See [Sheet 5](../hardware/expansion/expansion.md).

## Honest ceilings

Deliberate limits, chosen with eyes open:

- **5 GHz is recon only** — scan, sniff, beacon/probe flood; deauth is a PoC question. No inject / handshake capture / monitor+inject (that needs Linux).
- **2.4 GHz deauth works** — on the S3.
- **HF / CB / FM is receive-only** (Si4732).
- **One radio at a time** — the shared SPI bus and single-antenna-per-chain design mean chains take turns.
- **Audio is mono.**
- **Not a HackRF** — no raw wideband capture and no arbitrary TX.
- **No wideband jamming** — it is illegal, and the hardware does not do it.

## Cost

Whole-build target BOM **~135–160 USD** (~108–125 USD in electronics). See the [cost breakdown](bom.md) and the [pin budget](pin-budget.md).

---

*Back to the [README](../README.md). License: [MIT](../LICENSE), same as upstream ESP32-DIV. Copyright © Anton Vinogradov ([anton-vinogradov](https://github.com/anton-vinogradov)).*
