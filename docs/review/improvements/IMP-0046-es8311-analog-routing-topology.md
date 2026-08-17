# IMP-0046 — exact ES8311 analog routing topology

- Статус: **⚠️ Открыто; прежняя рекомендация A снята после complete-path review**
- Дата: 2026-08-17
- Trigger: [`FND-0065`](../findings/FND-0065-es8311-ce-and-differential-path.md)
- Evidence: [`AUDIO-0001`](../architecture/AUDIO-0001-es8311-exact-electrical-fit.md)
- Additional finding: [`FND-0066`](../findings/FND-0066-es8311-line-input-and-pam-differential-capability.md)
- Не меняет: S3 GPIO/I2S map, two slow selector controls, PTT independence

## Почему нужен выбор

Legacy analog bypass is wired single-ended. Exact ES8311 DAC is differential
`OUTP/OUTN`, but physical PAM8302A already has differential `IN+/IN-`; only its
legacy wiring is single-ended. Separately, ES8311 `MIC1P/MIC1N` are described
by the manufacturer as a microphone interface not recommended for line input,
while both selected RX sources are line/audio outputs. The output choice and
ADC conditioner must therefore be reviewed as one complete path.

## Варианты

### A — differential-to-single-ended conditioner, затем два one-pole selector

`OUTP/OUTN` входят в low-noise differential receiver; его single-ended output
идёт на speaker selector и через отдельный level/AC-coupling network на TX
selector. Analog defaults остаются `RX→PAM8302` и `electret→SA518 MIC_IN`.

- Плюсы: используется полный differential DAC swing; одна понятная точка gain/
  filtering; сохраняется legacy single-ended bypass и два control signal.
- Минусы: op-amp + matched resistors + decoupling; дополнительный active-noise/
  power объект; exact common-mode/output swing must be calculated.
- Current exact candidates: `TLV9061IDBVR` as receiver, two
  `SN74LVC1G3157DBVR` selectors. Это candidates, не BOM freeze.

### B — один DAC leg через AC coupling/attenuation, два one-pole selector

Один из `OUTP/OUTN` используется как single-ended source; второй получает
только manufacturer-valid load/termination.

- Плюсы: минимальный BOM/area; retains two selector controls.
- Минусы: потенциально теряет около 6 dB differential swing и common-mode
  cancellation; noise/headroom and unused-leg legality require explicit proof;
  это нельзя назвать «без потерь» до HIL.

### C — differential speaker switching plus separate TX conversion

Both PAM8302A input legs switch as a pair. In bypass, `IN+` receives qualified
`MUX_OUT` and `IN-` receives the matched AC-ground reference. In codec mode,
they receive AC-coupled `OUTP/OUTN`. TX uses a high-impedance, AC-coupled and
heavily attenuated tap from one DAC leg through its own selector.

- Плюсы: preserves the full differential DAC for local playback without the
  central op-amp; retains hardware-default RX bypass and the existing two slow
  controls. One DAC leg is still far above the SA518 typical modulation level,
  so the TX branch needs attenuation rather than voltage gain.
- Минусы: at least three analog switch poles; legacy bypass/PAM input network
  must be redesigned; one-leg loading and the exact SA518 divider/filter must
  pass calculation and HIL; more routing and common-die/fault analysis.
- Candidate switch: dual `TMUX1136DGSR` or `TMUX1136DQAR` for speaker plus
  `TS5A63157DCKR` for TX.

## Separate ADC-side problem

The user guide says the fully differential input is a microphone interface and
is not recommended for line input. Yet the product brief specifies about
`2 Vrms` differential full scale and `6 kΩ` input impedance, so the warning is
not equivalent to a hard prohibition. It means a blind ADC tap is not an
accepted circuit. Three implementation branches remain:

1. passive AC-coupled attenuation/reference network into `MIC1P/MIC1N`;
2. active line-to-differential buffer/conditioner;
3. reopen the codec comparison for a part with documented line input.

Actual Si4732 and SA518 min/nominal/max output levels, loading and required
recording SNR decide between them. A PCB can expose stuffing options for the
passive and active paths, but that choice adds area and test burden.

## Updated recommendation

Do **not** accept A yet. For the DAC/output half, **C** is now the leading
lower-BOM candidate because PAM8302A can already consume a differential input.
For the ADC/input half, no zero-loss recommendation is honest before the
source-level/load calculation and comparison with a documented-line-input
codec. The next artifact must compare complete circuits, not isolated ICs.

## Acceptance after choice

The eventual option is conditional on exact gain/common-mode calculations,
SA518/PAM8302 limits, off-state loading, power/reset defaults, pop/click and RF
HIL. No option allows codec state to assert PTT.
