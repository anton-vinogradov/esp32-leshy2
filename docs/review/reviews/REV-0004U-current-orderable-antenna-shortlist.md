# REV-0004U — current-orderable antenna shortlist fact review

- Статус: **Проведено ревью фактов; architecture decision и qualification открыты**
- Дата: 2026-08-17
- Evidence: [`ANT-0002`](../architecture/ANT-0002-current-orderable-antenna-shortlist.md)
- Finding: [`FND-0058`](../findings/FND-0058-antenna-sourcing-and-qualification-gate-open.md)
- Proposal: [`IMP-0043`](../improvements/IMP-0043-profiled-antenna-kit.md)

## Проверено

| Область | Результат |
|---|---|
| Connector convention | каждый candidate соответствует принятому `2 RP-SMA + 7 standard SMA` external mate class |
| Native Wi-Fi | один dual-band MPN может обслуживать S3/C5, exact stocked alternate найден, published gain остаётся в module bounds |
| Three nRF | один MPN ×3 сохраняет три independent paths; Ebyte source mismatch и two-stock-source proof открыты |
| Sub-GHz | universal 315–915 no-loss claim отклонён; отдельные 315/433 profiles и combined 868/915 candidate сформированы |
| Voice | full 136–174 и 400–470 MHz current antennas найдены, но это две сменные antennas одного port |
| Si4732 | FM/SW whip и AM/LW loop/pod остаются разными electrical domains; receiver two-source gate не закрыт |
| Cost | shared Wi-Fi/nRF SKUs и combined 868/915 сокращают позиции без удаления функции; universal compromise не назван экономией |
| Safety | SMA не считается identity sensor; profile change disarms TX, unknown/mismatch keeps TX disabled |
| Scope | MPN являются sourcing/HIL candidates, а не frozen BOM или разрешением TX |

## Результат

Fact review и формирование shortlist получают **«Проведено ревью»**. Проверка
одновременно исправляет прежнюю слишком сильную формулировку: shortlist не
закрывает production qualification. `FND-0058` остаётся открытым до exact
two-source assemblies и target HIL. Следующий переход требует решения владельца
по `IMP-0043`; machine architecture и target product contract до решения не
меняются.
