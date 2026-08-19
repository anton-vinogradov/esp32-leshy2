# FND-0084 — the main-rail source sequencer was still abstract

- Статус: **Исправлено exact AON-PG/POR chain**
- Дата: 2026-08-18
- Correction: [`PWR-0019`](../architecture/PWR-0019-exact-source-sequence-and-power-reserve.md)
- Decision: [`DEC-0080`](../decisions/DEC-0080-exact-aon-pg-por-main-sequence.md)
- Review: [`REV-0005AK`](../reviews/REV-0005AK-source-sequence-propagation.md)

## Finding

The machine map routed `MAIN_3V3_EN` from
`abstract:main-rail-enable-after-source-admission` and routed AON power-good to
another abstract sequencing endpoint. That hid a physical block between two
otherwise exact circuits. It also left no calculable high/low levels, delay or
brownout behavior for the main converter.

Simply tying the existing open-drain `POR_N` to the former 10-kOhm main-EN
pull-down would not close the gap. Its 10-kOhm pull-up and 10-kOhm pull-down
would produce approximately `1.65 V`, uncomfortably close to the
`TPS564252` 1.25-V maximum rising threshold and with poor noise margin.

## Correction

No additional sequencing IC is required. Valid battery admission or protected
USB input is already the only way to create `BQ25798 SYS`. `SYS` starts the
exact `TPS629203`; its pulled-up `PG` now drives `TPS3808G33.MR_N` directly.
The supervisor combines that evidence with its own 3.07-V SENSE threshold and
CT delay, then releases open-drain `POR_N` into the main converter.

One exact `RC0402FR-0710KL` pulls `POR_N` to AON. The main fail-low resistor is
changed to the already-used `RC0402FR-07100KL` 100-kOhm MPN. The released node
is approximately `3.0 V` at nominal AON and remains well above the converter
threshold at the supervisor's minimum valid rail. AON PG/SENSE loss pulls it
low without firmware.

