# BOM-0028 — consolidated I8 paper procurement-feasibility review

- Статус: **проведено ревью I8 paper feasibility; not target/frozen BOM**
- Дата: 2026-08-19
- Boundary correction: [`FND-0115`](../findings/FND-0115-i8-exit-mixed-g2f-with-downstream-g8.md)
- Review: [`REV-0005CC`](../reviews/REV-0005CC-i8-consolidated-paper-procurement-propagation.md)

## Consolidated result

| Prerequisite | Проверенный результат | Незакрытый downstream gate |
|---|---|---|
| physical inventory | 858 architecture nodes; one assembly-internal COG excluded; 857 supplied placements / 187 purchase lines | G4…G7 resynthesis may change the candidate |
| current source route | 186/187 used lines have dated orderability evidence; standalone `HMX035CTFT-001` has an exact raw-panel RFQ/no-drop-in gate and an orderable donor/specimen path | execute standalone RFQ at target BOM freeze |
| comparable component cost | 175/187 lines / 829 placements; USD 157.3727 partial base material | twelve explicit RFQ/retail gates; PCB/PCBA/test/enclosure/logistics/factory COGS in G8 |
| substitution boundary | 187/187 lines have exactly one conservative no-silent-substitution class | qualify named alternates only against the selected G7 architecture |
| physical purchase families | 4/4 families / 28 items have machine-readable owner, prerequisites and acceptance | G3 connector plane, received mates, coupons, exact MPN/drawings and assembled HIL |
| architecture impact | none: candidate owner/pin/net/rail/RF/diagram projection unchanged | I9 must still prove joint consistency |

## Why this is a pass

There is no anonymous or zero-valued procurement uncertainty left. Every
unknown is either a dated used-line gate or a physical-family resolution
contract. The evidence is sufficient to answer the G2F question — whether the
working electrical candidate has a credible, auditable procurement path —
without pretending to answer the later G8 question of what the final frozen
product BOM and factory COGS will be.

## What this pass does not authorize

- it does not accept `G2F-3I` as the target or atomic architecture;
- it does not freeze any connector footprint, harness length or antenna kit;
- it does not claim twelve missing numeric prices, 187 named second sources or
  complete factory COGS;
- it does not authorize KiCad, PCB or fabrication;
- a G3…G7 change to function, owner, device, quantity, physical interface or
  qualification envelope reopens the affected I8 evidence before G8.

I8 receives **«Проведено ревью» in paper procurement-feasibility scope**. I9
joint internal self-review is the next active prerequisite before the paused
integrated product mockup resumes.

Successor note: `FND-0116/I9-0001/REV-0005CD` later complete that prerequisite;
G3 is now active. This does not change the I8 evidence boundary above.
