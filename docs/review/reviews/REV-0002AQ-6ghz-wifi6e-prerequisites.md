# REV-0002AQ — 6 GHz/Wi-Fi 6E prerequisite review

- Статус: **Проведено ревью фактов; later closed C/`DEC-0040`**
- Дата: 2026-08-17
- Input: `W-EXTRA-17`, refined radio/key mission, current primary sources
- Outputs: `AUD-0012`, `FND-0048`, `IMP-0034`

## Проверка

| Проверка | Результат |
|---|---|
| 6 GHz matches radio/key mission | да; radio result |
| Accepted 5 GHz called 6 GHz/6E | no |
| Current ESP32-C5 claimed to contain 6 GHz RF | no |
| Host-attached 6E silicon shown feasible | да; SDIO/PCIe examples only |
| Example silently selects Linux, M.2 or exact chip | no |
| RF/antenna/power/driver/recovery cost exposed | да |
| Global TX legality assumed from one region | no |
| Passive, ordinary active and dangerous workflows separated | да |
| Deferred 6 GHz allowed to weaken 2.4/5 GHz | no |
| Base/optional/reject alternatives compared | да |

## Result

Fact/prerequisite slice receives **«Проведено ревью»**. The remaining question
is product placement, not technical existence. Recommendation `IMP-0034/B`
preserved a qualified optional radio/compute profile with no base hardware
burden. The owner later selected C through `DEC-0040`; this prerequisite review
remains evidence and imposes no current 6E target or architecture burden.
