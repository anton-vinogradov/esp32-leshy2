# REV-0004M — G2F-3I RF concurrency fact review

- Статус: **Проведено ревью фактов/policy; physical measurements open**
- Дата: 2026-08-17
- Finding: [`FND-0053`](../findings/FND-0053-arbitrary-colocated-rf-concurrency-is-impossible.md)
- Artifact: [`RFQ-0002`](../architecture/RFQ-0002-g2f-3i-rf-concurrency-boundary.md)

## Проверки

| Проверка | Результат |
|---|---|
| S3 Wi-Fi/BLE are independent simultaneous RF chains | no; official coexistence is TDM over one 2.4 GHz RF module |
| C5 2.4/5/802.15.4 are independent simultaneous RF chains | no; exact device is 1T1R and official coexistence arbitrates one RF resource |
| three nRF are independent physical radios | yes as architecture demand; exact production modules/antennas remain open |
| current compact E01 reference power/sensitivity | official vendor data: 0 dBm / approximately −93 dBm at 250 kbit/s |
| CC overlaps U214 | yes: CC 779–928 MHz and U214 868–923 MHz |
| CC overlaps preferred voice backend | yes: CC 387–464 MHz and SA518 UHF 400–470/480 MHz |
| local spacing alone proves weak-signal concurrency | no; optimistic 150 mm screening leaves roughly 69…137 dB between coupled local-TX order and sensitivity floor for critical overlap examples |
| same-band filter can guarantee arbitrary same-channel TX↔RX | no; it cannot reject the local interferer without rejecting the wanted same-frequency signal |
| 3×nRF arbitrary simultaneous PTX/PRX roles are digitally feasible | yes; dedicated bus/PIO/DMA/CE/IRQ resources do not require peer standby |
| local nRF TX preserves arbitrary same/near-channel weak RX sensitivity | no universal guarantee; `DEC-0047` selects qualified points measured by `N24H-0001` HIL |
| arbitrary all-radio concurrency remains feasible target | no; visible qualification/time-sharing or external fixture is required |

## Найденное несоответствие

Фраза «каждое радио работает без тормозов из-за соседей» могла быть неверно
расширена с digital scheduling на arbitrary electromagnetic concurrency.
`NIF-0001` теперь явно ограничен digital non-interference, а `RFQ-0002`
фиксирует отдельную physical boundary. Ни один status не выдаёт paper bus map
за доказанную sensitivity рядом с local TX.

## Review boundary

Проведено ревью диапазонов, native shared-chain limits, screening порядка
изоляции и cross-group policy. После прямой поправки владельца прежний split
`SG-N24-HUNT/SG-N24-TX` признан несоответствием и удалён. `DEC-0045` теперь
требует один `SG-N24` с любым одновременным PTX/PRX mix, а `DEC-0046` — quiet
state всех неиспользуемых interfaces. Antenna MPN/coordinates, filters,
shields и conducted/OTA measurements остаются открыты. `DEC-0047` принимает
qualified envelope и staged `L0 DIV↔DIV` pre-HIL / target `T1` plan
`N24H-0001`; поэтому policy
проверена, но physical nRF mix ещё не получает status «Проведено ревью».
