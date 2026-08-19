# FND-0082 — TPUL package map and repeat-pulse safety were incomplete

- Статус: **Исправлено на бумажном уровне; pulse/thermal HIL gate сохранён**
- Дата: 2026-08-18
- Correction: [`PWR-0017`](../architecture/PWR-0017-hardware-diagnostic-refractory-lockout.md)
- Decision: [`DEC-0078`](../decisions/DEC-0078-hardware-diagnostic-refractory-lockout.md)
- Review: [`REV-0005AI`](../reviews/REV-0005AI-diagnostic-lockout-propagation.md)

## Finding

The `TPUL2G223BQBR` machine record assigned `VCC` to physical contact 5 and
`2Q` to physical contact 16. The January-2026 TI WQFN-16 table states the
opposite: `2Q` is contact 5 and `VCC` is contact 16. The functional net names
looked plausible, but the physical package projection was not buildable.

The prior circuit also proved only the maximum duration of one pulse. Channel
1 is non-retriggerable while active, but it becomes ready again immediately
after its RC interval. Faulty or hostile firmware could therefore emit a dense
sequence of individually valid pulses. At the upper screen voltage the old
10-Ohm load instantaneously dissipated about 7.8 W, so a firmware-only cooldown
was not an independent safety boundary for the 1-W load part.

## Correction

- physical contact 5 is now `CH2_Q` and contact 16 is `VCC`, with regression
  assertions for both contacts;
- the already present second TPUL channel is no longer disabled;
- falling `CH1_Q` at the natural end of a pulse starts channel 2;
- `CH2_Q_N` asynchronously clears channel 1 throughout an exact
  `620 kOhm / 1 uF` refractory interval;
- even a stuck-high trigger can produce only one bounded channel-1 pulse after
  each hardware lockout, because clear release is itself gated by the TPUL
  truth table;
- the single 1-W load is replaced by two exact parallel 20-Ohm/2-W pulse-rated
  resistors, preserving a 10-Ohm nominal load while splitting heat;
- firmware adds a longer 10-second operational cooldown, but no safety proof
  depends on firmware honoring it.

Paper timing includes IC, resistor, capacitor, temperature and TDK 3.3-V
DC-bias loss and yields a conservative channel-2 minimum above 350 ms and an
upper value below the TPUL 860-ms recommended range. Lot timing, repeated
triggers, hot copper and enclosure temperature remain production HIL gates.

