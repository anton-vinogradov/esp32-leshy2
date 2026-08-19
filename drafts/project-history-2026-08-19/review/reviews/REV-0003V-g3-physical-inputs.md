# REV-0003V — G3 physical-product input review

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Input: repeated G2 closure `REV-0002AS`
- Output: [`PD-0001`](../product-design/PD-0001-g3-physical-design-inputs.md)

## Проверка

| Проверка | Результат |
|---|---|
| Same reviewed capability target used | да |
| Local field/safety/recovery works without phone | да |
| STOP/PTT/RE-ARM treated as mechanics, not UI decoration | да |
| U214 84×24×15.2 mm and Unit retention included | да |
| Three nRF sector identities retained | да |
| RF/body/antenna/service/battery drivers included | да |
| Rejected features reserve hidden volume/resources | no |
| Compute owner, components, buses or pins selected | no |
| Archived layouts consumed as target inputs | no |

## Result

`PD-0001` receives **«Проведено ревью входов»** and can feed G3 visual
candidates. It cannot feed G4 as a selected product until the physical
direction and surfaces receive owner/reviewed disposition.
