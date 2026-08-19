# REV-0005S — battery-topology reopen propagation

- Статус: **Проведено ревью; historical intermediate, A later accepted DEC-0065**
- Дата: 2026-08-18
- Decision: [`DEC-0064`](../decisions/DEC-0064-reopen-battery-electrical-topology.md)
- Comparison: [`PWR-0006`](../architecture/PWR-0006-one-or-two-cell-topology-comparison.md)

## Review matrix

| Check | Result |
|---|---|
| owner intent | pass: electrical topology reopened; two physical replaceable slots and safety behavior retained |
| direct parallel | rejected explicitly; controlled isolation/admission required |
| energy/current arithmetic | pass: equal Wh and ideal per-cell current shown; 1S common-current penalty calculated |
| charger compatibility | pass: exact BQ25798 remains physically valid for 1–4 cells; configured count reopened |
| complete rails | pass at architecture class: 2S buck versus 1S buck-boost/boost consequences named; exact selections remain after owner choice |
| one-cell behavior | explicit: B supports it, A does not, C deletes the second slot |
| cost | direction and uncertainty explicit; controlled two-slot 1S is not claimed as cost-down |
| target product pages | stable two-slot behavior retained without publishing an unselected electrical topology |
| firmware input | generic per-slot/admission states propagated; no manager driver frozen |
| prior artifacts | DEC-0062 item 1 and series-specific wording in items 5–8 superseded; IMP-0054 closed as a 2S branch; safety intent retained |

## Result

The reopen is internally consistent and does not erase earlier loose-cell
safety findings. `I3` remains active. No new manager, converter or cell MPN is
accepted and no KiCad work is authorized. The next action is the single owner
choice in `IMP-0055`.
