# REV-0003E — финальное ревью power envelope и `VVOICE`

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Входы: `DEC-0016`, `DEC-0024`, owner acceptance `IMP-0023/A`, `BUD-0001`, SA518 v1.1 source table
- Выходы: `DEC-0025`, закрытый architecture gate `FND-0030`, полный numeric input layouts

## Проверки

| Проверка | Результат |
|---|---|
| Output class | 4.0 V соответствует принятому SA518 1 W-class; legacy 5 V не переименован в 1 W |
| Topology | при 2S `BAT=6.0–8.4 V` достаточно отдельного BAT-fed buck; boost/buck-boost не добавляется |
| Rating | `VVOICE` floor 1.25 A continuous / 1.5 A transient покрывает source-table peak с инженерным запасом |
| STOP | rail default-off, hardware power/inhibit и PTT-RX под `DEC-0024`; firmware не единственный kill path |
| Fallback | SA518 и SA868S не смешаны: отдельные stuffing descriptor, supply config, manifest и HIL |
| Rail math | 3.3 V, 5 V non-voice, `VVOICE` и 2S pack/protection ceilings сведены в `BUD-0001` |
| Propagation | target/current hardware+firmware, requirement, decision/finding/improvement и registry синхронизированы |

## Вывод

Power-подшаг и весь `BUD-0001` получают статус **«Проведено ревью»**. `DM-0001` теперь является полным неизменным входом для `LAY-S3`, `LAY-C5` и `LAY-BAL`; это не доказывает exact stage-4 BOM или legacy schematic.

