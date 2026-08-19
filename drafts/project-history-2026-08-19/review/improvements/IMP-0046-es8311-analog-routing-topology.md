# IMP-0046 — complete codec, analog routing and reset-default package

- Статус: **Принято как вариант A в DEC-0054**
- Дата: 2026-08-17
- Facts: [`AUDIO-0002`](../architecture/AUDIO-0002-complete-audio-path-comparison.md)
- Findings: [`FND-0066`](../findings/FND-0066-es8311-line-input-and-pam-differential-capability.md),
  [`FND-0067`](../findings/FND-0067-audio-source-select-and-reset-bypass.md)
- Review: [`REV-0005C`](../reviews/REV-0005C-complete-audio-path-prerequisites.md)
- Decision: [`DEC-0054`](../decisions/DEC-0054-fail-safe-complete-audio-path.md)

## Текущее состояние

ES8311 digital fit remains valid on S3 GPIO1/2/15/16/17/18, but the old phrase
«ADC tap + two selectors» was not a complete circuit. A direct `≈6 kΩ` ES8311
tap can load the Si4732 bypass, the ES8311 user guide discourages blind line-in,
PAM8302A can already accept differential DAC, SA518 TX needs about 40 dB
attenuation, and TCA6424 selector outputs can remain stale through S3 reset.

The separately omitted `RX_AUDIO_SOURCE_SEL` has already been corrected on
slow `P27`; slow budget is now `24/0/0`. The remaining choice must select the
whole path and its failure behavior together.

## A — E2-B supported codec + active capture + one-pin arm **(recommended)**

- Keep exact `ES8311` QFN-20 and current Espressif driver path.
- Add high-input-impedance AC-coupled buffer candidate `TLV9061IDBVR` before a
  qualified ES8311 mic-range input network.
- Switch both PAM8302A inputs with dual `TMUX1136DGSR/DQAR`; use separate
  `TS5A63157DCKR` for attenuated DAC-to-SA518 selection.
- Keep P11/P12 as requested modes, add direct S3 GPIO6 `AUDIO_ARM`, and gate
  both through `SN74LVC2G08DCUR`; arm-low forces analog defaults.
- Preserve S3 GPIO43 as the only free direct S3 contact.
- Put passive E1-P stuffing/bypass pads on the prototype. They are not the
  production cost-down until the same board proves bypass and capture equality.

Consequences: one op-amp and one dual logic IC are added; codec/selector analog
values and HIL remain work. This has the least combined architecture, firmware
and zero-loss risk.

## B — E1-P cheapest passive ES8311 path from first prototype

Same differential output selectors and one-pin arm as A, but no active capture
buffer. A high-series-impedance passive network attenuates MUX_OUT into
ES8311. It is the smallest BOM, but it makes first hardware responsible for
proving unknown Si4732 level, low-band response and record SNR. Failure means a
board rework or a second PCB revision rather than a DNP cost-down.

## C — T1-P TAC5111IRGER documented-line-input path

Replace ES8311 with active TI `TAC5111IRGER`, VQFN-24 4×4 mm. It fits the same
six digital bus GPIO, documents line/mic input and 40-kΩ mode, and has excellent
ADC/DAC performance. It still needs external fail-safe speaker/TX selectors,
the one-pin arm and a high-impedance capture network. It is roughly `$1.6`
higher than ES8311 plus the screened buffer at quantity 100 before common
parts, and current `esp_codec_dev` does not provide its driver.

Consequences: technically clean codec documentation, larger/denser package,
new driver/HIL work and materially higher cost without a new accepted feature.

## Rejected fragments

- Former central differential-to-single-ended option: unnecessary for speaker
  because PAM8302A already accepts differential input.
- One DAC leg for both speaker and TX: loses differential speaker benefit and
  still does not solve TX attenuation.
- P11/P12 pulls alone: do not override an actively driven stale expander.
- Reset/power-cycle the whole TCA6424 for audio: couples unrelated UI, power and
  fault controls into audio recovery.
- Internal codec analog bypass as the only bypass: ordinary radio audio would
  then depend on codec power/register health.

## Recommendation

Accept **A**. It is deliberately the robust prototype, not the permanent
expensive stuffing choice: E1-P remains an explicit cost-down experiment on
the same PCB and may remove the op-amp only after measured equivalence. Do not
pay the TAC5111 premium unless E2 fails analog/RF HIL or later sourcing changes
the complete-circuit comparison.

## Owner result

Владелец принял вариант **A** целиком. Нормативный результат, pin-budget
consequence и открытая schematic/HIL boundary зафиксированы в `DEC-0054`.
