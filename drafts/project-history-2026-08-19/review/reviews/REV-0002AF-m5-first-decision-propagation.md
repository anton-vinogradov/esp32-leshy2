# REV-0002AF — распространение решения M5-first / separate high-speed

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Решение: [`DEC-0034`](../decisions/DEC-0034-m5-first-two-tier-expansion.md)
- Requirement: [`REQ-EXT-0001`](../requirements/REQ-EXT-0001-m5-first-expansion-platform.md)

## Проверка

| Проверка | Результат |
|---|---|
| Вариант B записан без наследования legacy owner/pin layout | да |
| Unit, Cap и M5-Bus не смешаны | да |
| Full U214 Cap contract сохранён | да |
| Native 30-pin M5-Bus не обещан | да |
| High-throughput tier сохранён отдельно | да |
| Exact USB role/connector не выбран преждевременно | да; `W-EXTRA-16` открыт |
| Safety/power/backfeed/STOP/update boundaries сформулированы | да |
| Hardware/Firmware, target/current-state, EN/RU распространены | да |
| Новые catalog-функции не приняты молча | да |

Later scope correction `DEC-0039` rejects generic `W-EXTRA-16`, removes the
former FIDO target and retains only profile-derived high-throughput transport.
This review remains the historical propagation record of `DEC-0034`.

## Итог

`IMP-0028` закрыт вариантом B, а `REQ-EXT-0001` получает статус **«Проведено
ревью требований»**. Это закрывает infrastructure-вопрос, но не весь G2:
At this historical point `W-EXTRA-12..17` still required sequential decisions.
Their current disposition is canonical in `INV-0002/INV-0004`.
