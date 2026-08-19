# IMP-0052 — safe field-replaceable 2S battery boundary

- Статус: **Принят вариант B как `DEC-0062`; проведено ревью propagation**
- Дата: 2026-08-18
- Context: [`PWR-0002`](../architecture/PWR-0002-i3-power-prerequisite-audit.md)
- Finding: [`FND-0073`](../findings/FND-0073-legacy-power-is-not-a-current-target.md)
- Affects: battery mechanics, protection/gauge, connector, charger, rear U214
  clearance, certification and field service

## Context

Legacy mockup contains an additional product behavior absent from the reviewed
wishlist wording: two individual 18650 cells are exposed in an open rear holder
and may be replaced separately. It may be intentional rather than excess, so
`I3` cannot silently delete it.

All options keep `2S / 6.0…8.4 V`, roughly the same two-cell rear volume and the
accepted U214 dock above the battery region. They differ in what the user may
replace and which fault states the base device must survive.

## Options

### A — keyed removable matched 2S assembly — recommended

- two matched cells are welded/assembled and replaced together;
- keyed touch-safe connector exposes pack power plus the exact sense/NTC/ID
  contacts required by the accepted gauge/protection topology;
- pack can remain field-replaceable and use the rear cradle, but random loose
  cells cannot be mixed or reversed;
- exact first pack SKU, connector, retention and component-level safety evidence
  are selected with the power tree and later checked against the mockup.

This preserves runtime, 2S efficiency and field replacement while removing the
highest-risk insertion/mismatch states. It adds pack sourcing/assembly cost and
the user replaces a pair rather than one commodity cell.

### B — retain two independently replaceable 18650 cells

- preserves the legacy open-holder experience and commodity-cell replacement;
- requires keyed/recessed per-cell mechanics, per-cell polarity fault analysis,
  explicit same-model/age/SOC policy, protection before unsafe fault energy,
  single-cell removal/insertion tests and a safe response to one reversed cell;
- increases hardware, warning, certification and HIL burden; cell balancing
  cannot make an arbitrary mismatched pair equivalent to a matched pack.

This option is feasible only as a consciously accepted product feature, not a
free mechanical choice.

### C — sealed/internal fixed 2S pack

- simplest user-safety boundary and easiest pack qualification;
- loses field replacement, complicates end-of-life/service and is unnecessary
  if option A fits the rear cradle.

## Recommendation

Choose **A**. It retains the useful field-replaceable behavior without treating
two arbitrary high-energy cells as a self-validating pack. Option B should be
chosen only if separate commodity-cell replacement is itself a required Leshy2
capability.

## Owner decision

Владелец выбрал **B**. Две банки остаются физически отдельно заменяемыми.
Решение не принимает произвольное смешивание ячеек: допуск конкретной пары,
механическое исключение reverse insertion, pre-connect измерение, one-cell
remove behavior и protected charge/discharge являются обязательной частью I3.
Зафиксировано в [`DEC-0062`](../decisions/DEC-0062-individually-replaceable-2s-cells.md).
