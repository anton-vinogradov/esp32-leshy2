# ⚠️ Предложение IMP-0050 — AON hard STOP и per-path actual-TX evidence

- Статус: **Принято владельцем: вариант A; реализовано как `DEC-0061`**
- Дата: 2026-08-17
- Internal step: [`INT-0001/I2`](../architecture/INT-0001-internal-design-closure-sequence.md)
- Facts/options: [`SAFE-0001`](../architecture/SAFE-0001-aon-stop-and-tx-evidence-options.md)
- Finding: [`FND-0071`](../findings/FND-0071-hard-stop-and-tx-evidence-coverage.md)
- Decision: [`DEC-0061`](../decisions/DEC-0061-aon-stop-and-per-path-tx-evidence.md)
- Exact circuit: [`SAFE-0002`](../architecture/SAFE-0002-accepted-aon-stop-and-evidence-circuit.md)

> **Позднее уточнение I6:** три nRF detector endpoint из исходного варианта A
> заменены exact directional chains `DC2337J5010AHF` + `AD8314ACPZ-RL7` в
> [`N24E-0001`](../architecture/N24E-0001-exact-three-nrf-electrical-endpoint.md).
> Это уточняет способ получения evidence и не переоткрывает принятое решение A.

## Текущее состояние и причина решения

Принцип hard STOP уже принят, но exact circuit отсутствует, а старый текст
сбрасывает только S3/C5 и не охватывает актуальный RP2354B. Одновременно
current map имеет abstract actual-TX inputs только для S3, C5, voice и IR;
3×nRF24 и CC1101 не имеют source-specific физического evidence.

Свободных direct GPIO у RP нет. Это не требует менять accepted pinout:
`RP.GPIO22` можно превратить из voice-only evidence в общий аппаратный
`ANY_TX_N`, а восемь отдельных состояний прочитать через input expander на
локальной стороне уже существующего RP I²C0. Физический LED и общий GPIO
формируются diode-isolated непосредственно от comparator outputs и не зависят
от I²C/firmware.

## A — рекомендуемый robust prototype плюс cost-down coupon

- AON safety chain: `TPS3808G33DBVR`, `SN74LVC1G74DCUR`,
  `74LVC2G14GW,125`, 2×`74LVC1G32GV,125`, 2×`SN74LVC08APWR`.
- `AON_SAFE` also keeps detector/comparator/critical-indicator electronics
  alive through STOP; its continuous load is budgeted in `I3`.
- STOP reset-dominates all three compute domains and independently gates every
  external CE/PTT/driver/rail; power cycle or fresh physical re-arm starts only
  a new TX-off boot.
- Five `LTC5532ES6#TRMPBF` cover S3/C5/3×nRF, two
  `LTC5507ES6#TRMPBF` cover CC/voice, `VEMD1060X01` covers IR.
- 2×`TLV1824PWR` and `TCA9534APWR` produce an eight-bit source mask plus
  independent physical `ANY_TX`.
- In parallel, a `BAT1503WE6327HTSA1` per-path detector coupon checks whether
  the approximately USD 17 detector-IC burden can later be reduced with no
  loss. It does not replace the robust first prototype before equal HIL proof.
- U214/later Cap without its own qualified evidence reports
  `unknown/unavailable`; mandatory-proof TX stays disabled/fixture-only.

Consequences: highest initial BOM/board-area cost, but the quickest path to
known sensitivity and source-specific evidence. Exact RF taps, passive values
and thresholds remain `I6/HIL`, and `TPS22918DBVT` remains an `I3` first target,
not a frozen switch for every rail.

## B — discrete BAT15 detectors immediately

Use one `BAT1503WE6327HTSA1` cell per RF path in the first prototype, keeping
the same STOP, comparators, source mask and physical indicator.

Consequence: materially lower eventual detector BOM, but greater first-board
risk from band-specific matching, temperature/calibration, false-state and
supply inconsistency. A failed detector coupon could force a board respin or
manual rework before safety HIL.

## C — shared detector or command/current inference

One group detector, PA-current sensor, `CE/PTT` or firmware state is used as
actual-TX indication.

Consequence: cheapest, but cannot source-identify three simultaneous nRF and
does not prove radiation. It violates the accepted evidence and no-loss
contracts and is therefore rejected by self-review, not recommended as an
equivalent option.

## Рекомендация

Принять **A**. It closes the paper architecture without spending another RP
GPIO, keeps the critical aggregate light independent of all software, and
separates prototype certainty from a real cost-down experiment. This adds
roughly USD 20 of volume-priced evidence electronics before passives/taps, so
the BAT15 coupon is worth doing; removing per-path proof is not a permissible
saving.

## Решение владельца

Вариант **A принят**. Exact propagation добавила Ioff reset-buffer,
stocked common-anode diode arrays и exact critical LEDs; это устраняет
электрические пробелы принятого варианта без изменения его функций.
