# REV-0005E — DEC-0055 antenna-kit decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0055`](../decisions/DEC-0055-profiled-external-antenna-kit.md)
- Machine candidate: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)

## Проверенный результат

| Gate | Результат |
|---|---|
| owner choice | pass: `IMP-0043/A` принят полностью |
| port count | pass: девять независимых onboard SMA endpoints сохранены |
| kit identity | pass: shared exact MPN только для 2× native Wi-Fi и 3× nRF; остальные profiles разделены по диапазону/роли |
| physical count | pass: полный field kit = 12 items; максимум подключено одновременно = 9 |
| TX safety | pass at contract level: profile change disarms TX; unknown/mismatch keeps TX disabled |
| availability process | pass: stock lookup перенесён на gate выбора exact MPN, а не повторяется при каждом architecture pass |
| machine source | pass: JSON, validator, regression и generated ledgers несут `DEC-0055` |
| sourcing/HIL | open by design: exact MPN, alternates, feeds, VNA/EIRP/sensitivity/coexistence и environmental HIL остаются `FND-0058` |

## Boundary

Ревью закрывает выбор структуры комплекта и его propagation. Оно не выбирает
фабрику, не замораживает exact MPN и не разрешает production BOM. Возможность
заказать PCBA и loose antennas одним комплектом отдельно проверена в
[`MFG-0001`](../architecture/MFG-0001-one-stop-pcba-antenna-kitting.md).

