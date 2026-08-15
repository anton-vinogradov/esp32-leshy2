# Leshy2 — Power sheet (Sheet 1)

*Read this in: **English** · [Русский](power.ru.md)*

Design of the power subsystem. This is a **transcribe-ready schematic design**: exact parts, net-by-net connections, and passive values.

> 🗂️ The transcribe-ready schematic drawing for this sheet is being redrawn for the two-chip layout.

> ⚠️ Design stage — values verified against datasheets, not yet on real hardware. Treat feedback dividers and inductor/sense values as a starting point to confirm during bring-up.

The charger is a **boost** 2S device: it steps **5 V USB up** to charge the 8.4 V pack. There is **no PD, no NVDC power-path, and no ship mode** — the system runs from the battery, and the single **master switch** is the only true on/off. Both chips — the **ESP32-S3** brain and the **ESP32-C5** co-processor — draw from the same rails hanging on the `BAT` node.

## Rails

| Rail | Source | Voltage | Budget | Feeds |
|------|--------|---------|:------:|-------|
| `VBUS_S3` | USB-C **J1** | 5 V | input | charger (BQ25887) + S3 native-USB |
| `VBUS_C5` | USB-C **J2** | 5 V | ESD only | ESD clamp — **not routed into the system**; C5 senses USB via its own peripheral |
| `BAT` | 2S pack (after protection + master switch) | 6.0–8.4 V | — | the two bucks |
| `+5V` | MP2315 buck from `BAT`, **EN = RAIL_EN_5V** | 5.0 V | 3 A | SA868 PA, WS2812 (via level shifter), PAM8302, IR, Grove 5V (opt.), **+3V3A LDO input** |
| `+3V3` | **MP2315** buck from `BAT` (wide Vin) | 3.3 V | 2 A | **S3**, **C5**, CC1101, 3× nRF24, **SX1262 (LoRa)**, microSD, PCA9555 ×3, ST7796 logic, Grove ports |
| `+3V3A` | TPS7A2033 LDO from `+5V`, **EN = RAIL_EN_3V3A** | 3.3 V | 0.3 A | Si4732, SA868 audio front-end (clean analog/RF) |

The two bucks hang directly on the **BAT** node. With no battery there is no system power — this charger has no power-path.

## Blocks and parts

| Ref | Part | Role | Key notes |
|-----|------|------|-----------|
| J1 | USB-C receptacle (16P) → **S3** | 5 V charge input + S3 data/console | Feeds BQ25887 `VBUS`; D+/D− → S3 native USB GPIO19/20 (Sheet 2). CC1/CC2 via 5.1 kΩ pull-downs (accept 5 V); ESD array on VBUS + CC + D± |
| J2 | USB-C receptacle (16P) → **C5** | C5 data/flash only | D+/D− → C5 USB GPIO13/14 (Sheet 2). **VBUS is not routed into the system** — only an ESD clamp. C5 flashing is brick-safe via its mask-ROM |
| U2 | **BQ25887** | 2S **boost** charger, I²C, **cell balancing**, 16-bit ADC | Charges 8.4 V from **plain 5 V** USB; no PD needed. Control via `BQ_CD` (disable) + `BQ_INT` on PCA9555 #1. Fuel gauge read from its I²C ADC (~0x6A) |
| BT1 | 2× 18650 (2S) | Pack | ~7.4 V nom, ~18 Wh; **plastic 2-cell holder (or 2× single)**, cell mid-tap wired for balancing |
| U3 + Q1/Q2 | **S-8252A** (2S AFE) + 2× N-MOSFET | 2S protection | OV / UV / OC / short; **FETs in the pack negative return (low-side)** |
| F1 | PPTC fuse | Pack over-current | in series with pack + |
| SW_MASTER | Hard SPDT master switch, ON-OFF (≥3 A) | **The only on/off** — breaks the pack + line | pack + → BAT node |
| RT1 | 10 kΩ NTC | Pack temperature | to BQ25887 `TS` |
| U4 | **MP2315** | +5 V / 3 A buck | Vref 0.8 V; L2 4.7 µH; **EN = RAIL_EN_5V** (PCA #2 P0.1) |
| U5 | **MP2315** | +3.3 V / 2 A buck | Vref 0.8 V; L3 2.2 µH; **wide Vin** — sits on 8.4 V BAT; EN auto-on via 100k/47k divider from BAT; feeds both MCUs |
| U6 | **TPS7A2033** low-noise LDO | +3V3A analog | from **+5 V**; **EN = RAIL_EN_3V3A** (PCA #2 P0.2); feeds Si4732 / SA868 audio |

## Key nets

```
USB_VBUS : J1.VBUS ── U2.VBUS ── C1(10µF) ── D1(TVS)
USB_CC1/2: J1.CC1/CC2 ── 5.1k pull-downs (5 V sink)
USB_D±_S3: J1.D+/D− ── ESP32-S3 GPIO19/20 (Sheet 2) ── ESD array
USB_D±_C5: J2.D+/D− ── ESP32-C5 GPIO13/14 (Sheet 2) ── ESD array
J2_VBUS  : J2.VBUS ── ESD clamp only   ; NOT into any rail (C5 senses USB internally)
BAT      : BT1+ ── F1 ── SW_MASTER ── BAT node ── U2.BAT ── U4.IN ── U5.IN ── C6(22µF bulk)
           protection: BT1− ── Q1(low-side charge/discharge FETs, S-8252A) ── PACK−
           BATM = cell mid-tap ── U2.VCELL(balance) / U3.VC
SW1      : U2.SW ── L1(2.2µH) ── (boost node)
+5V      : U4.SW ── L2(4.7µH) ── +5V ── U6.IN ── C_out(2×22µF)   ; C_bst(100nF) U4.BST──U4.SW
+3V3     : U5.SW ── L3(2.2µH) ── +3V3 ── C_out(22µF)   ; C_bst(100nF) U5.BST──U5.SW ; feeds S3 + C5 + radios + SD + logic
+3V3A    : U6.OUT ── C(1µF‖2.2µF)
EN_5V    : U4.EN  ── RAIL_EN_5V   (PCA #2 P0.1) ── 100k pull-down (default off)
EN_3V3   : U5.EN  ── 100k/47k divider from BAT → auto-on at a safe level (never raw 8.4 V)
EN_3V3A  : U6.EN  ── RAIL_EN_3V3A (PCA #2 P0.2) ── 100k pull-down ; interlock — needs +5V up first
FB_5V    : +5V ── R1(52.3k) ── U4.FB ── R2(10k) ── GND      (0.8·(1+52.3/10)=4.98 V)
FB_3V3   : +3V3 ── R3(31.6k) ── U5.FB ── R4(10k) ── GND      (0.8·(1+31.6/10)=3.33 V)
I2C      : U2.SDA/SCL ── system I²C, S3 GPIO4/5 (Sheet 2) ; fuel gauge via U2 ADC
CTRL     : U2.BQ_CD, U2.BQ_INT ── PCA9555 #1 (Sheet 2)   (CD = pause charging ; INT = status)
GND      : common
```

## Passives (starting values)

- **VBUS in:** 10 µF X5R + 0.1 µF; TVS/ESD array on VBUS, both CC lines and D± — on **both** J1 and J2.
- **BQ25887:** L1 2.2 µH (Isat > 3 A), 10 µF at BAT, 47 nF bootstrap, ICHG/input-current-limit set over I²C.
- **MP2315 (+5V):** L2 4.7 µH (Isat > 4 A), Cin 22 µF, Cout 2× 22 µF, **100 nF bootstrap (BST→SW)**.
- **MP2315 (+3V3):** L3 2.2 µH (Isat > 3 A), Cin 22 µF, Cout 22 µF, **100 nF bootstrap (BST→SW)**; wide-Vin part (BAT direct), EN via 100k/47k divider from BAT.
- **LDO (+3V3A):** Cin 1 µF, Cout 2.2 µF (low-ESR).
- **nRF24 brown-out (critical):** **100–220 µF + 100 nF right at each of the 3 module VCC pins** on `+3V3`.
- **LCD backlight (bring-up item, not yet budgeted):** the 4.0″ panel's white-LED string wants a small boost / constant-current LED driver (~9–12 V, ~20–60 mA off `+5V` or `BAT`) — it is **not** on the logic `+3V3` rail. `LCD_BL_EN` (PCA9555 P1.4) is **on/off only**, so the roadmap's auto-dim needs a PWM-capable control line. Decide at bring-up: fixed-brightness on/off, or add the boost driver + one PWM pin for dimming.
- **SX1262 (LoRa) & SA868:** local bulk at each PA supply — SX1262 47–100 µF on +3V3; SA868 220–470 µF + 100 nF on +5V (2 W TX burst).

## Rail budget (why these sizes)

- **+5V / 3 A:** SA868 at 2 W TX pulls the biggest bursts (~1.5–2 A @ 5 V), plus WS2812 and PAM8302. Peak ~2–2.5 A → 3 A buck with margin. **LoRa is on +3V3, not here.**
- **+3V3 / 2 A:** S3 Wi-Fi TX + C5 Wi-Fi/BLE TX (~0.5 A) + 3× nRF24 PA (bursty) + **SX1262 +22 dBm (~0.12 A)** + CC1101 + SD + GPS + display logic + sensors → ~1.5 A peak.
- **+3V3A / 0.3 A:** Si4732 (~25 mA) and the SA868 audio front-end; separated to keep switching noise off the analog/RF supply.

## Protection & monitoring

- 2S protection (U3 **S-8252A** + Q1) in the pack **negative** return; PPTC (F1) and the master switch on pack +.
- NTC (RT1) to `TS` for charge-temperature cutoff.
- **Fuel gauge = the BQ25887's own I²C 16-bit ADC** (VBUS/BAT/cell voltages, charge current, temperature) — no dedicated MCU ADC pin.
- Test points: `TP_BAT`, `TP_5V`, `TP_3V3`, `TP_3V3A`, `TP_GND`.

## Fab realization (real parts)

`hardware/tscircuit/power.tsx` is now **fab-drafted**: every IC/connector pulls its
real, manufacturer-verified footprint and pinout from the LCSC/JLCPCB database
(`footprint="jlcpcb:C…"`), so pinouts are authoritative, not hand-typed. KiCad DRC on
the export reports **0 unconnected, 0 shorts, 0 schematic-parity** (the remaining
violations are placement/routing only — nothing is laid out yet).

| Ref | Part | LCSC |
|-----|------|------|
| J1, J2 | USB-C 16P GT-USB-7010ASV | C2988369 |
| U2 | BQ25887 | C2761614 |
| U3 | S-8252AAS-M6T1U | C468224 |
| Q1, Q2 | AO3400A N-FET | C20917 |
| U4, U5 | MP2315 | C45889 |
| U6 | TPS7A2033 | C2862740 |

Realized per datasheet: **BQ25887 wired as the boost it is** — inductor `PMID↔SW`,
boost output on its own `SNS` node (44 µF to GND — the SNS↔BAT shunt is **internal**, so SNS is *not* tied to BAT externally) — with its full support network (PMID/REGN/BTST/SNS/ILIM/MID
caps + the **TS thermistor divider from REGN**, without which charging is blocked);
MP2315 `VCC`/`AAM`; S-8252A reference sides (`VSS`=B−, `VM`=EB−). The 2S protection
FETs use the standard back-to-back **common-drain** pair (Q1 discharge / Q2 charge,
drains tied) — a single FS8205-class dual-FET may replace the two AO3400A. Values to
confirm at bring-up: the TS divider (per the exact NTC), cell-balance `Rcbset`, `Raam`.

## Gotchas

- **Charges from plain 5 V — no PD.** BQ25887 is a **boost** charger: it makes 8.4 V from 5 V USB. Charge current scales with the input current the source offers (set ICHG / input-limit over I²C). A 5 V / ≥2 A source is the target.
- **No power-path.** The bucks sit on the BAT node; with no battery the system is dead. Do not expect USB-only operation.
- **No soft power-off.** There is no ship mode on this charger. Power on/off is the **master switch** only (true zero when open). `BQ_CD` merely pauses charging. Because a master-switch cut is abrupt, the firmware should flush microSD periodically; an optional brown-out detector on BAT can trigger an emergency flush.
- **Two USB-C jacks, one power path.** Only **J1** (→ S3) carries charge into BQ25887. **J2** (→ C5) is data/flash only — its VBUS reaches ESD and a detect tap, never a rail. Plugging J2 alone will **not** power or charge the device; C5 re-flash is brick-safe through its mask-ROM.
- **RESET (EN) and BOOT are on the S3, not the C5** — the boot straps and reset button live on the brain (Sheet 2). The C5 is flashed over its own USB (J2) with no external boot control.
- **+3V3A is interlocked to +5V.** The analog LDO takes its input from +5V and its enable from `RAIL_EN_3V3A`; cutting `RAIL_EN_5V` collapses +5V and therefore the whole HF-receive front-end (Si4732 + audio) as well.
- **The +3V3 buck must be wide-Vin.** It sits directly on the 8.4 V `BAT` node, so a 5.5 V-max part (e.g. TLV62569) would be destroyed — use a wide-input buck (**MP2315**, same as +5V). Its enable is a **divider off `BAT`**, never raw 8.4 V on the EN pin. Both bucks need a **100 nF bootstrap cap (BST→SW)** or they will not switch.
- **eFuse `set_flash_voltage 3.3V` is a production step.** Burning it de-straps **GPIO45** so it can serve as the CC1101 carrier-sense IRQ; skip it and the flash-voltage strap fights that net.
- **Don't use IP5306-class power banks** — weak boost and auto-shutdown at low load.
- **TX power is a firmware concern** — per-region caps in software; the rails are sized to *allow* the legal maximum (SA868 2 W) without sagging.

---

*Next sheets: (2) [MCU + buses](../c5-buses/c5-buses.md), (3) [RF](../rf/rf.md), (4) [audio](../audio/audio.md), (5) [expansion](../expansion/expansion.md), (6) [indicators/IO](../indicators/indicators.md).*
*Part of [Leshy2](../../README.md) · MIT.*
