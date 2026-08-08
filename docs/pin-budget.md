# Leshy2 — GPIO budget by usage mode

*Read this in: **English** · [Русский](pin-budget.ru.md)*

Built bottom-up, the way it should be reviewed: a **hard core** that can't be cut, then the **radios** (one mode at a time, so they share a pool and only the peak counts), then **options** with an explicit price. No hub, no WS2812 line — the per-antenna "on-air" LEDs are **purely hardware** (an RF envelope detector each, 0 GPIO, dimmed by a resistor; they light on TX only, RX/scan is shown on the display). The ESP32-C5 has about **19 usable GPIO**.

![GPIO budget tiers](img/pin-budget.svg)

## Tier 0 — core (can't cut)

| Line | Pins | Why |
|---|:--:|---|
| `Encoder A/B/SW` | 3 | navigation — scroll and select in every mode |
| `SPI SCK/MOSI/MISO` | 3 | the bus every SPI radio and the SD card ride on |
| `SD chip-select` | 1 | microSD — PCAP logging and profiles, available in every mode |
| **Core total** | **7** | + display |

**Display** adds **+1** (1-bit SPI: DC only, shares the bus) or **+5** (QSPI: its own 4-bit bus). So the floor is **SPI 8 / QSPI 12**.

## Tier 1 — radios (per mode)

Every mode reuses the same physical pool (mode-exclusive), so only the **peak** mode counts. Chip-selects here are **direct** (no decoder). Modes marked ⓘ need the I²C option below.

### Menu / idle

**Use case.** Browse menus, settings, battery and status. No radio active.

*Adds nothing beyond the core.*

Radio pool: **0** pin(s).

### WiFi 2.4/5 (Marauder)

**Use case.** Scan APs/clients, deauth, beacon/probe flood, sniff mgmt frames. The radio is inside the C5 — no external pins.

*Adds nothing beyond the core.*

Radio pool: **0** pin(s).

### 2.4 scan (nRF24×3)

**Use case.** The three nRF24 sniff/scan across 2.4 GHz in parallel (RX). CE tied high, IRQ polled.

| Adds | Why |
|---|---|
| `nRF24 CS×3` (3) | one direct chip-select per module (they run together) |

Radio pool: **3** pin(s).

### Mousejack (nRF24 TX)

**Use case.** Inject on 2.4 GHz — one module transmits on the target channel while the others keep listening.

| Adds | Why |
|---|---|
| `nRF24 CS×3` (3) | chip-select per module |
| `CE` (1) | arm/TX on the injecting module |

Radio pool: **4** pin(s).

### Sub-GHz (CC1101)

**Use case.** Capture and replay OOK/FSK remotes and sensors; RSSI 'geiger'.

| Adds | Why |
|---|---|
| `CC1101 CS` (1) | chip-select |
| `GDO0` (1) | packet/data-ready interrupt |

Radio pool: **2** pin(s).

### Walkie (SA868)

**Use case.** Listen and talk on 433/446 MHz; PTT keys the transmitter; analog audio.

| Adds | Why |
|---|---|
| `UART TX/RX` (2) | control + channel/power to SA868 |
| `PTT` (1) | key the transmitter |

Radio pool: **3** pin(s).

### LoRa + GPS (Meshtastic)

**Use case.** Send/receive Meshtastic text and show position. This is the pin peak.

| Adds | Why |
|---|---|
| `LoRa CS` (1) | chip-select |
| `BUSY` (1) | wait line before each SPI op |
| `DIO1` (1) | RX/TX-done interrupt |
| `GPS TX/RX` (2) | NMEA serial to/from the GNSS |

Radio pool: **5** pin(s).

### Listen HF/FM (Si4732) ⓘ

**Use case.** Tune and listen to CB 27 MHz, HF/shortwave (AM/SSB) and FM broadcast.

| Adds | Why |
|---|---|
| `Si4732 RST` (1) | reset/boot the receiver |

Radio pool: **1** pin(s).

### Keys (RFID2) ⓘ

**Use case.** Read/emulate 13.56 MHz cards.

*Adds nothing beyond the core.*

Radio pool: **0** pin(s).

### IR remotes

**Use case.** Clone and replay IR remotes.

| Adds | Why |
|---|---|
| `IR TX` (1) | 38 kHz carrier out (RMT) |
| `IR RX` (1) | demodulated edges in |

Radio pool: **2** pin(s).

**Peak radio mode = LoRa + GPS (5).** Core + radios = **SPI 13 / QSPI 17**.

## Tier 2 — options (add with a price)

### I²C bus — +2 pins

SDA/SCL is a **shared bus** with pull-ups and devices on it (Si4732, RFID2, Grove connectors), so its two pins are physically committed — they **can't** double as anything else, even in modes that don't use it. It buys **HF/CB/FM listening (Si4732), the RFID reader, and the M5 Grove expansion**. Cut it → drop those three (the ⓘ modes above). Not "reserved for M5 in empty modes" — it's the receiver's control bus.

### 74HC138 CS decoder — +1 pin (optional)

Turns 3 pins into 8 clean point-to-point chip-selects. Under mode-exclusivity it only helps the nRF24 mode (4 CS) — the pin peak (LoRa) has just 2 CS — so it costs **+1** at the peak. Without it, direct CS share nets across chips (a sleeping chip must release MISO — a small SI risk on the first spin). Keep for clean routing, drop for the pin.

## Budget combinations

| Configuration | SPI | QSPI |
|---|:--:|:--:|
| Core + radios (no I²C, no 138) | 13 | 17 |
| + I²C (listen / keys / Grove) | 15 | 19 |
| + 74HC138 (clean CS) | 14 | 18 |
| + I²C + 138 (everything) | 16 | 20 |

Ceiling is 19. On **SPI** every combination fits. On **QSPI**: bare 17 and +138 18 fit; **+I²C lands exactly at 19**; everything (20) is over by 1 → needs the USB-pin reclaim (+2). The one unavoidable radio cost is the **I²C +2 for Si4732 listening** — it's a bus, it can't be shared. The 138 is the only true swing pin.

## Switching modes — latency and no freezes

A switch = sleep the old radio → re-mux shared GPIO (µs) → start the new radio. The wait is startup, and it never freezes the UI (radios wait on a timer; the CPU is free).

| Enter mode | From sleep | Feel |
|---|:--:|---|
| nRF24 / CC1101 / LoRa / WiFi | ≤5 ms | instant |
| Si4732 AM/FM | ~200 ms | brief "tuning…" |
| SA868 walkie | ~0.3–1 s | short spinner |
| Si4732 **SSB** (patch) | ~1.2 s | spinner + progress bar |

Firmware rules: non-blocking init on the single-core C5 (background task); keep **nRF24 warm**, **sleep CC1101 and Si4732** between uses (a warm Si4732 radiates its LO into SA868/CC1101); **pre-warm on menu focus** to hide the SSB second; SA868 mic-preamp cap **1 µF (not 10 µF)** cuts TX fade-in ~700 ms → ~70 ms.

---
*Interactive version (click a mode) is in chat; GitHub renders the static page above.*
*Part of [Leshy2](../README.md) · MIT.*
