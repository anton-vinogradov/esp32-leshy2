# IMP-0046 — exact ES8311 analog routing topology

- Статус: **⚠️ Открыто; требуется решение владельца**
- Дата: 2026-08-17
- Trigger: [`FND-0065`](../findings/FND-0065-es8311-ce-and-differential-path.md)
- Evidence: [`AUDIO-0001`](../architecture/AUDIO-0001-es8311-exact-electrical-fit.md)
- Не меняет: S3 GPIO/I2S map, two slow selector controls, PTT independence

## Почему нужен выбор

Existing analog bypass is single-ended. Exact ES8311 DAC is differential
`OUTP/OUTN`. Мы можем сохранить принятые функции и safe defaults несколькими
способами, но у них разные BOM, качество, failure surface и объём HIL.

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

Both speaker legs switch as a pair between qualified analog bypass and
`OUTP/OUTN`; TX still gets a separate single-ended conditioner/selector.

- Плюсы: preserves differential DAC into the speaker branch; may avoid the
  central conversion stage for local playback.
- Минусы: at least three analog switch poles; legacy bypass/PAM input network
  must be redesigned; more routing and common-die/fault analysis; TX conversion
  remains, so total part saving is uncertain.
- Candidate switch: dual `TMUX1136DGSR` or `TMUX1136DQAR` for speaker plus
  `TS5A63157DCKR` for TX.

## Рекомендация

**A** is the conservative zero-functional-loss baseline. It preserves the
full ES8311 differential output and both hardware-default analog bypasses while
keeping the accepted two selector controls. The extra analog stage costs BOM
and power, but that cost is explicit and can be optimized after measured levels.
Option B is a cost-down experiment only; C is justified only if speaker-path
measurement shows A cannot meet noise/headroom or area goals.

## Acceptance after choice

The chosen option is still conditional on exact gain/common-mode calculations,
SA518/PAM8302 limits, off-state loading, power/reset defaults, pop/click and RF
HIL. No option allows codec state to assert PTT.
