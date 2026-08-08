# Leshy2 — GPIO budget by usage mode

*Read this in: **English** · [Русский](pin-budget.ru.md)*

The device runs **one radio mode at a time**. That splits its GPIO into three honest groups — pins used **every** mode, pins **reserved for radio** (wired to the radios, reused per mode), and the **I²C bus**. Add the optional 74HC138 and you have the whole budget. No hub; the per-antenna "on-air" LEDs are pure hardware (0 GPIO). The ESP32-C5 has about **19 usable GPIO**.

![GPIO budget tiers](img/pin-budget.svg)

## 1. Used in every mode

Lit no matter what you're doing.

| Line | Pins | Why |
|---|:--:|---|
| `Encoder A/B/SW` | 3 | navigation — turn (A/B) and press (SW) |
| `SPI SCK/MOSI/MISO` | 3 | shared data highway for every SPI radio and the SD card |
| `SD chip-select` | 1 | picks the SD card on that highway (PCAP logs, profiles) |
| **Subtotal** | **7** | + display |

**Display** adds **+1** (1-bit SPI: DC only, shares the bus) or **+5** (QSPI: its own 4-bit bus) → **SPI 8 / QSPI 12**.

## 2. Reserved for radio (reused per mode)

These GPIO are **soldered to the radios' control lines** (CS, CE, BUSY, DIO1, …). In menu they sit idle on the sleeping radios, but they **can't be used for anything else** — so they're reserved. The trick of "one radio at a time" is that the **same** pins serve different radios in different modes, so you reserve the **heaviest single mode**, not the sum of all radios.

| Mode | Use case | Uses from the radio pins | Pins |
|---|---|---|:--:|
| Menu / idle | browse menus, settings, status | — | 0 |
| WiFi 2.4/5 | scan / deauth / sniff (radio inside the C5) | — | 0 |
| 2.4 scan (nRF24×3) | 3 nRF24 sniff 2.4 GHz in parallel | 3× nRF24 CS | 3 |
| Mousejack (nRF24 TX) | inject on 2.4 GHz (one module TXes) | 3× CS + CE | 4 |
| Sub-GHz (CC1101) | capture/replay remotes; RSSI geiger | CS + GDO0 | 2 |
| Walkie (SA868) | listen/talk on 433/446 (PTT) | UART + PTT | 3 |
| LoRa + GPS | Meshtastic text + position — the peak | CS + BUSY + DIO1 + GPS-UART | 5 |
| Listen HF/FM (Si4732) | receive CB/HF/FM (AM/SSB) | RST (+ I²C bus) | 1 |
| Keys (RFID2) | read/emulate 13.56 MHz cards | — (I²C bus) | 0 |
| IR remotes | clone/replay IR remotes | IR TX + RX | 2 |
| | | **peak = LoRa + GPS** | **5** |

So this group reserves **5 pins** — not ~15 (the sum), because they're reused; and not fewer, because LoRa+GPS needs 5 at once.

## 3. The I²C bus

**2 pins.** SDA/SCL is a *bus* (pull-ups + Si4732 + RFID2 + Grove connectors on the same copper), so it **can't be reused** like the radio pins above — its 2 pins are held whenever you want **HF/CB/FM listening (Si4732), the RFID reader, or M5 Grove units**. Drop all three → drop the I²C bus.

## Optional: 74HC138 CS decoder — +1 pin

Turns 3 pins into 8 clean point-to-point chip-selects. Under "one mode at a time" it only helps the nRF24 mode; the pin peak (LoRa) has just 2 CS, so it costs **+1** overall. Without it, direct CS share nets across chips (a sleeping chip must release the line — a small first-spin SI risk). Keep for clean routing; drop for the pin.

## Totals

```
Used every mode (encoder+SPI+SD+display) .. SPI 8  / QSPI 12
Reserved for radio (peak = LoRa) .......... +5
I²C bus (listen / RFID / Grove) ........... +2
                                            = SPI 15 / QSPI 19
+ 74HC138 (optional, clean CS) ............ +1  = SPI 16 / QSPI 20
```

| Configuration | SPI | QSPI |
|---|:--:|:--:|
| radio only (no I²C, no 138) | 13 | 17 |
| + I²C (listen / RFID / Grove) | 15 | 19 |
| + I²C + 138 (everything) | 16 | 20 |

## The premium (QSPI) screen — yes, it fits

**QSPI with everything you'd actually use (listen, RFID, Grove, LoRa) = 19 → exactly the 19 ceiling.** The 74HC138 is the *only* thing that pushes it over (to 20). So the premium AMOLED is on the table — just **skip the optional 138** and wire chip-selects directly. No USB-pin reclaim needed. The one trade is direct CS on shared nets (careful routing).

## Switching modes — latency and no freezes

A switch = sleep the old radio → re-mux the reserved GPIO (µs) → start the new radio. The wait is startup; it never freezes the UI (radios wait on a timer, the CPU is free).

| Enter mode | From sleep | Feel |
|---|:--:|---|
| nRF24 / CC1101 / LoRa / WiFi | ≤5 ms | instant |
| Si4732 AM/FM | ~200 ms | brief "tuning…" |
| SA868 walkie | ~0.3–1 s | short spinner |
| Si4732 **SSB** (patch) | ~1.2 s | spinner + progress bar |

Firmware: non-blocking init on the single-core C5 (background task); keep **nRF24 warm**, **sleep CC1101 and Si4732** between uses; **pre-warm on menu focus**; SA868 mic cap **1 µF (not 10 µF)** cuts TX fade-in.

---
*Interactive version (click a mode) is in chat; GitHub renders the static page above.*
*Part of [Leshy2](../README.md) · MIT.*
