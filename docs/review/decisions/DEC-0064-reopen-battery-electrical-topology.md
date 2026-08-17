# DEC-0064 — reopen the two-cell electrical topology

- Статус: **Завершено выбором supervised 2S в `DEC-0065`**
- Дата: 2026-08-18
- Reopens: [`DEC-0062`](DEC-0062-individually-replaceable-2s-cells.md), item 1 only
- Comparison: [`PWR-0006`](../architecture/PWR-0006-one-or-two-cell-topology-comparison.md)
- Owner gate: [`IMP-0055`](../improvements/IMP-0055-battery-electrical-topology-after-reopen.md)
- Propagation review: [`REV-0005S`](../reviews/REV-0005S-battery-topology-reopen-propagation.md)
- Final decision: [`DEC-0065`](DEC-0065-supervised-2s-battery-topology.md)

## Decision

1. The product still has two physical, individually accessible and replaceable
   qualified 18650 slots. The product/safety intent of items 2–8 and the reopen
   rule in `DEC-0062` remain requirements; their series-specific words
   `pair`, common pack FET and balancing are superseded as described below.
2. The previous mandatory `2S` electrical arrangement is no longer an input.
   It becomes one candidate to compare against a controlled two-slot `1S`
   power bus and a one-slot `1S` cost-down variant.
3. Directly paralleling two removable cells is not a candidate. A two-slot
   `1S` topology must isolate both slots, observe each cell before connection,
   bound precharge/equalization and prevent either cell from charging the
   other after any reset, insertion, removal or host fault.
   One already admitted slot may operate alone; the second slot is evaluated
   before its own path may join the common bus.
4. One-cell operation is now a scored property, not an accepted requirement.
   It may not silently remove runtime, peak-load, replacement, recovery or
   safety guarantees.
5. Exact `BQ25798RQMR` remains accepted because the physical device supports
   one to four series cells. Its final cell-count configuration, the cell
   manager and all downstream converters remain open until `IMP-0055` closes.
6. Target-product pages state only the stable result: two independently
   replaceable supervised slots. They do not advertise a provisional `2S` or
   `1S2P` implementation.

## Consequences

- `PWR-0005/IMP-0054` remain a reviewed **2S branch**, not the current owner
  gate and not authorization to select MAX17320.
- `PWR-0002/PWR-0004` keep their load and USB-PD evidence, but every statement
  that turns `2S` into an invariant is superseded by this decision.
- `I3` cannot close until one topology is selected and its complete charger,
  rail, protection, loss, thermal, removal and recovery tree is reviewed.
- The living diagram keeps two cell nodes and a generic supervised boundary;
  no speculative manager or converter MPN is added before the choice.

## Closure

The comparison requested here completed in `PWR-0006`; the owner selected
option A in `DEC-0065`. The temporary topology-neutral propagation is retained
as history, not as the current target.
