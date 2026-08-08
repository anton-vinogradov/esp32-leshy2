# Leshy2 — GPIO budget by usage mode

*Read this in: **English** · [Русский](pin-budget.ru.md)*

Leshy2 runs **one radio mode at a time** and puts the inactive radios to sleep, so the radios share GPIO. This page is built bottom-up: a **minimal common set** that is always present, then each mode's **use case** and the lines it adds on top. The peak is the heaviest single mode, not the sum. The ESP32-C5 has about **19 usable GPIO** (after flash/PSRAM and USB).

**No I²C hub in the baseline.** We look without it first; the hub section at the bottom shows why it can't help our peak anyway.

![GPIO budget by mode](img/pin-budget.svg)

## Minimal common — always present

The set that exists in **every** mode, regardless of what radio is active.

| Line | Pins | Why it's always there |
|---|:--:|---|
| `Encoder A/B/SW` | 3 | navigation — you scroll and select in every mode |
| `WS2812` | 1 | per-antenna status LEDs |
| `SPI SCK/MOSI/MISO` | 3 | bus to microSD + the active SPI radio |
| `74HC138 A/B/C` | 3 | decodes all chip-selects (SD + radios), 1-of-8, no latency — logic, not the I²C hub |
| `I²C SDA/SCL` | 2 | reserved bus for Si4732 (Listen) and RFID2 (Keys); dedicated, can't be reused |
| **Common total** | **12** | + display |

**Display** adds **+1** (1-bit SPI: DC only, shares the SPI bus, CS via the 138) or **+5** (QSPI: its own 4-bit bus).

So the always-on floor is **SPI 13 / QSPI 17** pins — buttons, status LED, the two buses, the CS decoder, and the screen.

## Per usage mode — what it does, what it adds

Every mode reuses the same physical pool of GPIO (mode-exclusive), so only the **peak** mode counts.

### Menu / idle

**Use case.** Browse menus, settings, battery and status. No radio is active.

*Adds nothing — common set only.*

Pins: **SPI 13 / QSPI 17** (of 19)

### WiFi 2.4/5 (Marauder)

**Use case.** Scan APs/clients, deauth, beacon/probe flood, sniff management frames. The 2.4/5 GHz radio is inside the C5 — no external pins.

*Adds nothing — common set only.*

Pins: **SPI 13 / QSPI 17** (of 19)

### 2.4 scan (nRF24×3)

**Use case.** The three nRF24 sniff/scan across 2.4 GHz in parallel (RX). CE is tied high, IRQ is polled, CS goes through the 138.

*Adds nothing — common set only.*

Pins: **SPI 13 / QSPI 17** (of 19)

### Mousejack (nRF24 TX)

**Use case.** Inject on 2.4 GHz — one module transmits on the target's channel while the others keep listening.

| Adds | Why |
|---|---|
| `CE` (1) | arm/TX on the injecting module |

Pins: **SPI 14 / QSPI 18** (of 19) ⚠️

### Sub-GHz (CC1101)

**Use case.** Capture and replay OOK/FSK remotes and sensors; RSSI 'geiger'.

| Adds | Why |
|---|---|
| `GDO0` (1) | packet / data-ready interrupt from CC1101 |

Pins: **SPI 14 / QSPI 18** (of 19) ⚠️

### Walkie (SA868)

**Use case.** Listen and talk on 433/446 MHz like a Baofeng; PTT keys the transmitter; analog audio.

| Adds | Why |
|---|---|
| `UART TX/RX` (2) | control + channel/power to SA868 |
| `PTT` (1) | key the transmitter |

Pins: **SPI 16 / QSPI 20** (of 19) ❌

### LoRa + GPS (Meshtastic)

**Use case.** Send/receive Meshtastic text and show position.

| Adds | Why |
|---|---|
| `BUSY` (1) | wait line before each SX1262 SPI op |
| `DIO1` (1) | RX/TX-done interrupt |
| `GPS TX/RX` (2) | NMEA serial to/from the GNSS |

Pins: **SPI 17 / QSPI 21** (of 19) ❌

### Listen HF/FM (Si4732)

**Use case.** Tune and listen to CB 27 MHz, HF/shortwave (AM/SSB) and FM broadcast.

| Adds | Why |
|---|---|
| `Si4732 RST` (1) | reset/boot the receiver (its I²C is already in the common set) |

Pins: **SPI 14 / QSPI 18** (of 19) ⚠️

### Keys (RFID2)

**Use case.** Read/emulate 13.56 MHz cards. RFID2 sits on the common I²C bus — no extra pins.

*Adds nothing — common set only.*

Pins: **SPI 13 / QSPI 17** (of 19)

### IR remotes

**Use case.** Clone and replay IR remotes.

| Adds | Why |
|---|---|
| `IR TX` (1) | 38 kHz carrier out (RMT) to the IR LED |
| `IR RX` (1) | demodulated edges from the IR receiver |

Pins: **SPI 15 / QSPI 19** (of 19) ⚠️

## Aggregate

The heaviest mode is **LoRa + GPS** (pool 4). So the whole device needs:

- **1-bit SPI display: 17 / 19** — fits, ~2 to spare.
- **QSPI display: 21 / 19** — over by 2.

So on SPI everything fits with no hub and no cuts. QSPI overflows and needs the USB-pin reclaim (don't wire USB data → +2 GPIO, first-flash over a UART pad + OTA).

## The hub question

We deliberately started **without** an I²C GPIO hub (PCA9555). Does it help if we overflow?

**It's pin-neutral, and it can't fix our overflow.** Two reasons:

1. The hub only carries **slow, set-and-forget** signals (buttons, enables). But our overflowing mode — LoRa + GPS — is **all timing-critical**: `BUSY`, `DIO1` and the GPS `UART` must be on real GPIO. The hub physically cannot take them, so it doesn't lower the peak.

2. Buttons already sit on the encoder (direct, instant). Moving them to the hub would just add a chip plus I²C read-latency on every press, for zero pin saving.

So the hub is dropped. It would only earn its place if we wanted a **large keypad** (8+ buttons) — we don't.

## Switching modes — latency and no freezes

A mode switch = sleep the old radio → re-mux the shared GPIO (µs) → start the new radio. The wait is the new radio's startup, and it never has to freeze the UI (radios wait on a timer; the CPU is free).

| Enter mode | From sleep | Feel |
|---|:--:|---|
| nRF24 / CC1101 / LoRa / WiFi | ≤5 ms | instant |
| Si4732 AM/FM | ~200 ms | brief "tuning…" |
| SA868 walkie | ~0.3–1 s | short spinner |
| Si4732 **SSB** (patch load) | ~1.2 s | spinner + progress bar |

**Rules baked into the firmware plan:**

- Non-blocking switch on the single-core C5: slow init runs in a background task / chunked with yield; the encoder and screen stay live.
- Warm vs sleep: keep **nRF24 warm** (Standby-I ~26 µA, no LO leak); **sleep CC1101 and Si4732** between uses (a warm Si4732 radiates its LO into SA868/CC1101); SX1262 warm is optional.
- **Pre-warm on menu focus:** when the cursor lands on a slow mode, start its init in the background so it's ready on select — hides the SSB second and the SA868 boot.
- HW: SA868 mic-preamp coupling cap **1 µF (not 10 µF)** cuts TX fade-in ~700 ms → ~70 ms; run Si4732 I²C at 400 kHz to roughly halve the SSB patch load.

---
*Interactive version (click a mode) is available in chat; GitHub renders the static page above.*
*Part of [Leshy2](../README.md) · MIT.*
