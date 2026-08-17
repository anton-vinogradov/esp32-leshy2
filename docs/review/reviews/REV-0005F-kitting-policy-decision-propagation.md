# REV-0005F — DEC-0056 kitting-policy decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0056`](../decisions/DEC-0056-prefer-one-stop-kitting-with-fallback.md)
- Proposal: [`IMP-0047`](../improvements/IMP-0047-one-stop-pcba-antenna-kitting-policy.md)

## Проверенный результат

| Gate | Результат |
|---|---|
| owner choice | pass: вариант B принят явно |
| supplier freedom | pass: one-stop preference не исключает более выгодный/надёжный separate flow |
| kit integrity | pass: exact MPN, no-substitution, labels, traceability and incoming inspection сохраняются в обоих flows |
| RF boundary | pass: factory kitting не считается VNA/EIRP/sensitivity/coexistence qualification |
| architecture impact | none: `DEC-0055` antenna profiles/count and nine device ports unchanged |
| firmware impact | none: runtime antenna identity and TX interlock unchanged |
| RFQ readiness | deferred correctly: quantity, exact MPN and quotations follow product/BOM closure |

## Boundary

Решение закрывает supplier policy, но не выбирает supplier. Следующий активный
этап остаётся G3: адаптация legacy clamshell generator к текущему exact-device
и principled-pinout source.

