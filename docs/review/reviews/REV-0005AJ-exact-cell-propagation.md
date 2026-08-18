# REV-0005AJ — exact-cell propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0079`](../decisions/DEC-0079-xtar-18650-4000mah-qualification-target.md)
- Analysis: [`PWR-0018`](../architecture/PWR-0018-xtar-18650-4000mah-cell-profile.md)
- Finding: [`FND-0083`](../findings/FND-0083-generic-cell-placeholder-blocked-real-limits.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Exact physical devices | two separate `XTAR 18650 4000mAh` instances replace both `MPN TBD` cell nodes |
| Electrical source | each instance exposes only exact positive button-top and negative end contacts into its own 1048P slot |
| Capacity | `4000 mAh` typical / `3800 mAh` minimum; pair is `28.8 Wh` nominal |
| Load fit | 10-A rating has paper margin over 2.22-A continuous / 2.78-A transient per series cell |
| Charge | 2-A product ceiling equals standard cell charge; reset remains 1 A and runtime may derate only downward |
| Protection hierarchy | 11…14-A cell trip does not remove either 5-A slot fuse, MAX17320 protection or fail-closed admission; time-current coordination remains HIL |
| Temperature | charge blocked outside 0…45 °C pending exact assembly evidence; all three NTC paths remain mandatory |
| Mechanics | max 18.7×69.7-mm model propagated; exact holder insertion/retention and sensor pressure remain specimen gates |
| Supply identity | exact manufacturer/model/source plus packaging/lot identity recorded because XTAR publishes no separate order code; raw, USB-equipped and third-party protected variants remain unsupported |
| Certification | exact assembly UN38.3/test-summary identity remains a hard regional-kit gate and is not inferred from CE/RoHS |
| Product pages | exact model, 28.8-Wh pair and separate physical diagram nodes appear in both target languages |
| Firmware | exact capacity/current/temperature identity and fail-closed document/lot state become runtime inputs |

## Remaining gates

Obtain the exact assembly certification package and at least two received lots;
measure cell/holder fit, protection trip, new/aged droop distributions, all
three sensor responses and charge/load thermal behavior. Derive production
thresholds from those results. The exact first target receives **«Проведено
ревью»** at paper level and does not authorize KiCad.
