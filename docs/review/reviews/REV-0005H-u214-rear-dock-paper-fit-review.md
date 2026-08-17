# REV-0005H — U214 rear-dock paper-fit review

- Статус: **Проведено ревью paper fit; D принято, exact mechanics/HIL открыты**
- Дата: 2026-08-17
- Artifact: [`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md)
- Proposal: [`IMP-0048`](../improvements/IMP-0048-u214-dock-versus-sma-placement.md)
- Decision: [`DEC-0057`](../decisions/DEC-0057-u214-rear-dock-above-batteries.md)

## Проверенный результат

| Gate | Результат |
|---|---|
| reproducibility | pass: `hardware/product-design/u214_rear_fit.py --check` validates dimensions/collisions and generated SVG freshness |
| real-device shape | pass for source model: official U214/Cardputer-Adv STL alignment is L-shaped/edge-wrapping, not a flat header assumption |
| 75-mm board width | pass with explicit `4.5 mm` accessory overhang per side |
| five RF-board top SMA keep-outs | pass on scaled plan with `5.5 mm` remaining gap; four UI-board ports are separate and unaffected |
| battery-holder plan gap | pass with `9.719 mm` remaining gap |
| rear depth | pass on paper: U214 `15.11 mm` is within bare-18650 `18.6 mm` silhouette by `3.49 mm`; holder/wall tolerance is still open |
| legacy encoder | fail as inherited placement: collision is drawn and relocation is mandatory |
| production mechanics | partial: M2 centres are `56 mm` with `14-mm` end offsets; exact header MPN, boss/rail height, wall, screw engagement and specimen measurement remain open |
| installed accessory | open: hand, desk, GNSS sky-view, LoRa/RF coexistence, connector/cable bend and drop/strain HIL |

## Review conclusion

Rear-above-battery D passed paper review and is accepted by `DEC-0057`. It is
not enclosure sign-off: the failed legacy encoder placement and every
exact-mechanics/HIL gate remain visible through `MEC-0001/FND-0069`.
