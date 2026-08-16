> Архивировано решением DEC-0027: этот документ оптимизировал legacy-derived раскладку и не является входом новой архитектуры. Сохранён только как источник идей и отрицательных результатов.

# SC-0001 — единая scorecard полных компоновок этапа 3

- Статус: **Проведено ревью; scoring полных layouts открыт после completion `DM-0001`**
- Вход: `DEC-0023`, `DM-0001`, `PIN-0001`, open findings
- Варианты: минимум `LAY-S3`, `LAY-C5`, `LAY-BAL`

## Сначала hard fail

Вариант не получает weighted score, если нарушена хотя бы одна строка.

| Gate | Hard-fail criterion |
|---|---|
| `HF-01` Wishlist | потеря любого accepted/conditional base leaf или его acceptance boundary |
| `HF-02` 3×nRF24 | меньше трёх simultaneous full-function PTX/PRX; нет independent logical CS/CE/session state |
| `HF-03` IR | не C5; нет двух RX + TX resource; carrier-learning/robust path сокращены |
| `HF-04` BLE/radios | native BLE не S3 baseline; C5 Wi-Fi/802.15.4 owner broken; false simultaneity claim |
| `HF-05` Audio | нет четырёхсигнального S3 I²S ES8311 path или fail-safe analog bypass |
| `HF-06` STOP | STOP зависит только от MCU/I²C/UI; не доминирует над каждым TX path/accessory |
| `HF-07` Actual TX | software intent выдаётся за actual-TX proof; unsafe unknown can arm Controlled action |
| `HF-08` Pins | unavailable/duplicate/strap-unsafe GPIO, wrong voltage or controller double booking |
| `HF-09` Memory | selected exact module cannot fit worst simultaneous firmware/data buffers with accepted margin |
| `HF-10` Transport | update/capture/control traffic exceeds measured bound or link loss can leave TX lease active |
| `HF-11` Recovery | either MCU cannot be recovered after bad image without relying on that bad image |
| `HF-12` External profiles | GPS/U214/U216 electrical/data profile broken or external module counted as free pins when attached |
| `HF-13` Power/RF | rail/thermal/startup peak fails or unsafe simultaneous TX is physically possible before HIL authorization |
| `HF-14` Evidence | score depends on unversioned binary, unsupported API, fictitious detector or unmeasured percentage |

## Weighted comparison after hard gates

Each category is scored `0..5` from evidence. Weight totals 100. A narrative claim without artifact receives zero, not an estimated middle score.

| Category | Weight | 5-point boundary |
|---|---:|---|
| Functional/performance margin | 18 | all mandatory scenarios pass with ≥30% measured controller/bus/memory deadline margin |
| Safety/fault containment | 18 | independent STOP and actual-TX fan-out proven by fault injection with no single hidden controller dependency |
| Recovery/update robustness | 12 | independent S3/C5 recovery, signed update/rollback and debug access preserved |
| Base total cost | 12 | lowest verified PCBA+assembly+test cost among equivalent passing variants, no optional accessory hidden |
| GPIO/controller expansion margin | 10 | meaningful direct/control/controller reserve after all conditional base attachments |
| Power/autonomy/thermal | 10 | lowest measured energy/peak/thermal burden at equal scenarios and battery |
| RF coexistence/placement | 8 | best measured isolation/self-desense and fewest forbidden combinations |
| Complexity/testability | 7 | fewest unique bridges/latches/protocols while retaining observability and deterministic fixtures |
| Serviceability/supply | 5 | current components, replaceable modules, accessible test points and multi-source non-critical parts |
| **Total** | **100** |  |

## Mandatory score sheet columns

| Field | Meaning |
|---|---|
| Exact module/BOM revision | no generic S3/C5/module names |
| Owner and transport map | every peripheral and inter-MCU path |
| Pin/controller table | exact GPIO, strap/reset state, controller/DMA/IRQ owner |
| Scenario measurements | `SCN-01..08` latency/loss/throughput/current/temperature |
| Safety tree | STOP and actual-TX path with failure states |
| Recovery procedure | bad S3, bad C5, broken link, empty flash |
| Cost evidence | date, quantity, supplier, assembly/test/NRE inclusions |
| Risks and degraded modes | explicit, not hidden in score |
| Open findings | closure evidence or hard fail |

## Tie-break order

If total scores differ by less than 3 points: safety/fault containment → recovery → functional margin → total cost → expansion margin. Historical placement is never a tie-breaker.

