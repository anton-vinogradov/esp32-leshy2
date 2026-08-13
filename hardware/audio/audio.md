# Leshy2 — Audio sheet (Sheet 4)

*Read this in: **English** · [Русский](audio.ru.md)*

The two audio radios and the fully-analog path to the speaker: **Si4732** (HF / CB / FM receiver, I²C) and **SA868-U** (UHF voice walkie, UART). Their analog line-outs feed a **2:1 analog mux** into a **PAM8302** class-D amplifier; an electret mic feeds SA868 transmit. The MCU is **not** in the audio path — there is no DAC. Everything hangs off the **ESP32-S3** brain: control pins on two of the three **PCA9555** expanders, data on the **SA868 UART1** and **Si4732 I²C**. These are two of the nine onboard antennas.

> ⚠️ Design stage. Analog levels, the summing resistors and the mic bias are starting points to confirm on real hardware. Si4732 and the whole analog front end run on the quiet **`+3V3A`** LDO rail (from `+5V`, [power sheet](../power/power.md)); the SA868 PA runs on **`+5V`**.

## Blocks and parts

| Ref | Part | Role | Key notes |
|-----|------|------|-----------|
| U30 | **Si4732-A10** | AM/SSB/CW + FM receiver: CB 27 MHz, full HF/SW, MW/LW, FM 64–108 | **A10 only** — the SSB patch will not load on A11; I²C `0x11`, telescopic whip |
| U31 | **SA868-U** | UHF NBFM voice, RX + TX ≤ 2 W | UART1 + PTT + PD; own SMA |
| U32 | **PAM8302A** | Mono class-D amp, ~2.5 W @ 4 Ω | BTL out; SD (shutdown) on PCA #1 |
| U33 | **74LVC1G3157** | 2:1 analog mux — picks the live source into the amp | one select line, PCA #1 |
| MK1 | Electret mic + bias | SA868 transmit audio | analog → SA868 MIC via **1 µF** |
| LS1 | Speaker 4–8 Ω | Output | from PAM8302 (BTL, floating) |
| J30 | 3.5 mm jack | Headphone tap + mechanical mute on insert | jack-detect on PCA #2 (see gotcha) |

Volume is set **inside each radio** — Si4732 by an I²C register, SA868 by a UART command — so there is no analog volume pot; the PAM8302 gain is fixed by resistors.

## Key nets

```
Si4732 (U30)  — analog front end, all on +3V3A
  I2C     : SDA=GPIO4 · SCL=GPIO5   addr 0x11 (SEN → GND)
  reset   : RST  → PCA #1 (0x20) P0.3
  clock   : RCLK ← dedicated 32.768 kHz crystal (NOT from the MCU) + load caps
  antenna : HF/CB telescopic whip → AMI via match + ESD clamp (back-to-back diodes)
            FM tap → FMI (series cap)
  audio   : LOUT + ROUT → summing R pair (L+R → mono) → mux U33.A

SA868-U (U31)
  UART1   : TX=GPIO16 → U31.RXD · RX=GPIO17 ← U31.TXD
  control : PTT → PCA #1 P0.1 · PD → PCA #1 P0.2
  power   : VBAT = +5V + local bulk 220–470 µF + 100 nF (2 W PA burst)   ; single-supply module
  antenna : UHF → SMA
  RX audio: U31.AF_OUT → mux U33.B2
  TX audio: MK1 electret → 1 µF → U31.MIC_IN   (see gotcha)

Audio out
  mux     : U33 select = MUX_SEL → PCA #1 P0.7  (Si4732 vs SA868, one live at a time)
  amp     : U33.A → R_in → PAM8302.IN ; SD = PAM_SD → PCA #1 P1.3 ; Vcc = +5V
  speaker : PAM8302 OUT± → LS1 (4–8 Ω, BTL, no ground reference)
  jack    : J30 JACK_DET → PCA #2 (0x21) P0.3 ; AC-couple both legs (see gotcha)
```

## Analog routing — one source at a time

A radio mode is exclusive, so only one audio source is ever live. The tiny **2:1 analog switch (U33, 74LVC1G3157)** cleanly routes either the Si4732 line-out or the SA868 RX audio into the amp — no mixing artefacts, and the idle source is fully isolated. One control line (`MUX_SEL`, PCA #1 P0.7) does it.

## Si4732 — receiver front end

- **Revision A10, not A11.** The downloadable **SSB patch loads only on A10**; an A11 die will run FM/AM but silently refuse SSB/CW. Buy and mark A10 parts.
- **Clean supply:** the low-noise **`+3V3A`** LDO keeps switching noise off the receiver.
- **RCLK from a dedicated 32.768 kHz crystal**, not the MCU — a separate watch crystal with its load caps. Sharing an MCU clock injects digital jitter into the tuner. Keep traces short or it may not start.
- **I²C address:** tie **SEN → GND** for `0x11` (SEN → VIO = 0x63); fix it so the address is deterministic.
- **HF input protection:** the telescopic whip feeds `AMI` through a matching network with a **passive ESD clamp (back-to-back diodes)**. The FM tap feeds `FMI` through a **series cap**. There is **no manual antenna disconnect** — de-sense from our own transmitters is handled by mode-exclusive sleep, and the whip unscrews.
- **Line-out:** `LOUT`/`ROUT` are real analog audio; a **pair of summing resistors** collapses L+R to mono for the single speaker.

## SA868-U — voice walkie

- **Control over UART1** (frequency, squelch, volume); **PTT** keys TX, **PD** sleeps the module. Both are slow → on **PCA #1** (P0.1 / P0.2).
- **Single-supply `VBAT` on `+5V`** for the 2 W burst; add **local bulk (220–470 µF + 100 nF at the module VBAT)** so a PTT burst doesn't sag the rail and distort TX. The +5V rail is sized for it (power sheet).
- **Legal power** is capped per region in firmware (446 PMR ≤ 0.5 W ERP; 5 W only on ham 70 cm with a licence).

## PAM8302 — speaker amp

- Single-ended input from the mux, gain fixed by the input resistor; **SD** (shutdown, PCA #1 P1.3) mutes the amp and saves power between sounds.
- **BTL output** drives the speaker directly — do **not** ground either speaker terminal.

## Fab realization (real parts)

`hardware/tscircuit/audio.tsx` is fab-drafted: real footprints/pinouts are engine-pulled
from LCSC. KiCad DRC = **0 unconnected / 0 shorts / 0 schematic-parity**.

| Ref | Part | LCSC |
|-----|------|------|
| U30 | Si4732-A10-GS (16-SOIC) | C1526102 |
| U31 | SA868-U walkie module | C3001507 |
| U32 | PAM8302AASCR (8-pin MSOP) | C113367 |
| U33 | SN74LVC1G3157 analog mux | C10426 |
| Y1 | 32.768 kHz crystal NX3215SA | C280830 |

Corrections found by realizing against the real parts:
- **SA868-U is single-supply.** The real module has one **`VBAT`** pin (3.3–5.5 V), not the
  separate `VIN`+`VCC3V3` the base assumed — `VBAT` → `+5V`, the 3V3 pin is dropped. Its
  internal audio-amp enable `AudioON` (active-low) is tied to GND.
- **PAM8302A is 8-pin MSOP**, not SOT-23-6.
- Si4732 gained its `RFGND` → GND and a 100 nF VDD HF decoupling cap.

To confirm at layout: **SA868 `H/L` (pin 7) is left open = 2 W high power** — pull it low
(or wire a control line) for regions capped at ≤0.5 W (UART power-set is available too);
Si4732 pins 1/2/3/16 (engine-unnamed → ROUT/LOUT/NC); the 3.5 mm jack and mic/speaker are
placeholders; crystal load caps (12 pF) per the final crystal.

## Gotchas

- **Headphone jack needs AC coupling — the amp is BTL.** PAM8302 has no ground reference; both outputs swing. A standard TRS jack ties `sleeve → GND`, which would **short one bridge leg** and kill/overheat the amp. Series **coupling caps on both legs** (or a proper single-ended headphone driver) before J30; mechanical mute on insert is fine. `JACK_DET` on **PCA #2 P0.3**.
- **Si4732 must be A10.** An A11 die looks identical and works on FM/AM, so the fault only shows when SSB stays silent. Wrong-revision boards are unfixable in software.
- **Mic coupling cap = 1 µF, not 10 µF.** A 10 µF cap into the SA868 MIC forms a long RC with the bias network, so the first ~0.5 s of transmit audio fades in and the **first word is clipped**. 1 µF settles fast.
- **The MCU has no DAC.** All audio is analog line-out → mux → amp; the buzzer (control sheet) is the only MCU-driven sound.
- **Keep +3V3A quiet.** Route the Si4732 / SA868-audio supply away from the bucks and the nRF24 PA returns; a noisy analog rail shows up as receiver hiss. Note the interlock: `+3V3A` is fed from `+5V`, so cutting the +5V rail also silences HF receive.
- **Mute before switching.** Assert PAM8302 `SD` while the mux flips sources, to avoid a click.

---

*Next sheets: (5) [expansion](../expansion/expansion.md), (6) [indicators/IO](../indicators/indicators.md). Previous: (3) [RF](../rf/rf.md).*
*Part of [Leshy2](../../README.md) · MIT.*
