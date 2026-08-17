# FND-0059 — pin-budget presentation was stale after quiet-state controls

- Статус: **Несоответствие исправлено и защищено generated atlas/test**
- Серьёзность: architecture-review integrity / hidden GPIO overbooking risk
- Обнаружено: 2026-08-17
- Corrected artifact: [`PIN-0003`](../architecture/PIN-0003-g2f-3i-principled-pinout.md)

## Несоответствие

`NIF-0001/REV-0004L` сохраняли бюджет до `DEC-0046`:

- S3 `29 used / 3 reserved / 4 free`;
- C5 `13 / 6 / 2`;
- RP `46 / 0 / 2`.

После добавления direct quiet-state controls реально стало:

- C5 `GPIO4 → IR_FRONTEND_PWR_EN`, поэтому C5 `14 / 6 / 1`;
- RP `GPIO15 → NRF_GROUP_PWR_EN` и `GPIO23 → CC_PWR_EN`, поэтому RP
  `48 / 0 / 0`.

Generated ledger уже показывал правильные числа, но один stale prose gap внутри
machine source и прежние review tables создавали противоречие.

## Исправление

- stale source prose и `NIF-0001/REV-0004L` исправлены;
- создан отдельный generated
  [`G2F-3I-principled-pinout`](../architecture/generated/G2F-3I-principled-pinout.md);
- `--check` теперь проверяет оба generated artifacts;
- regression test фиксирует exact `29/3/4`, `14/6/1`, `48/0/0` budgets.

## Результат

Presentation mismatch закрыт. Нулевой direct RP reserve остаётся осознанным
architecture fact, а не закрытой проблемой: новый direct endpoint обязан
переоткрыть layout review.

