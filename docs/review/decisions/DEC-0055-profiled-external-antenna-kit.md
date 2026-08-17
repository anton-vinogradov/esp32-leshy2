# DEC-0055 — profiled external antenna kit

- Статус: **Принято владельцем; architecture propagation проведено ревью**
- Дата: 2026-08-17
- Owner answer: `A` / проверять доступность только при выборе exact MPN
- Proposal: [`IMP-0043`](../improvements/IMP-0043-profiled-antenna-kit.md)
- Facts: [`ANT-0002`](../architecture/ANT-0002-current-orderable-antenna-shortlist.md)
- Propagation review: [`REV-0005E`](../reviews/REV-0005E-antenna-kit-decision-propagation.md)

## Решение

Девять независимых onboard SMA endpoints сохраняются. Полный полевой комплект
содержит 12 сменных antenna items:

| Порт/группа | Принятый профиль комплекта | Количество |
|---|---|---:|
| `S3-2G4`, `C5-2G4/5` | один общий exact dual-band RP-SMA MPN | 2 |
| `N24-0/1/2` | один общий exact 2.4-GHz standard-SMA MPN | 3 |
| `CC-SUB` | отдельные 315 MHz, 433 MHz и combined 868/915 MHz | 3 |
| `VOICE-V/U` | отдельные full-range VHF 136–174 и UHF 400–470 MHz | 2 |
| `RX-FM/SW` | telescopic whip profile | 1 |
| `RX-AM/LW` | direct loop либо qualified buffered pod profile | 1 |

Одновременно подключается не более девяти items. Общий MPN применяется только
к электрически эквивалентным путям; решение не превращает разные диапазоны в
фиктивную universal antenna.

## Runtime safety

Смена `CC-SUB` или `VOICE` profile немедленно сбрасывает TX arm. Оператор
выбирает exact antenna identity и подтверждает физическую установку. Unknown,
mismatched, expired или unqualified identity оставляет TX disabled. Цвет,
маркировка и QR помогают оператору, но не считаются автоматическим
электрическим распознаванием.

## Availability и BOM boundary

Текущие exact MPN из `ANT-0002` остаются датированными specimen candidates, а
не frozen BOM. Во время дальнейшей архитектурной работы stock не опрашивается
повторно. Availability проверяется в момент выбора exact MPN; при фактическом
размещении заказа выбранная строка BOM неизбежно проходит обычную закупочную
проверку поставщика.

До выбора MPN остаются открытыми exact antenna/feed/harness assemblies,
alternate sources, механика, VNA, sensitivity, EIRP, coexistence, regulatory и
environmental HIL из `FND-0058`. Вопрос base/extended комплекта отложен до
costed product variants.

