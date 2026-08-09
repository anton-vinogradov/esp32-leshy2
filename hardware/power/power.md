# Leshy2 — Power sheet (Sheet 1)

*Read this in: **English** · [Русский](power.ru.md)*

Design of the power subsystem. This is a **transcribe-ready schematic design**: exact parts, net-by-net connections, and passive values. See [power-schematic.svg](power-schematic.svg) for the drawing.

> ⚠️ Design stage — values verified against datasheets, not yet on real hardware. Treat feedback dividers and inductor/sense values as a starting point to confirm during bring-up.

The charger is a **boost** 2S device: it steps **5 V USB up** to charge the 8.4 V pack. There is **no PD, no NVDC power-path, and no ship mode** — the system runs from the battery, and the single **master switch** is the only true on/off.

## Rails

| Rail | Source | Voltage | Budget | Feeds |
|------|--------|---------|:------:|-------|
| `VBUS` | USB-C | 5 V | input | charger only |
| `BAT` | 2S pack (after protection + master switch) | 6.0–8.4 V | — | the two bucks |
| `+5V` | MP2315 buck from `BAT` | 5.0 V | 3 A | SA868 PA, WS2812 (via level shifter), audio amp, Grove 5V (opt.) |
| `+3V3` | TLV62569 buck from `BAT` | 3.3 V | 2 A | C5, CC1101, 3× nRF24, **SX1262 (LoRa)**, microSD, u-blox GPS, PCA9555, ST7796 logic, sensors |
| `+3V3A` | low-noise LDO from +5V | 3.3 V | 0.3 A | Si4732, SA868 audio front-end (clean analog/RF) |

The two bucks hang directly on the **BAT** node. With no battery there is no system power — this charger has no power-path.

## Blocks and parts

| Ref | Part | Role | Key notes |
|-----|------|------|-----------|
| J1 | USB-C receptacle (16P) | 5 V input + data | CC1/CC2 via 5.1 kΩ pull-downs (accept 5 V); D+/D− → C5 USB; ESD array on VBUS + CC + D± |
| U2 | **BQ25887** | 2S **boost** charger, I²C, **cell balancing**, 16-bit ADC | Charges 8.4 V from **plain 5 V** USB; no PD needed. Control via `CD` (disable) + `/INT`. Fuel gauge read from its I²C ADC |
| BT1 | 2× 18650 (2S) | Pack | ~7.4 V nom, ~18 Wh; cell mid-tap wired for balancing |
| U3 + Q1 | **S-8252A** (2S AFE) + dual N-MOSFET | 2S protection | OV / UV / OC / short; **FETs in the pack negative return (low-side)** |
| F1 | PPTC fuse | Pack over-current | in series with pack + |
| SW_MASTER | Hard SPST master switch (≥3 A) | **The only on/off** — breaks the pack + line | pack + → BAT node |
| RT1 | 10 kΩ NTC | Pack temperature | to BQ25887 `TS` |
| U4 | **MP2315** | +5 V / 3 A buck | Vref 0.8 V; L2 4.7 µH |
| U5 | **TLV62569** | +3.3 V / 2 A buck | Vref 0.6 V; L3 2.2 µH |
| U6 | Low-noise LDO (**TPS7A2033** / AP2112K-3.3) | +3V3A analog | from +5 V; feeds Si4732 / SA868 audio |

## Key nets

```
USB_VBUS : J1.VBUS ── U2.VBUS ── C1(10µF) ── D1(TVS)
USB_CC1/2: J1.CC1/CC2 ── 5.1k pull-downs (5 V sink)
USB_D±   : J1.D+/D− ── ESP32-C5 GPIO13/14 (Sheet 2) ── ESD array
BAT      : BT1+ ── F1 ── SW_MASTER ── BAT node ── U2.BAT ── U4.IN ── U5.IN ── C6(22µF bulk)
           protection: BT1− ── Q1(low-side charge/discharge FETs, S-8252A) ── PACK−
           BATM = cell mid-tap ── U2.VCELL(balance) / U3.VC
SW1      : U2.SW ── L1(2.2µH) ── (boost node)
+5V      : U4.SW ── L2(4.7µH) ── +5V ── U6.IN ── C_out(2×22µF)
+3V3     : U5.SW ── L3(2.2µH) ── +3V3 ── C_out(22µF)
+3V3A    : U6.OUT ── C(1µF‖2.2µF)
FB_5V    : +5V ── R1(52.3k) ── U4.FB ── R2(10k) ── GND      (0.8·(1+52.3/10)=4.98 V)
FB_3V3   : +3V3 ── R3(45.3k) ── U5.FB ── R4(10k) ── GND      (0.6·(1+45.3/10)=3.32 V)
I2C      : U2.SDA/SCL ── system I²C (Sheet 2)     ; fuel gauge via U2 ADC
CTRL     : U2.CD, U2./INT ── PCA9555 (Sheet 2)     (CD = pause charging ; INT = status)
GND      : common
```

## Passives (starting values)

- **VBUS in:** 10 µF X5R + 0.1 µF; TVS/ESD array on VBUS, both CC lines and D±.
- **BQ25887:** L1 2.2 µH (Isat > 3 A), 10 µF at BAT, 47 nF bootstrap, ICHG/input-current-limit set over I²C.
- **MP2315 (+5V):** L2 4.7 µH (Isat > 4 A), Cin 22 µF, Cout 2× 22 µF, EN pull-up.
- **TLV62569 (+3V3):** L3 2.2 µH (Isat > 3 A), Cin 22 µF, Cout 22 µF.
- **LDO (+3V3A):** Cin 1 µF, Cout 2.2 µF (low-ESR).
- **nRF24 brown-out (critical):** **100–220 µF + 100 nF right at each of the 3 module VCC pins** on `+3V3`.
- **SX1262 (LoRa) & SA868:** local bulk at each PA supply — SX1262 47–100 µF on +3V3; SA868 220–470 µF + 100 nF on +5V (2 W TX burst).

## Rail budget (why these sizes)

- **+5V / 3 A:** SA868 at 2 W TX pulls the biggest bursts (~1.5–2 A @ 5 V), plus WS2812 and PAM8302. Peak ~2–2.5 A → 3 A buck with margin. **LoRa is on +3V3, not here.**
- **+3V3 / 2 A:** C5 Wi-Fi TX (~0.5 A) + 3× nRF24 PA (bursty) + **SX1262 +22 dBm (~0.12 A)** + CC1101 + SD + GPS + display logic + sensors → ~1.5 A peak.
- **+3V3A / 0.3 A:** Si4732 (~25 mA) and the SA868 audio front-end; separated to keep switching noise off the analog/RF supply.

## Protection & monitoring

- 2S protection (U3 **S-8252A** + Q1) in the pack **negative** return; PPTC (F1) and the master switch on pack +.
- NTC (RT1) to `TS` for charge-temperature cutoff.
- **Fuel gauge = the BQ25887's own I²C 16-bit ADC** (VBUS/BAT/cell voltages, charge current, temperature) — no dedicated C5 ADC pin.
- Test points: `TP_BAT`, `TP_5V`, `TP_3V3`, `TP_3V3A`, `TP_GND`.

## Gotchas

- **Charges from plain 5 V — no PD.** BQ25887 is a **boost** charger: it makes 8.4 V from 5 V USB. Charge current scales with the input current the source offers (set ICHG / input-limit over I²C). A 5 V / ≥2 A source is the target.
- **No power-path.** The bucks sit on the BAT node; with no battery the system is dead. Do not expect USB-only operation.
- **No soft power-off.** There is no ship mode on this charger. Power on/off is the **master switch** only (true zero when open). `CD` merely pauses charging. Because a master-switch cut is abrupt, the firmware should flush microSD periodically; an optional brown-out detector on BAT can trigger an emergency flush.
- **Don't use IP5306-class power banks** — weak boost and auto-shutdown at low load.
- **TX power is a firmware concern** — per-region caps in software; the rails are sized to *allow* the legal maximum (SA868 2 W) without sagging.
- RESET (EN) and BOOT are on the C5 (Sheet 2).

---

*Next sheets: (2) ESP32-C5 + buses, (3) RF chains, (4) audio, (5) expansion, (6) indicators/IO.*
*Part of [Leshy2](../../README.md) · MIT.*
