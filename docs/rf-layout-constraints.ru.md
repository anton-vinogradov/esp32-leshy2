# Ограничения RF layout

`H3.5.2` проведён ревью: `23` машинных checks, незакрытых аналитических findings нет. Точный текущий маркер — `H3.5.3`.

Линии H1 остаются topology/corridor guides, а не якобы готовой медью KiCad. Их проекционные длины перенесены только для того, чтобы H6 не мог молча потерять или перепутать тракт.

| Тракт | Внутренняя сторона платы | Guide H1, мм | Максимальный шаг via fence, мм |
|---|---:|---:|---:|
| S3-2G4 | ui-inner | 10.550 | 1.25 |
| C5-2G4/5 | ui-inner | 10.550 | 1.25 |
| N24-0 | rf-inner | 48.550 | 1.25 |
| N24-1 | rf-inner | 43.812 | 1.25 |
| N24-2 | rf-inner | 38.636 | 1.25 |
| CC-SUB | rf-inner | 10.300 | 2.5 |
| VOICE-V/U | rf-inner | 60.632 | 2.5 |
| RX-FM/SW | ui-inner | 70.786 | 2.5 |
| RX-AM/LW | ui-inner | 59.324 | capacitance-controlled |

Для каждого обычного RF-mainline H6 обязан рассчитать геометрию по утверждённому stack-up, сохранить непрерывную reference plane, исключить tee/test stub, предпочитать ноль и допускать максимум один рассчитанный signal-layer transition, а return vias connector/ESD/matching ставить немедленно. Общий шаг fence для 2,4/5 ГГц равен `1,25 мм`: он округлён вниз от консервативного `lambda_g/20 = 1.361 мм` на 5,885 ГГц при effective permittivity 3,5.

`RX-AM/LW` намеренно отличается: под его high-impedance сегментом нет общего 50-омного plane/fence. Вместо этого connector, PCB, ESD и pod должны уложиться во внешний бюджет H3.5.1 `19,500 пФ`.

Машинное evidence: [`H3-VRF52-rf-layout-constraints.json`](../hardware/verification/generated/H3-VRF52-rf-layout-constraints.json).
