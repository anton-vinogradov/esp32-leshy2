# REV-0005Q — battery-format decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0062`](../decisions/DEC-0062-individually-replaceable-2s-cells.md)
- Proposal: [`IMP-0052`](../improvements/IMP-0052-safe-field-replaceable-2s-pack.md)

## Reviewed propagation

| Check | Result |
|---|---|
| retained behavior | pass: both 18650 cells remain individually accessible/replaceable |
| arbitrary-pair overclaim | pass: unknown/mismatched pair is refused before CHG/DSG enable |
| reverse insertion | pass at architecture boundary: must be mechanically open before manager pins; exact contact HIL remains |
| one-cell replacement | pass: allowed only after complete pair admission, never by force balancing |
| removal/bounce | pass as assigned proof: no reverse charge/re-arm/backfeed; early warning/hold-up shared with I4 |
| rear U214 | pass: dock remains, exact safe access/clearance returns in integrated mechanics |
| old power source | pass: decision does not revive BQ25887/S-8252A/ordinary holder |
| next dependency | pass: charger/power-path choice can proceed in `PWR-0003/IMP-0053` |

## Result

`IMP-0052/B` is consistently propagated. Battery mechanics and exact parts are
still open proofs, but battery product behavior is no longer ambiguous.

