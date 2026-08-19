# REV-0004Q — nine-SMA decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
- Evidence: [`ANT-0001`](../architecture/ANT-0001-external-sma-path-inventory.md)
- Proposal: [`IMP-0041`](../improvements/IMP-0041-exact-external-sma-count.md)

## Проверено

| Область | Результат |
|---|---|
| Decision ledger | зафиксированы 9 identities и отдельные Si4732 `FMI`/`AMI` paths |
| Machine source | все три сравниваемые G2F maps содержат count=9 и одинаковый ordered identity set |
| Validator | отклоняет count drift, missing/reordered identities, shared Si switch и generic AMI coax profile |
| Generated artifact | antenna policy печатает total count, all identities и split Si topology |
| Target/current hardware docs | открытый 8-vs-9 вопрос заменён принятым 9-port boundary |
| Firmware input/docs | сохраняет разные runtime antenna profiles и запрещает считать `RX-AM/LW` generic coax port |
| Scope guard | решение не выдаёт connector/feed/frontend/placement или RF coexistence за закрытые |

## Результат

Распространение `DEC-0049` получает **«Проведено ревью»**. Следующий RF-
mechanical pass должен выбрать exact connectors/feeds/protection и antenna
profiles, не переоткрывая count без нового finding.
