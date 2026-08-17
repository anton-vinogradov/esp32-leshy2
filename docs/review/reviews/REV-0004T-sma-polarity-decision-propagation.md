# REV-0004T — SMA polarity decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0050`](../decisions/DEC-0050-ecosystem-aligned-sma-polarity.md)
- Evidence: [`RFH-0002`](../architecture/RFH-0002-antenna-connector-ecosystem-review.md)
- Proposal: [`IMP-0042`](../improvements/IMP-0042-external-sma-gender-and-feed-policy.md)

## Проверено

| Область | Результат |
|---|---|
| Decision ledger | exact device-side и detachable-mate contact convention записана для девяти identities |
| Machine source | все три G2F candidates содержат `2 RP-SMA + 7 standard SMA`, two-source gate и identification controls |
| Validator | отклоняет drift решения, path polarity/mate map и ослабление qualification gate |
| Generated ledger | печатает RP-SMA и standard-SMA path groups и fallback gate |
| Target/current docs | открытый `IMP-0042` заменён принятым `DEC-0050` |
| Firmware input | polarity сохраняется как assembly metadata; девять runtime identities не меняются |
| Scope guard | решение не замораживает antenna MPN, mount, pigtail length или physical placement |

## Результат

Распространение `DEC-0050` получает **«Проведено ревью»**. Следующий prerequisite
— current-orderable exact antenna shortlist по каждой antenna group; только
после него допустимы connector/harness BOM freeze и physical co-design.
