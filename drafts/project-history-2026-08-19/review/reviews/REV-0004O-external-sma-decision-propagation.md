# REV-0004O — external-SMA and compact-nRF decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md)
- Proposal: [`IMP-0040`](../improvements/IMP-0040-three-nrf-module-and-antenna-baseline.md)
- Evidence: [`N24M-0001`](../architecture/N24M-0001-exact-module-antenna-comparison.md)

## Проверенная propagation matrix

| Область | Результат |
|---|---|
| Owner clarification | «все антенны внешние, все SMA» сохранено как base onboard RF invariant; `RSA` не заведён как новый connector type |
| nRF module direction | все три candidate maps используют один `E01-ML01IPX` verified reference; встроенный `E01-ML01S` не target |
| nRF antenna identity | ровно три independent IPEX→short-pigtail→SMA paths; никакого antenna switch/shared radiator |
| Other onboard RF | external SMA закреплён как endpoint class; exact count, gender, bulkhead/edge-launch и feed parts открыты |
| External accessories | M5 Unit/Cap сохраняют собственные antenna manifests и не увеличивают base antenna-bank contract |
| Safety/runtime | port/band/antenna profile входит в TX manifest; наличие SMA не доказывает correct load, EIRP или legal profile |
| Legacy mockup | внешний antenna-bank принцип переиспользуется; старые owners, fixed count и generic modules не наследуются |
| Machine source | `DEC-0048` policy обязателен для `G2F-2R/3D/3I`; regression test отклоняет PCB antenna, два SMA или не-IPEX nRF reference |
| Firmware repository | `ARC-0002` и стартовые/status pages требуют labelled SMA identity в manifests |

## Открытые границы

Ревью не выдаёт BOM/CAD pass. Остаются exact production nRF MPN/revision/lot,
SMA gender/polarity and mounting, cable SKU/loss/bend/retention, ненRF port
count, physical packing, antenna sets, coexistence/self-desense, emissions,
regulatory/EIRP и `T1` HIL.

## Результат

Решение распространено без потери трёх simultaneous nRF paths и без возврата
legacy owners. Шаг получил статус **«Проведено ревью»**. Следующий шаг — exact
SMA/feed/placement envelope и target `T1`, а не KiCad.
