# REV-0005I — DEC-0057 U214 rear-dock decision propagation

- Статус: **Проведено ревью решения; exact mechanics/HIL открыты**
- Дата: 2026-08-17
- Decision: [`DEC-0057`](../decisions/DEC-0057-u214-rear-dock-above-batteries.md)
- Mechanical facts: [`MEC-0001`](../product-design/MEC-0001-u214-cap-bus-mechanical-interface.md)

## Проверенный результат

| Gate | Результат |
|---|---|
| owner decision | pass: option D accepted explicitly |
| proposal | pass: `IMP-0048` closed as accepted D |
| physical artifact | pass: `PHY-0001` identifies rear-above-battery D as active working layout |
| legacy collision | pass: old encoder placement remains rejected/visible |
| nine top SMA | pass: five RF-board keep-outs checked, four UI-board ports unaffected |
| exact interface facts | pass: `MEC-0001` records male/female `2×7 2.54-mm`, two M2/56-mm retention and official generic schematic identity |
| orderable host connector | open: official MPN/stack-up absent; `FND-0069` created |
| firmware contract | no delta: U214 ownership/signals/power policy are unchanged by physical placement |

## Conclusion

Placement choice is closed and propagated without converting paper fit into
false production sign-off. Exact connector/rail/screw data and installed-cap
HIL remain explicit downstream prerequisites.
