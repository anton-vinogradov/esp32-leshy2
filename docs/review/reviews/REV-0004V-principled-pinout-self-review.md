# REV-0004V — principled pinout self-review

- Статус: **Проведено ревью current principled pinout; final electrical closure открыта**
- Дата: 2026-08-17
- Artifact: [`PIN-0003`](../architecture/PIN-0003-g2f-3i-principled-pinout.md)
- Generated atlas: [`G2F-3I principled pinout`](../architecture/generated/G2F-3I-principled-pinout.md)
- Findings: [`FND-0059`](../findings/FND-0059-stale-pin-budget-after-quiet-state.md),
  [`FND-0060`](../findings/FND-0060-abstract-electrical-endpoints-block-final-pinout.md)

## Проверено

| Проверка | Результат |
|---|---|
| diagram and tables share one source | pass: both generated from `G2F-3I.json` |
| exact module/package contacts | pass for S3/C5/RP, nRF references, CC1101, U214, slow I/O, I²C isolator, microSD, SA518 and Si4732 |
| GPIO accounting after quiet-state controls | pass: S3 `29/3/4`, C5 `14/6/1`, RP `48/0/0` |
| slow-plane accounting | pass: `23 used + P27 reserve` |
| every nRF physically independent at bus/control level | pass: 3× six direct contacts, separate PIO SM and DMA pair |
| other radio/accessory bus waits for nRF/display | no; resource contracts remain dedicated |
| controller/fixed-mux capacity | pass: PIO `5/12`, RP DMA `13/16`, S3 GDMA TX/RX `3/5` |
| S3/C5/RP independent recovery | pass on exact exposed contacts |
| SA518 update/recovery access | pass at pin-contract level: `UPDATE/UART_TX/UART_RX/PD` fixture; UPDATE electrical direction still specimen gate |
| Si4732 split antenna/control pins | pass: exact `FMI/AMI/SDIO/SCLK/RST/INT/RCLK` routes |
| final exact electrical endpoints | fail/open: `FND-0060`; no target-final claim |
| generator regressions | pass: 30 tests |

## Исправления этого прохода

1. Найден и исправлен stale pre-`DEC-0046` budget в `NIF-0001/REV-0004L` и
   qualification prose machine source.
2. Generated output разделён на full comparison ledger и focused principled
   pinout atlas; `--check` защищает оба.
3. SA518 and Si4732 перестали быть generic peers: exact contacts and SA518
   service fixture теперь входят в machine source.
4. Полный список оставшихся abstractions вынесен в generated atlas и
   `FND-0060`, поэтому он не может быть выдан за готовую схему.

## Результат

Current G2F-3I principle pin mapping получает **«Проведено ревью»** в пределах
paper owners/controllers/pins/service/capacity. Это не финальное принятие
архитектуры: exact electrical parts, physical product layout, whole-device
optimality, RF/power/SI and HIL остаются обязательными последующими gates.

