# FND-0064 — stage ledger сохранял pre-QSPI бюджет S3

- Статус: **Закрыто исправлением**
- Серьёзность: status/architecture inconsistency
- Обнаружено: 2026-08-17
- Исправление проверено: [`REV-0005A`](../reviews/REV-0005A-hmx-display-electrical-fit.md)

## Находка

`docs/review/stages.md` всё ещё показывал S3 `29/3/4`, хотя после принятого
`DEC-0052` machine source, generated atlas, target README и regression test
уже давали `31 used / 3 reserved / 2 free`.

## Исправление

Stage ledger приведён к machine-derived `31/3/2`. Новый HMX electrical-fit
pass не меняет эту арифметику: бывший `GPIO39/LCD_DC` переиспользован под
touch IRQ, reset lines уже находились на slow plane. Subsequent `DEC-0054`
корректно расходует GPIO6 на `AUDIO_ARM`; current ledger теперь `32/3/1`.
