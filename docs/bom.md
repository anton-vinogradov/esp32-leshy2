# Leshy2 — Bill of materials & cost

*Read this in: **English** · [Русский](bom.ru.md)*

What the device is made of, and what it costs. Prices are **approximate single-unit** figures for a hand-built prototype (design stage — nothing is ordered yet), grouped by the six schematic sheets. They are a planning estimate, not a quote; at volume most lines drop.

> **Bottom line:** electronics ≈ **$105**, whole build (with PCB + enclosure) ≈ **$120–150** — inside the original target.

## Cost by subsystem

| Sheet | Subsystem | ≈ USD |
|------|-----------|:----:|
| 1 | [Power](../hardware/power/power.md) | 23 |
| 2 | [ESP32-C5 + buses](../hardware/c5-buses/c5-buses.md) | 9 |
| 3 | [RF chains](../hardware/rf/rf.md) | 28 |
| 4 | [Audio](../hardware/audio/audio.md) | 21 |
| 5 | [Expansion + GPS](../hardware/expansion/expansion.md) | 16 |
| 6 | [Indicators / IO](../hardware/indicators/indicators.md) | 7 |
| — | **Electronics total** | **≈ 104** |
| — | 4-layer PCB (JLC7628, small run) | 5–10 |
| — | Enclosure, connectors, hardware | 10–20 |
| — | **Whole build** | **≈ 120–150** |

## What it's made of

### 1 · Power — ≈ $23
| Part | Role | ≈ $ |
|------|------|:--:|
| 2× 18650 cells (2S) | pack, ~7.4 V / ~18 Wh | 10 |
| BQ25887 | 2S boost charger (5 V→8.4 V, I²C, ADC gauge) | 3.5 |
| S-8252A + dual FET | 2S protection | 1 |
| MP2315 · TLV62569 · TPS7A2033 | +5V / +3V3 bucks + +3V3A LDO | 3 |
| Master switch, PPTC, NTC, USB-C, inductors, passives | rails, input, protection | 5.5 |

### 2 · ESP32-C5 + buses — ≈ $9
| Part | Role | ≈ $ |
|------|------|:--:|
| ESP32-C5-WROOM-1U (PSRAM) | brain, native 2.4 **+ 5 GHz** Wi-Fi + BLE | 5 |
| 74HC138 · PCA9555 | CS decoder · I²C slow-line expander | 1.3 |
| Rotary encoder + RESET/BOOT buttons | input | 1.7 |
| Decoupling, passives | — | 1 |

### 3 · RF chains — ≈ $28
| Part | Role | ≈ $ |
|------|------|:--:|
| 3× nRF24L01+PA/LNA | 2.4 GHz raw | 6 |
| CC1101 + per-band matching + PE4259 switch | sub-GHz 300–928 | 4 |
| SX1262 (E22-900M22S, +22 dBm) | LoRa / Meshtastic | 7 |
| 5 antennas (3× 2.4, sub-GHz, LoRa) + u.FL/SMA | RF I/O | 10 |
| brownout caps, T/R inverter | — | 1 |

### 4 · Audio — ≈ $21
| Part | Role | ≈ $ |
|------|------|:--:|
| SA868-U (2 W) | 433/446 voice walkie (RX+TX) | 10 |
| Si4732 | HF/CB/FM receiver | 2.5 |
| PAM8302 · 74LVC1G3157 · mic · speaker | amp · 2:1 mux · TX mic · speaker | 3.3 |
| HF whip + UHF antenna + SMA | RF I/O | 5 |
| 32.768 kHz crystal, passives | — | 0.7 |

### 5 · Expansion + GPS — ≈ $16
| Part | Role | ≈ $ |
|------|------|:--:|
| u-blox SAM-M8Q (I²C, integrated antenna) | onboard GPS | 14 |
| supercap + Schottky, Grove HY2.0, ESD | GPS hot-start, one I²C port | 2 |

### 6 · Indicators / IO — ≈ $7
| Part | Role | ≈ $ |
|------|------|:--:|
| 7× amber LED + envelope detectors | hardware TX-live per chain | 4 |
| WS2812 + 74AHCT1G125 level shifter | status LED | 0.5 |
| active buzzer + transistor | alerts | 0.5 |
| IR LED + TSOP38238 + transistor | IR clone/replay | 1.2 |
| microSD socket | PCAP logging | 1 |

## Biggest cost drivers

Five parts are ~60 % of the electronics cost — worth knowing where the money goes:

1. **u-blox GPS (~$14)** — the I²C-native module is a premium over a cheap UART GPS; it's what keeps the pin budget clean ([why](pin-budget.md)).
2. **SA868-U walkie (~$10)** — the only 2 W voice transceiver here.
3. **2× 18650 cells (~$10)** — quality cells; generic ones are cheaper.
4. **Antennas (~$15 total across both RF sheets)** — 8 chains, each its own tuned antenna.
5. **SX1262 LoRa module (~$7)**.

## Honest caveats

- **Approximate.** Individual part prices are not pinned at the design stage; treat every figure as ±30 %.
- **Single-unit.** These are hobby-quantity prices; the modules (nRF24, CC1101, SX1262, GPS) drop noticeably at volume.
- **Not counted:** solder, wire, test gear, the VNA time to tune 8 antennas, and your labour.
- **Enclosure varies most** — a 3D print is near-free; a machined case is not.

---

*Part of [Leshy2](../README.md) · MIT. Per-part detail lives in each [schematic sheet](../hardware).*
