# REV-0005H — U214 rear-dock paper-fit review

- Статус: **Проведено ревью paper fit; решение placement и HIL открыты**
- Дата: 2026-08-17
- Artifact: [`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md)
- Proposal: [`IMP-0048`](../improvements/IMP-0048-u214-dock-versus-sma-placement.md)

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
| production mechanics | open: exact header MPN, boss pitch/height, wall/rail, retention and specimen measurement |
| installed accessory | open: hand, desk, GNSS sky-view, LoRa/RF coexistence, connector/cable bend and drop/strain HIL |

## Review conclusion

Rear-above-battery D is mechanically credible enough to become the recommended
active-layout candidate. It is not an enclosure decision: the failed legacy
encoder placement and every exact-mechanics/HIL gate remain visible.
