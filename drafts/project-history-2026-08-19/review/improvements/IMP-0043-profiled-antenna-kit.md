# IMP-0043 — profiled external antenna kit

- Статус: **Принято как вариант A в DEC-0055**
- Дата: 2026-08-17
- Decisions: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md),
  [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md),
  [`DEC-0050`](../decisions/DEC-0050-ecosystem-aligned-sma-polarity.md)
- Evidence: [`ANT-0002`](../architecture/ANT-0002-current-orderable-antenna-shortlist.md)
- Finding: [`FND-0058`](../findings/FND-0058-antenna-sourcing-and-qualification-gate-open.md)
- Decision: [`DEC-0055`](../decisions/DEC-0055-profiled-external-antenna-kit.md)

## Текущее состояние и причина решения

Leshy2 имеет девять независимых external-SMA endpoints, но это не означает
девять уникальных antenna designs. Одновременно выяснилось, что один universal
radiator не покрывает без потерь 315/433/868/915 MHz и full
136–174/400–470 MHz. Нужно выбрать product rule до exact harness/mechanical
co-design: унифицировать одинаковые paths и менять antenna profile на одном
широкодиапазонном radio port либо требовать одну компромиссную antenna.

Датированная availability из `ANT-0002` не меняет architecture choice.
`DEC-0055` переносит следующую проверку наличия на момент выбора exact MPN;
production two-source qualification остаётся `FND-0058`.

## Вариант A — profiled kit с общей SKU только там, где это доказуемо

Рекомендуемый комплект:

- `2×` один dual-band RP-SMA MPN для `S3-2G4` и `C5-2G4/5`;
- `3×` один standard-SMA 2.4 GHz MPN для `N24-0/1/2`;
- для одного `CC-SUB` port: отдельные 315 и 433 MHz antennas плюс одна
  combined 860–928 MHz antenna для common 868/915 profiles;
- для одного `VOICE-V/U` port: отдельная full-band VHF и отдельная full-band
  UHF antenna;
- для `RX-FM/SW`: telescopic whip profile;
- для `RX-AM/LW`: dedicated short loop/pod profile.

Итого на устройстве остаются девять ports и максимум девять одновременно
подключённых antennas/pods. Полный field kit содержит 12 physical items, но
только 9 primary antenna SKU; объединение 868/915 удаляет одну SKU/item по
сравнению с полностью band-specific комплектом. S3/C5 и три nRF также
закупаются кратно из общих MPN, что снижает AVL, запасные части и риск
разносимметрии трёх nRF.

Цена: при переходе между `CC-SUB` bands или `VOICE` V/U пользователь меняет
antenna. SMA не умеет автоматически проверить её identity, поэтому профиль
выбирается явно, TX arm сбрасывается, а unknown/mismatch запрещает TX. Цвет,
надпись и QR помогают оператору, но не заменяют qualification.

## Вариант B — одна universal antenna на каждый physical port

Внешне проще и требует меньше предметов в коробке. Но найденные реальные
candidates не дают эквивалентного результата:

- compact 315–915 MHz antenna без заметного efficiency/matching компромисса не
  подтверждена;
- consumer dual-band VHF/UHF antennas часто покрывают amateur sub-bands, а не
  полные SA518 hardware ranges 136–174 и 400–470 MHz;
- неправильное согласование снижает receive sensitivity и может нарушить
  TX/EIRP/harmonic profile;
- экономия нарушает `DEC-0005`, пока equivalence не доказана измерениями.

Вариант не рекомендуется.

## Вариант C — положить только региональный/базовый subset, остальные optional

Архитектурно сохраняет все profiles, но уменьшает стартовую цену коробки:
например, shipped kit содержит 433 и региональную 868/915 antenna, а 315,
другой voice band и special RX pod заказываются отдельно. Это packaging/SKU
решение, а не zero-loss BOM saving самого устройства. Оно может ухудшить
восприятие `all-in-one`, поэтому его разумно принимать позже вместе с target
рынком и комплектациями, не смешивая с electrical architecture.

## Рекомендация

Принять **A** как architecture input, а вопрос base/extended packaging из C
отложить до costed product variants. Exact MPN из `ANT-0002` остаются
procurement candidates, не frozen BOM: все они обязаны пройти two-source и
assembled HIL gate из `FND-0058`.

## Решение владельца

Вариант **A** принят как [`DEC-0055`](../decisions/DEC-0055-profiled-external-antenna-kit.md),
включая обязательный TX interlock. Availability проверяется при выборе exact
MPN, а не при каждом следующем architecture pass.
