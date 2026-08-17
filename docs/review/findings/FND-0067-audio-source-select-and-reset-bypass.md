# FND-0067 — audio source select was missing and expander controls do not reset with S3

- Статус: **Частично исправлено; reset-bypass owner decision открыт**
- Серьёзность: architecture/safety/pin-accounting blocker
- Обнаружено: 2026-08-17
- Artifact: [`AUDIO-0002`](../architecture/AUDIO-0002-complete-audio-path-comparison.md)
- Proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)

## Находка 1 — пропущен existing RX mux control

`DEC-0009` retains the existing analog mux between Si4732 mono audio and SA518
AFOUT. `G2F-3I` represented both receiver outputs and two new codec selectors,
but did not allocate the mux's own `MUX_SEL` control. The GPIO/slow budget was
therefore incomplete by one required wishlist signal.

## Исправление 1

The last controlled slow-plane reserve, TCA6424A `P27`, now carries
`RX_AUDIO_SOURCE_SEL`. It is ordinary source selection, not PTT or a safety
deadline, so the slow plane is appropriate. Accounting changes from
`23U/1R/0F` to `24U/0R/0F`; S3/C5/RP budgets do not change.

## Находка 2 — safe pulls do not override stale expander outputs

`AUDIO_SEL0/1` currently originate from TCA6424A `P11/P12`. The expander powers
up as inputs, so external pulls do establish the initial state. But an S3 reset
does not power-cycle or reset the expander. If P11/P12 were already outputs in
codec position, they may continue driving that position through S3 reset. This
violates the accepted requirement that reset/watchdog/codec failure returns
speaker and TX-audio selection to ordinary analog paths.

## Leading closure

Use one direct S3 `GPIO6 / AUDIO_ARM` with a bypass-safe pull-down and gate both
P11/P12 requests through an always-powered dual logic gate. `AUDIO_ARM=0`
forces both selectors to analog default independently of stale I2C state.
GPIO43 remains free. Exact logic polarity, power rail and stuck-fault tests are
part of `IMP-0046/AUDIO-0002`; no machine-map allocation is made before owner
acceptance.

## Closure evidence

1. Owner accepts one complete `IMP-0046` path including its control topology.
2. Machine map allocates direct `AUDIO_ARM` and exact logic endpoint.
3. Oscilloscope proof covers power-on, S3 reset, brownout, watchdog, I2C stuck,
   codec-off and stale P11/P12 while both analog defaults remain usable.
4. TX selector state never asserts PTT and STOP dominance is unchanged.

