# REV-0003W — first G3 form-factor candidate review

- Статус: **Проведено ревью артефакта; downstream direction superseded DEC-0041**
- Дата: 2026-08-17
- Input: [`PD-0001`](../product-design/PD-0001-g3-physical-design-inputs.md)
- Output: [`LAY-0001`](../product-design/LAY-0001-form-factor-candidates.md)

## Проверка

| Проверка | Результат |
|---|---|
| At least three materially different physical candidates | да |
| Same capability/exclusion scope in all three | да |
| U214 fits the stated 84 mm product width | да; exact connector alignment later |
| Attached Unit/antenna/cable envelope made visible | да |
| RF, battery, service and controls shown together | да |
| Working dimensions called exact or final | no |
| Electronics zone mistaken for component placement | no |
| One candidate silently selected | no |

## Result

The first visual artifact receives **«Проведено ревью артефакта»**. P2 is the
former engineering recommendation, P1 is the aggressive compact bound, and P3
is the service/RF upper bound.

The owner then clarified that logical owner/bus/exact-exposed-pin feasibility
and reuse of the legacy reproducible mockup must come first. `DEC-0041` removes
the open P1/P2/P3 selection. This review remains valid only as a check of what
the drawing depicts; it does not authorize its process direction.
