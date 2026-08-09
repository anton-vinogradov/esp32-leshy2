# Leshy2 — RF chains sheet (Sheet 3)

*Read this in: **English** · [Русский](rf.ru.md)*

The data radios that hang off the shared SPI bus: **3× nRF24L01+PA/LNA** (2.4 GHz raw), **CC1101** (sub-GHz 300–928), and the onboard **SX1262** (LoRa / Meshtastic 868–915). Each is a shielded u.FL module, each with its own antenna and its own chip-select from the 74HC138. Control-line pins come from [Sheet 2](../c5-buses/c5-buses.md). The audio radios (Si4732, SA868) are on the audio sheet, not here.

> ⚠️ Design stage. All RF sits on shielded u.FL modules to de-risk the first PCB spin; the board only carries power, decoupling, chip-selects and antenna traces to each module. Antenna matching is tuned by hand on real hardware (VNA).

## Chains and parts

| Ref | Module | Band | Role | Interface |
|-----|--------|------|------|-----------|
| U20–U22 | 3× **nRF24L01+PA/LNA** (u.FL) | 2.4 GHz | parallel band scan, mousejack, channel analyzer | SPI + CSN (138) + shared CE + IRQ (polled) |
| U23 | **CC1101** (Ebyte E07-900M10S, u.FL) | 300–928 MHz | capture/replay OOK-FSK, RSSI "geiger" | SPI + CS (138) + GDO0 |
| U24 | **SX1262** (Ebyte E22-900M22S, +22 dBm, u.FL) | 868 / 915 MHz | Meshtastic text mesh | SPI + NSS (138) + BUSY + DIO1 (polled) + NRESET |
| U25 (opt.) | RF switch (PE4259 / BGS12) | — | fold CC1101's sub-bands onto one SMA | 1–2 control lines via PCA9555 |

All logic runs on **`+3V3`**. Because only one radio is selected at a time (74HC138), the four chains share the SPI bus without contention.

## Nets

```
SPI      : SCK(23) · MOSI(24) · MISO(6)  →  U20 U21 U22 U23 U24   (shared)
CS (138) : Y1 → U23 CC1101_CS
           Y2/Y3/Y4 → U20/U21/U22 nRF24 CSN
           Y5 → U24 SX1262 NSS
nRF24 CE : GPIO26 → CE of U20, U21, U22 (tied)         ; IRQ → polled (STATUS reg)
CC1101   : GDO0 → GPIO8 (RMT: raw OOK data / RSSI)      ; GDO2 unused
SX1262   : BUSY → GPIO9 ; DIO1 → polled (GetIrqStatus) ; NRESET → PCA9555.P0.4
           DIO2 = internal RX/TX antenna switch (inside the E22 module)
POWER    : +3V3 to all ; 100–220 µF + 100 nF at each nRF24 VCC (brownout) ;
           bulk 47–100 µF at CC1101 and SX1262 PA
ANT      : ANT_nRF24_1/2/3 (2.4) · ANT_CC1101 (sub-GHz) · ANT_LoRa (868/915)
           each u.FL pigtail → top-mounted SMA ; separate antenna per chain (no shared switch)
```

## nRF24 ×3 — the brownout rule

The PA/LNA modules pull **pulsed** current on TX (~115 mA bursts) and will sag their own and neighbours' supply. Each of U20/U21/U22 gets **100–220 µF bulk + 100 nF right at its VCC pin** on `+3V3`. Keep the three modules' grounds short and stitched. CE is tied across all three: in scan mode all three receive in parallel; in mousejack the one configured for TX transmits while the others stay RX — only its CSN is addressed for the FIFO writes.

## CC1101 — one SMA for several bands (optional)

The CC1101 covers 315 / 433 / 868 / 915 with different matching networks. An optional **RF switch (U25)** folds those onto a single SMA — the trick borrowed from the M5 Cap CC1101. This is **within one chain**, not shared across chains, and its 1–2 select lines are slow, so they ride the **PCA9555**. Without the switch, pick one matched band or bring out separate matched taps.

## SX1262 (LoRa) — onboard module

The **E22-900M22S** carries the SX1262, its PA to **+22 dBm**, the TCXO, the RX/TX switch (driven by the chip's DIO2, internal to the module) and the matching — so the board only wires SPI + NSS + BUSY + NRESET and the u.FL. `DIO1` (TX/RX-done) is **polled** over SPI to save a pin. Per-region legal power caps are enforced in firmware, not in this sheet.

## Antennas

Five of the eight onboard antennas live here: **3× 2.4 GHz** (nRF24), **1 sub-GHz** (CC1101), **1 LoRa** (SX1262). Each chain keeps its **own** antenna — there is no RF switch shared between chains. All are u.FL pigtails to top-mounted SMA connectors, tuned by hand with a VNA.

## Gotchas

- **Only one CS low at a time.** The 74HC138 guarantees a single selected radio; the firmware parks the address on Y7 before switching. Two radios never drive MISO together.
- **CE is shared, CSN is not.** Independent addressing is via CSN (the 138); the tied CE only gates RX/TX enable, which suits parallel-scan and single-TX modes.
- **Keep PA supplies stiff.** nRF24 brownout caps are mandatory; CC1101/SX1262 PA want local bulk too. A sagging PA rail shows up as range loss and packet errors, not as an obvious failure.
- **Shared SPI clock ceiling.** The bus clock must suit the slowest device on it (nRF24 ≤ 10 MHz in some clones); set per-CS clock in firmware, or the display (fast) and nRF24 (slow) will fight the common rate.

---

*Next sheets: (4) audio (Si4732 + SA868 + PAM8302), (5) expansion, (6) indicators/IO. Previous: (2) [C5 + buses](../c5-buses/c5-buses.md).*
*Part of [Leshy2](../../README.md) · MIT.*
