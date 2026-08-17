# FND-0062 — old 4-inch display fits the workload but not the accepted QSPI path

- Статус: **Открыто; target disposition требует решения `IMP-0045`**
- Серьёзность: exact display/interface/physical-design gate
- Обнаружено: 2026-08-17
- Decision: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md)
- Evidence: [`DSP-0003`](../architecture/DSP-0003-exact-fast-display-shortlist.md)

## Находка

Старый 4-inch Elecrow/MSP4031-class module остаётся функционально пригодным
для menu и dirty-row waterfall: `DEC-0043` не требует video/full-frame rate.
Но exact ST7796S module выводит только обычный 4-wire **1-bit SPI**. Он не может
использовать принятые `DEC-0052` линии D2/D3 и не даёт QSPI headroom.

Надпись `SPI+RGB` на распространённых 4-inch square ST7701S panels ситуацию не
исправляет: SPI служит для commands/configuration, а continuous pixels идут по
24-bit RGB. Текущий S3 pin budget такую шину не вмещает.

Проверенные готовые 4-inch host-QSPI modules используют BT817 EVE. Они
технически работают, но добавляют display coprocessor, существенно повышают
цену и/или ширину корпуса. Это fallback `DEC-0052`, а не zero-loss direct-QSPI
эквивалент старого portrait module.

## Критерий закрытия

Владелец выбирает disposition из `IMP-0045`: новый 3.5-inch portrait QSPI
target class, дорогой 4-inch EVE либо возврат к старому 1-bit target с явным
пересмотром `DEC-0052`. Старый 4-inch module можно сохранить как A0 control/
compatibility HIL независимо от target choice.
