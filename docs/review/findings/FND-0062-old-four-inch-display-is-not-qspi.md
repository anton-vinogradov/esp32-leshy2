# FND-0062 — old 4-inch display fits the workload but not the accepted QSPI path

- Статус: **Закрыто `DEC-0053`; old 4-inch оставлен A0/control fixture**
- Серьёзность: exact display/interface/physical-design gate
- Обнаружено: 2026-08-17
- Decision: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md)
- Evidence: [`DSP-0003`](../architecture/DSP-0003-exact-fast-display-shortlist.md)
- Closure: [`DEC-0053`](../decisions/DEC-0053-new-35in-qspi-display-class.md)

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

## Закрытие

Владелец принял `IMP-0045/A` как `DEC-0053`: target — новый 3.5-inch portrait
QSPI class; старый 4-inch module сохраняется как A0 control/compatibility HIL,
а EVE — как high-end fallback. Exact production panel/connector остаются
отдельным sourcing/HIL gate и перечислены в `DSP-0004`.
