# Leshy2 — RF chains sheet (Sheet 3)

*Read this in: **English** · [Русский](rf.ru.md)*

The data radios that hang off the shared **SPI2** bus and two of the three PCA9555 expanders: **3× nRF24L01+PA/LNA** (2.4 GHz raw), a **bare CC1101** (sub-GHz 300–928, switched across four matched bands), and the onboard **SX1262 / E22-900M22S** (LoRa / Meshtastic 868–915). Every device shares the S3's FSPI bus and takes its chip-select from the 74HC138; slow control (resets, band-switch, T/R) rides the expanders. Pin assignments come from [Sheet 2](../c5-buses/c5-buses.md). The audio radios (Si4732, SA868) are on the [audio sheet](../audio/audio.md), not here.

> ⚠️ Design stage. The nRF24 and SX1262 are shielded modules with their own antennas; the CC1101 is a **bare IC on-board** (crystal + balun + per-band matching + SP4T). Antenna matching is tuned by hand on real hardware (VNA).

## Chains and parts

| Ref | Device | Band | Role | Interface |
|-----|--------|------|------|-----------|
| U20–U22 | 3× **nRF24L01+PA/LNA** module | 2.4 GHz | parallel band scan, mousejack, channel analyzer | SPI + CSN (138 Y2/Y3/Y4) + shared `CE` + `IRQ` (gated → GPIO46) |
| U23 | **CC1101** bare IC + 26 MHz xtal + balun | 300–928 MHz | capture/replay OOK-FSK, RSSI "geiger", carrier-sense wake | SPI + CS (138 Y1) + `GDO0` (GPIO7 RMT) + `GDO2` (GPIO45) |
| U24 | RF switch **SKY13414-485LF** (SP4T) + 4× matched networks | 315/433/868/915 | fold four sub-GHz bands onto one CC1101 antenna | `RFSW_A/B/C` (V1/V2/V3, PCA9555) |
| U25 | **SX1262** / Ebyte **E22-900M22S**, +22 dBm | 868 / 915 MHz | Meshtastic text mesh | SPI + NSS (138 Y5) + `BUSY` (poll) + `DIO1` (IRQ) + `NRESET` + `RXEN/TXEN` |

All logic runs on **`+3V3`**. Only one device drives `MISO` at a time (74HC138 asserts a single CS), so the four chains share SPI2 without contention.

## Key nets

```
SPI2     : MOSI(GPIO11) · SCK(GPIO12) · MISO(GPIO13)  →  U20 U21 U22 U23 U25  (shared, FSPI 80 MHz)
CS (138) : Y1 → CC1101_CS   ·   Y2/Y3/Y4 → nRF24_1/2/3 CSN   ·   Y5 → LoRa_NSS
nRF24 CE : GPIO6  → CE of U20/U21/U22 (tied)
nRF24 IRQ: 3× push-pull → SN74LVC1G10 3-input NAND (idle-LOW) → GPIO46 (interrupt)
CC1101   : GDO0 → GPIO7  (RMT: raw OOK RX / replay)
           GDO2 → GPIO45 (carrier-sense / wake-on-sub-GHz)
           band : SKY13414 SP4T ← RFSW_A/RFSW_B/RFSW_C (V1/V2/V3; PCA#1 P1.5, PCA#2 P0.4, PCA#2 P07) → 315/433/868/915
SX1262   : BUSY → GPIO15 (polled before each command)
           DIO1 → GPIO3  (RxDone/TxDone/timeout interrupt)
           NRESET ← PCA#1 P0.4
           RXEN/TXEN ← LoRa_TR (PCA#1 P1.2) + 74LVC1G04 inverter (complementary T/R)
POWER    : +3V3 to all ; 100–220 µF + 100 nF at each nRF24 VCC (brownout) ;
           bulk 47–100 µF at CC1101 and at the E22 PA
ANT      : ANT_nRF24_1/2/3 (2.4) · ANT_CC1101 (sub-GHz, via SP4T) · ANT_LoRa (868/915)
           external SMA per chain ; no RF switch shared between chains
```

## nRF24 ×3 — the brownout rule

The PA/LNA modules pull **pulsed** current on TX (~115 mA bursts) and will sag their own and their neighbours' supply. Each of U20/U21/U22 gets **100–220 µF bulk + 100 nF right at its VCC pin** on `+3V3`; keep the three grounds short and stitched. `CE` is **tied across all three** (timing-critical, so a direct S3 pin, GPIO6): in scan mode all three receive in parallel; in mousejack the one configured for TX transmits while the others stay RX — only its CSN is addressed for the FIFO writes.

The three `IRQ` lines are **push-pull** (active-low), so they cannot simply wire-OR. They are combined by a **SN74LVC1G10 3-input NAND** into one signal that is **idle-LOW** — which both gives the S3 a single interrupt on GPIO46 and satisfies that pin's boot strap (GPIO46 must be low at POR). Firmware reads each radio's STATUS register to find which one fired.

## CC1101 — bare IC, four bands on one antenna

The CC1101 tunes 300–928 MHz, but a single matching network only covers one band. To reach the sub-GHz bands remotes and sensors actually use (**315 / 433 / 868 / 915**), the chain is a **bare CC1101 IC + a 26 MHz crystal (with load caps) + an RF balun on RF_P/RF_N + one matched network per band + an SP4T RF switch (SKY13414-485LF)** that folds all four onto a single antenna — the multiband trick borrowed from the M5 Cap CC1101, taken to a 4-way switch. The three select lines `RFSW_A` / `RFSW_B` / `RFSW_C` are slow, so they ride the **PCA9555** expanders (PCA #1 P1.5, PCA #2 P0.4, PCA #2 P0.7). `GDO0` carries raw OOK data / replay on an S3 **RMT** pin (GPIO7); `GDO2` is programmed as **carrier-sense** and wired to GPIO45 as a wake / "sub-GHz geiger" interrupt. (A single-band Ebyte module like E07-433M would be simpler but drops the other three bands — not chosen, since 315/433/868/915 all matter.)

## SX1262 (LoRa) — onboard E22 module

The **E22-900M22S** carries the SX1262, an external **PA/LNA to +22 dBm**, the TCXO and the matching. Its T/R front-end is **not** switched by DIO2 alone — the module brings out **RXEN** and **TXEN** on the header, and both must be driven or the receiver is deaf and TX never reaches the antenna. We drive them **complementarily from one PCA9555 line** (`LoRa_TR`, PCA#1 P1.2) through a **74LVC1G04** inverter: TX asserts TXEN and drops RXEN, RX the reverse. Mesh is half-duplex, so the I²C-paced switch is fast enough. The board wires SPI + NSS (Y5) + BUSY + NRESET + RXEN/TXEN + antenna; runs on **`+3V3`** (not +5V). Unlike Sheet-2's earlier polled scheme, `DIO1` is a **real interrupt** (GPIO3) so LoRa RX is event-driven; `BUSY` (GPIO15) stays **polled** before each command; per-region power caps are in firmware.

**Deep-idle catch.** A single inverter makes RXEN/TXEN *complementary* — one is always high, so the E22's LNA/PA bias is never fully zeroed. Put the SX1262 to sleep with an SPI command; a few mA of LNA bias remain because the E22 sits on the **non-gated `+3V3`** (there is no rail to drop, and `RAIL_EN_3V3A` feeds only Si4732/audio, not the E22). Truly powering the E22 down would need a gated E22 rail or a second T/R line — not wired. In normal use the module simply sits in RX.

## Antennas

Five of the nine onboard antennas live here: **3× 2.4 GHz** (nRF24), **1 sub-GHz** (CC1101, fed through the SP4T), **1 LoRa** (SX1262). Each chain keeps its **own** antenna — there is **no RF switch shared between chains** (the SP4T only multiplexes CC1101's four *band matches* onto CC1101's single antenna).

**Mounting: u.FL → pigtail → panel SMA, not board-edge SMA.** Six of the nine radios are u.FL/IPEX modules (S3, C5, 3× nRF24, E22 LoRa); their ports run by short coax pigtail to bulkhead SMA on the enclosure panel, in two staggered rows. CC1101 (bare) and SA868 take a u.FL there too; Si4732 is a fold-out telescopic whip. Nine end-launch SMA will not fit an 80 mm edge (they need 72–90 mm), and pigtails let the antennas spread to opposite corners for isolation — the 2 W SA868 and the 2.4 GHz cluster at one end, Si4732 / GPS and the 2.4/5 GHz scan RX at the other. All matching is tuned by hand on a VNA.

**RF coexistence (the real isolation levers, all on one board).** With nine radiators in one shell, over-the-air antenna-to-antenna coupling (~10–25 dB) dominates — splitting the design across boards would not change it. Isolation is bought instead by: **TDD arbitration in firmware** (never receive on Si4732 / GPS while the SA868 keys — its +33 dBm through ~20 dB of coupling is +13 dBm at a neighbour's port, enough to block or damage a front-end); a **PIN-diode limiter + RX blanking on the Si4732 HF input**; **shield cans at source** (30–60 dB) over the aggressive PA sections; a continuous 4-layer ground plane; and separate LC-filtered feeds with a star-point return for the PA rails.

## Fab realization (real parts)

`hardware/tscircuit/rf.tsx` is fab-drafted: real footprints/pinouts are engine-pulled
from LCSC by part number. KiCad DRC = **0 unconnected / 0 shorts / 0 schematic-parity**.

| Ref | Part | LCSC | Note |
|-----|------|------|------|
| U23 | CC1101RGPR (QFN-20) | C29953 | bare IC |
| U25 | E22-900M22S (SX1262) | C411293 | module footprint |
| U27 | SN74LVC1G04 inverter (T/R) | C7827 | |
| U28 | SN74LVC1G10 3-input NAND (IRQ combiner) | C485078 | |
| U20–U22 | nRF24L01+PA/LNA module | — | 2×4 header placeholder |
| U24 | SP4T SKY13414-485LF | C255353 | 3-line V1/V2/V3 |

Realized per datasheet: the CC1101 gains its bare-IC support (all AVDD/DVDD → `+3V3`,
`DGUARD` → `+3V3`, `DCOUPL` 100 nF → GND, `RBIAS` 56 kΩ 1 % → GND, EP → GND). The nRF24
IRQ combiner is a **3-input NAND** (74LVC1G10): three idle-HIGH active-low IRQs give a
NAND output that is idle-LOW and asserts HIGH on any interrupt — matching the GPIO46
strap. nRF24/E22 are shielded modules (header/module footprints); the balun and per-band
matching are placeholders tuned by hand on a VNA.

**SP4T (`U24`) = SKY13414-485LF (C255353), in stock.** The originally-planned PE42440 is not
stocked at JLCPCB, so the in-stock SKY13414 is used. It takes **3-line control** (`V1/V2/V3`
= `RFSW_A/RFSW_B/RFSW_C`); the added `RFSW_C` rides **PCA9555 #2 P07** (Sheet 2). Its common
pad drives the CC1101 radio; RF1..RF4 fan the four per-band matches onto the shared antenna.
Ground the EP + unused pads per the SKY13414 layout.

## Gotchas

- **Only one CS low at a time.** The 74HC138 guarantees a single selected device; firmware parks the address on Y7 before switching. microSD (also on SPI2, Sheet 6) can hold `MISO` for a few clocks after deselect — issue **8+ dummy clocks** before addressing a radio.
- **CE is shared, CSN is not.** Independent addressing is via CSN (the 138); the tied `CE` only gates RX/TX enable, which suits parallel-scan and single-TX modes.
- **nRF24 IRQ is gated, not wire-OR.** Push-pull outputs need the SN74LVC1G10 NAND; it also fixes the GPIO46 boot-strap level. Don't try to pull-up wire-OR three totem-pole drivers.
- **Keep PA supplies stiff.** nRF24 brownout caps are mandatory; CC1101 and the E22 PA want local bulk too. A sagging PA rail shows up as range loss and packet errors, not as an obvious failure.
- **SP4T select is slow.** `RFSW_A/B/C` cross two PCA9555 devices over I²C — settle the switch before keying CC1101, and never change bands mid-transaction.
- **E22 is never truly off via GPIO.** Complementary RXEN/TXEN leave the LNA/PA biased; the E22 is on the non-gated `+3V3`, so a few mA idle draw is accepted (SX1262 SPI-sleep handles the chip). `RAIL_EN_3V3A` does **not** reach the E22 — it gates only Si4732/audio.
- **Shared SPI clock ceiling.** The bus clock must suit the slowest device (nRF24 ≤ 10 MHz on some clones); set a per-CS clock in firmware, or the display (fast) and nRF24 (slow) will fight the common rate.

---

*Next sheets: (4) [audio](../audio/audio.md) (Si4732 + SA868 + PAM8302), (5) [expansion](../expansion/expansion.md), (6) [indicators/IO](../indicators/indicators.md). Previous: (2) [C5 + buses](../c5-buses/c5-buses.md).*
*Part of [Leshy2](../../README.md) · MIT.*
