# Leshy2 — Audio sheet (Sheet 4)

*Read this in: **English** · [Русский](audio.ru.md)*

The two audio radios and the fully-analog path to the speaker: **Si4732** (HF / CB / FM receiver, I²C) and **SA868-U** (433 / 446 MHz voice walkie, UART), their analog line-outs summed into a **PAM8302** class-D amplifier, plus the electret mic for SA868 transmit. The MCU is **not** in the audio path — there is no DAC. Control pins come from [Sheet 2](../c5-buses/c5-buses.md); these are the last two of the eight onboard antennas.

> ⚠️ Design stage. Analog levels, the summing resistors and the mic bias are starting points to confirm on real hardware. Both radios run on the quiet **`+3V3A`** analog rail from the power sheet; the SA868 PA runs on **`+5V`**.

## Blocks and parts

| Ref | Part | Role | Interface |
|-----|------|------|-----------|
| U30 | **Si4732-A10** | AM/SSB/CW + FM receiver: CB 27 MHz, full HF/SW, MW/LW, FM 64–108 | I²C + RST + 32.768 kHz RCLK + analog LOUT/ROUT |
| U31 | **SA868-U** | 433/446 NBFM voice, RX + TX ≤ 2 W | UART + PTT + PD + AF-out + MIC-in |
| U32 | **PAM8302A** | Mono class-D amp, ~2.5 W @ 4 Ω | analog IN + SD (shutdown) |
| U33 | 2:1 analog mux (74LVC1G3157) | selects the active source into the amp | 1 select line (PCA9555) |
| MK1 | Electret mic + bias | SA868 transmit audio | analog → SA868 MIC |
| LS1 | Speaker 4–8 Ω | Output | from PAM8302 (BTL) |
| J30 (opt.) | 3.5 mm jack | Headphone tap + speaker mute on insert | jack-detect → PCA9555 |

Volume is set **inside each radio** — Si4732 by an I²C register, SA868 by a UART command — so there is no analog volume pot; the PAM8302 gain is fixed by resistors.

## Nets

```
Si4732 (U30)
  I2C     : SDA(0) · SCL(1)                         RST → PCA9555.P0.3
  clock   : 32.768 kHz crystal on RCLK/GPO3 + 2×~22 pF load caps   VDD → +3V3A ; SEN → GND (addr 0x11)
  antenna : HF/CB telescopic whip → AMI via match + ESD clamp ; FM tap → FMI (series cap)
  audio   : LOUT + ROUT → (L+R sum) → mux U33.A

SA868-U (U31)
  UART    : TX(11) → U31.RXD · RX(15) ← U31.TXD     PTT → PCA9555.P0.1 · PD → PCA9555.P0.2
  power   : module Vin = +5V + local 220–470µF + 100nF bulk (2 W PA burst) ; logic 3V3
  antenna : 433/446 UHF → SMA
  RX audio: U31.AF_OUT → mux U33.B
  TX audio: MK1 electret → 1 µF → U31.MIC_IN        (see gotcha)

Audio out
  mux     : U33 select = PCA9555.P0.7 (Si4732 vs SA868, one active at a time)
  amp     : U33.OUT → R_in → PAM8302.IN+ ; MUX_SEL → PCA9555.P0.7 ; PAM_SD → PCA9555.P1.3 ; +5V
  speaker : PAM8302 OUT± → LS1 (4–8 Ω, BTL, no ground reference)
  opt jack: J30 tip = pre-amp line tap ; sleeve-switch → mute PAM8302
```

## Analog routing — one source at a time

Because a radio mode is exclusive, only one audio source is ever live, so a tiny **2:1 analog switch (U33)** cleanly routes either the Si4732 line-out or the SA868 RX audio into the amp — no mixing artefacts, and the idle source is fully isolated. (A passive resistor sum would also work if the idle source is muted over I²C/UART, but the switch is cleaner for one control line.)

## Si4732 — receiver front end

- **Clean supply:** `+3V3A` (low-noise LDO, power sheet) keeps switching noise off the receiver.
- **RCLK:** a 32.768 kHz watch crystal is the reference — add **two ~22 pF load caps** (per the crystal's CL) or it may not start; keep traces short.
- **I²C address:** tie **SEN → GND** for address `0x11` (SEN → VIO = 0x63); fix it so the address is deterministic.
- **HF input protection:** the big telescopic whip feeds `AMI` through a matching network with a **passive ESD/clamp** (back-to-back diodes). There is **no manual antenna disconnect** — de-sense from our own transmitters is handled by mode-exclusive sleep, and the whip unscrews.
- **Line-out:** `LOUT`/`ROUT` are real analog audio; sum L+R to mono for the single speaker.

## SA868-U — voice walkie

- **Control over UART** (frequency, squelch, volume); **PTT** keys TX, **PD** sleeps the module. Both are slow → on the PCA9555.
- **PA on `+5V`** for the 2 W burst; add **local bulk (220–470 µF + 100 nF at the module Vin)** so a PTT burst doesn't sag the rail and distort TX. The +5V rail is sized for it (power sheet).
- **Legal power** is capped per region in firmware (446 PMR ≤ 0.5 W ERP; 5 W only on ham 70 cm with a licence).

## PAM8302 — speaker amp

- Single-ended input from the mux, gain fixed by the input resistor; **SD** (shutdown) on the PCA9555 mutes the amp and saves power between sounds.
- **BTL output** drives the speaker directly — do **not** ground either speaker terminal.

## Gotchas

- **Mic coupling cap = 1 µF, not 10 µF.** A 10 µF cap into the SA868 MIC forms a long RC with the bias network, so the first ~0.5 s of transmit audio fades in and the first word is clipped. 1 µF settles fast.
- **The MCU has no DAC.** All audio is analog line-out → amp; any MCU-generated tone could only be an I²S codec, deliberately kept out of the receive chain. The buzzer (Sheet 2) is the only MCU-driven sound.
- **Keep +3V3A quiet.** Route the Si4732/SA868-audio supply away from the bucks and the nRF24 PA returns; a noisy analog rail shows up as receiver hiss.
- **Mute before switching.** Assert PAM8302 `SD` while the mux flips sources, to avoid a click.

---

*Next sheets: (5) expansion, (6) indicators/IO. Previous: (3) [RF chains](../rf/rf.md).*
*Part of [Leshy2](../../README.md) · MIT.*
