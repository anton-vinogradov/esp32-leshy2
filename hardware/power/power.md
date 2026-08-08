# Leshy2 — Power sheet (Sheet 1)

*Read this in: **English** · [Русский](power.ru.md)*

Design of the power subsystem. This is a **transcribe-ready schematic design**: exact parts,
net-by-net connections, and passive values. See [power-schematic.svg](power-schematic.svg) for the drawing.

> ⚠️ Design stage — values verified against datasheets, not yet on real hardware. Treat feedback
> dividers and inductor/sense values as a starting point to confirm during bring-up.

## Rails

| Rail | Source | Voltage | Budget | Feeds |
|------|--------|---------|:------:|-------|
| `VBUS` | USB-C | 5 V, or **12 V** via PD | input | charger only |
| `VBAT` | 2S pack | 6.0–8.4 V | — | charger / power-path |
| `VSYS` | charger power-path | 6.0–8.4 V | ~3 A | the two bucks |
| `+5V` | buck from VSYS | 5.0 V | 3 A | SA868 PA, LoRa cap, WS2812, audio amp, Grove/cap 5V |
| `+3V3` | buck from VSYS | 3.3 V | 2 A | C5, CC1101, 3× nRF24, microSD, display logic, sensors |
| `+3V3A` | low-noise LDO from +5V | 3.3 V | 0.3 A | Si4732, SA868 audio front-end (clean analog/RF) |

Power-path means the system runs from `VSYS` **even with no battery / while charging**.

## Blocks and parts

| Ref | Part | Role | Key notes |
|-----|------|------|-----------|
| J1 | USB-C receptacle (16P) | Input + PD | CC1/CC2 → CH224K; VBUS → charger; add USB ESD array on VBUS + CC |
| U1 | **CH224K** | USB-PD sink | Strap CFG for a **12 V** request so the 2S buck charger has headroom above 8.4 V |
| U2 | **BQ25887** | 2S buck charger, I²C, **cell balancing**, power-path | Needs `VBUS > VBAT` to charge → 12 V from PD. At 5 V-only input it will **not** charge 2S (system still runs from battery) |
| BT1 | 2× 18650 (2S) | Pack | ~7.4 V nom, ~18 Wh; cell mid-tap wired for balancing |
| U3 + Q1 | **S-8254A** + dual N-MOSFET | 2S protection | OV / UV / OC / short; low-side FETs |
| F1 | PPTC fuse | Pack over-current | In series with pack + |
| RT1 | 10 kΩ NTC | Pack temperature | To BQ25887 `TS` pin |
| U4 | **MP2315** | +5 V / 3 A buck | Vref 0.8 V; L2 4.7 µH |
| U5 | **TLV62569** | +3.3 V / 2 A buck | Vref 0.6 V; L3 2.2 µH |
| U6 | Low-noise LDO (**TPS7A2033** or AP2112K-3.3) | +3V3A analog | From +5 V; feeds Si4732 / SA868 audio |

## Key nets

```
USB_VBUS : J1.VBUS ── U1.VBUS ── U2.VBUS ── C1(10µF) ── D1(TVS)
USB_CC1  : J1.CC1  ── U1.CC1
USB_CC2  : J1.CC2  ── U1.CC2
VBAT     : BT1+ ── F1 ── Q1(protection) ── U2.BAT ; BATM = cell mid-tap ── U2.VC / U3
VSYS     : U2.SYS ── U4.IN ── U5.IN ── C6(22µF bulk)
SW1      : U2.SW ── L1(2.2µH) ── VSYS
+5V      : U4.SW ── L2(4.7µH) ── +5V ── U6.IN ── C_out(2×22µF)
+3V3     : U5.SW ── L3(2.2µH) ── +3V3 ── C_out(22µF)
+3V3A    : U6.OUT ── C(1µF‖2.2µF)
FB_5V    : +5V ── R1(52.3k) ── U4.FB ── R2(10k) ── GND      (0.8·(1+52.3/10)=4.98 V)
FB_3V3   : +3V3 ── R3(45.3k) ── U5.FB ── R4(10k) ── GND      (0.6·(1+45.3/10)=3.32 V)
I2C      : U2.SDA/SCL ── (system I²C to ESP32-C5)
IRQ/CE   : U2.INT, U2.CE, U2.QON ── ESP32-C5 GPIO
VMON     : VBAT ── R(200k)/R(100k) divider ── ESP32-C5 ADC (coarse gauge)
GND      : common
```

## Passives (starting values)

- **VBUS in:** 10 µF X5R + 0.1 µF; TVS/ESD array on VBUS and both CC lines.
- **BQ25887:** L1 2.2 µH (Isat > 3 A), 10 µF on SYS, 47 nF bootstrap, ICHG/ILIM set over I²C.
- **MP2315 (+5V):** L2 4.7 µH (Isat > 4 A), Cin 22 µF, Cout 2× 22 µF, EN pull-up.
- **TLV62569 (+3V3):** L3 2.2 µH (Isat > 3 A), Cin 22 µF, Cout 22 µF.
- **LDO (+3V3A):** Cin 1 µF, Cout 2.2 µF (low-ESR).
- **nRF24 brown-out (critical):** **100–220 µF + 100 nF right at each of the 3 module VCC pins** on `+3V3` — the PA/LNA modules pull bursty current and will sag their neighbours otherwise.

## Rail budget (why these sizes)

- **+5V / 3 A:** SA868 at 2 W TX pulls the biggest bursts (~1 A @ 5 V), plus LoRa-cap peaks, WS2812 (kept dim), and PAM8302. Peak ~2–2.5 A → 3 A buck with margin.
- **+3V3 / 2 A:** C5 Wi-Fi TX bursts (~0.5 A) + 3× nRF24 PA (bursty) + CC1101 + SD + display logic + sensors → ~1–1.5 A peak.
- **+3V3A / 0.3 A:** Si4732 (~25 mA) and the SA868 audio front-end; separated to keep switching noise off the analog/RF supply.

## Protection & monitoring

- 2S protection (U3 + Q1) between cells and charger; PPTC (F1) on pack+.
- NTC (RT1) to `TS` for charge-temperature cutoff.
- Coarse fuel gauge = `VBAT` divider into a C5 ADC pin; fine gauge (optional) = a 2S gauge IC later.
- Test points: `TP_VBAT`, `TP_VSYS`, `TP_5V`, `TP_3V3`, `TP_3V3A`, `TP_GND`.

## Gotchas

- **Charging needs PD.** With plain 5 V USB (no PD), a 2S buck charger cannot reach 8.4 V — CH224K must negotiate 9–12 V. The device still **runs** from battery on 5 V-only input.
- **Don't use IP5306-class power banks** here — weak boost and auto-shutdown at low load. This is why we roll our own PMIC.
- **TX power is a firmware concern, not a rail concern** — per-region caps are enforced in software, but the +5V rail is sized to *allow* the legal maximum (e.g., SA868 2 W) without sagging.

---

*Next sheets: (2) ESP32-C5 + buses, (3) RF chains, (4) audio, (5) expansion, (6) indicators/IO.*
*Part of [Leshy2](../../README.md) · MIT.*
