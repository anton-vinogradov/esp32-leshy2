# Как проверяется железо R2 до изготовления

[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Параметры](parameter-model-register.ru.md) · [English](verification-methods.md)

Статус `H3-R2.0.3`: ✅ reviewed. Проверка R2 использует воспроизводимые worst-case методы, а не оптимистичные typical-значения. Каждый будущий результат обязан показать источники, состояния/corners, худший случай, численный запас и физический residual.

## Методы R2

| ID | Workstreams | Метод | Запрещённая подмена |
|---|---|---|---|
| `M-INT` | H3-R2.1, H3-R2.2, H3-R2.3, H3-R2.4, H3-R2.5, H3-R2.6 | deterministic interval/corner enumeration over authoritative min/max tolerances and legal discrete modes | typical values, undocumented defaults and Monte Carlo percentiles cannot prove pass |
| `M-DC` | H3-R2.1 | closed-form KCL/KVL, source ORing, conversion efficiency and dissipation envelopes for every legal source/load state | a hidden aggregate load or unexplained efficiency allowance is forbidden |
| `M-TRANS` | H3-R2.2, H3-R2.3, H3-R2.6 | bounded piecewise-linear or datasheet behavioral transient model with explicit initial conditions and dt versus dt/2 convergence | a plotted waveform without thresholds, input provenance and convergence margin is non-evidence |
| `M-STATE` | H3-R2.1, H3-R2.2, H3-R2.5, H3-R2.6 | deterministic state, arbitration, watchdog, reset, recovery and single-fault enumeration | a nominal happy path cannot close safety, quiet-state or ownership requirements |
| `M-ANALOG` | H3-R2.3 | bounded small-signal, gain, noise, bandwidth, loading and threshold equations with exact selected-part applicability | a family reference circuit cannot replace exact selected-value and load corners |
| `M-DIGITAL` | H3-R2.4 | VIH/VIL/VOH/VOL, leakage, pull, power-off, fanout, setup/hold and occupancy algebra for each endpoint and bus | logic-family names or nominal clock rates cannot replace endpoint limits and worst-case service time |
| `M-RF` | H3-R2.5 | source-to-port 50-ohm pre-layout loss/mismatch/isolation budget plus deterministic one-active-group and three-nRF service analysis | pre-layout work cannot claim final impedance, radiated performance, antenna match or coexistence; those remain H6/H8 |
| `M-THERMAL` | H3-R2.1, H3-R2.3, H3-R2.6 | worst-case dissipation with bounded junction/board/enclosure/cell thermal resistance and capacitance networks | unknown enclosure or interface resistance is a range, never a guessed scalar |
| `M-XCHECK` | H3-R2.7 | machine join from every frozen sheet, component, net, requirement and method result to one downstream physical residual owner | an unlinked pass, orphan input or unowned uncertainty cannot close H3 |

## Единые pass/fail rules

- `PF-R2-01` — Every normal and allowed degraded corner remains inside manufacturer recommended operating conditions; absolute maximum is never a design target.
- `PF-R2-02` — A missing min/max tolerance, applicability condition, unit or model provenance makes the owning result unresolved_fail.
- `PF-R2-03` — Steady rail/source current retains at least 25% reserve over enumerated worst-case load; a named transient-only rating requires separate transient proof.
- `PF-R2-04` — A regulated rail retains at least 5% nominal-voltage headroom after source tolerance, distribution loss and steady droop while every load stays in its supply range.
- `PF-R2-05` — Worst-case timing and shared-resource occupancy consume no more than 80% of the assigned deadline or service budget; independent buses are never combined artificially.
- `PF-R2-06` — Power-off, reset and quiet-state combinations cannot back-power or enable a transmitter; any allowed injection stays below the exact published limit with at least 2x analytical reserve.
- `PF-R2-07` — Predicted junction temperature stays at least 20 C below its applicable maximum; cell charge/discharge temperature stays at least 10 C inside exact cell and charger limits.
- `PF-R2-08` — Transient results at dt and dt/2 differ by no more than 10% of the remaining pass margin; otherwise the timestep is reduced or the result is unresolved_fail.
- `PF-R2-09` — Every single fault reaches a bounded-energy safe state without relying on the same failed compute domain, and a readable cause remains recoverable whenever energy remains.
- `PF-R2-10` — RF pre-layout pass means only a complete constraint and margin budget; final feed, antenna, VNA, spectrum and coexistence claims require H6/H8 evidence.
- `PF-R2-11` — Every calculator emits all evaluated states/corners, the worst case, numeric margin, outcome and physical residual; summary-only output is non-evidence.
- `PF-R2-12` — Input hash drift, tool-policy drift, a failed margin or an unowned residual invalidates acceptance and requires downstream regeneration.

## Воспроизводимость

Все `239` групп получили хотя бы один метод; используются `9` методов и `12` общих rules. Runtime — `Python 3.14.6`, только standard library, `Decimal` precision 50/Fraction, hash-bound JSON/CSV/SVG. Сеть, случайность и незакреплённый внешний solver не участвуют в acceptance.

## Что ещё не является pass

У `166` групп параметры ещё извлекаются из точных источников. Контракт метода закрыт, но их расчёты обязаны вернуть `unresolved_fail`, пока нет min/max, unit и applicability.

> Следующий шаг — H3-R2.1: power/DC/source/charge/state расчёты. Placement, routing, закупка и печать остаются запрещены.

[Машинный контракт методов и 239 назначений](../hardware/verification/generated/H3-R2-method-contract.json). Исторический `H3-VRF03` не является authority R2.
