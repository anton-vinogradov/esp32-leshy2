# Leshy2 — Bill of materials & cost

*Read this in: **English** · [Русский](bom.ru.md)*

What the device is made of, and what it costs. Prices are **approximate single-unit** figures for a hand-built prototype (design stage — nothing is ordered yet). They are a planning estimate, not a quote; at volume most lines drop.

Leshy2 is priced as a **platform + capabilities**, not one flat parts list:

- **Platform** — what is always on the board: the two brains, the display, power, buses, and the onboard I/O. Buy this and you already have a **2.4 GHz Wi-Fi + BLE** tool (native on the ESP32-S3), a screen, and an SD logger. Nothing extra needed.
- **Capabilities** — each radio you add costs what it costs. Want a walkie? Add ~$13. Want 5 GHz recon? Add the ESP32-C5 (~$7). Skip what you don't want and the price drops with it.

> **Bottom line:** electronics ≈ **$108–125**, whole build (with PCB + enclosure) ≈ **$135–160**. Two chips, nine antennas, every RF chain built from bare silicon.

## Cost at a glance

| Block | ≈ USD |
|------|:----:|
| **Platform** (S3 + C5-link glue + display + power + buses + onboard I/O) | ≈ 47 |
| **Capabilities** (every radio, GPS, audio) | ≈ 61 |
| **Electronics total** | **≈ 108** |
| 4-layer PCB (small run, two RF sections) | 8–15 |
| Enclosure, connectors, antennas hardware | 15–25 |
| **Whole build** | **≈ 135–160** |

## Platform — ≈ $47

Always present. This is the tool you get before adding a single extra radio.

| Part | Role | ≈ $ |
|------|------|:--:|
| ESP32-S3-WROOM-1U-N8R2 | **main brain** — UI, display, all wired radios, SD, buses; native **2.4 GHz Wi-Fi + BLE**; 38/38 pins | 4 |
| ST7796 4.0″ IPS TFT (320×480, SPI) | color display + hardware-scroll waterfall | 9 |
| Power (sheet 1) | 2S 2×18650, BQ25887 boost-charge, S-8252A, MP2315/TLV62569/TPS7A2033 rails, master switch | 23 |
| 2× PCA9555 · 74HC138 · 74AHC1G gate | slow-line expanders (0x20/0x21) · CS decoder · nRF24-IRQ gate | 1.3 |
| microSD · RESET/BOOT/PTT buttons · encoder · WS2812 · buzzer · amber TX LEDs | onboard I/O + PCAP log + honest "on-air" LEDs | 9 |
| 2× USB-C · S3 2.4 GHz SMA antenna · passives | J1→S3 (charge+data), J2→C5 (data-only) | 1 |

The external **SMA** antenna on the S3 (not a chip antenna) is what lets the 2.4 GHz Wi-Fi front-end actually reach. That is the free-with-platform radio.

## Capabilities — ≈ $61

Add only what you need. Each line is a self-contained radio (module + its own tuned antenna).

| Capability | Parts | ≈ $ |
|------|------|:--:|
| **5 GHz recon** | ESP32-C5-WROOM-1U coprocessor (the only ESP32 with native 5 GHz) + dual 2.4/5 antenna; SPI3 + DRDY link to S3 | 7 |
| **Walkie (voice TX/RX)** | SA868-U 2 W 433/446 NBFM + UHF antenna | 13 |
| **2.4 GHz raw** | 3× nRF24L01+PA/LNA + 3 antennas — parallel band scan, mousejack | 10 |
| **LoRa / Meshtastic** | SX1262 (E22-900M22S, +22 dBm) + antenna | 9 |
| **Sub-GHz 315/433/868/915** | CC1101 (bare + xtal + balun) + SP4T PE42440 + 4 matching networks + antenna | 8 |
| **GPS** | u-blox module over UART, onboard + antenna | 6 |
| **HF/CB/FM listen + audio** | Si4732-A10 (RX only) + PAM8302 amp + speaker + headphone jack + telescopic whip | 8 |
| **GPIO45 de-strap** | eFuse `set_flash_voltage 3.3V` — frees the pin for CC1101 carrier-sense | 0 |

The **GPS is now a plain UART module (~$6)** — half the old I²C u-blox (~$14). The pin budget is locked without it, so the premium part is gone.

The **eFuse step is $0 in parts** — it is a one-time factory burn, not a component. It buys back a pin (GPIO45) for the CC1101 GDO2 carrier-sense interrupt.

## Biggest cost drivers

A handful of lines are most of the electronics cost — worth knowing where the money goes:

1. **Power (~$23)** — cells + 2S boost-charger + three rails. Quality 18650s alone are ~$10.
2. **Walkie SA868-U (~$13)** — the only 2 W voice transceiver here.
3. **3× nRF24L01+PA/LNA (~$10)** — three modules for parallel 2.4 GHz coverage.
4. **Display ST7796 (~$9)** — the 4.0″ IPS panel. *(This line was missing from the earlier single-chip BOM — it is now counted.)*
5. **LoRa SX1262 (~$9)** and **ESP32-C5 (~$7)** — the mesh radio and the 5 GHz coprocessor.

## Honest caveats

- **Approximate.** Individual part prices are not pinned at the design stage; treat every figure as ±30 %.
- **Single-unit.** These are hobby-quantity prices; the modules (nRF24, CC1101, SX1262, SA868, C5) drop noticeably at volume.
- **Two chips, bigger board.** Two RF sections and a link bus mean a larger 4-layer PCB than the old single-chip estimate.
- **Not counted:** solder, wire, test gear, the VNA time to tune nine antennas, and your labour.
- **Enclosure varies most** — a 3D print is near-free; a machined case is not.

---

*Part of [Leshy2](../README.md) · MIT. Per-part detail lives in each [schematic sheet](../hardware).*
