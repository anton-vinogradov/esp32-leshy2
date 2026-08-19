# REV-0004B — compute, clock and recovery evidence review

- Статус: **Проведено ревью фактов; `IMP-0024` later accepted by `DEC-0029`; qualification gates открыты**
- Дата: 2026-08-16
- Артефакт: [`BOM-0002`](../components/BOM-0002-compute-clock-recovery-evidence.md)
- Finding: [`FND-0035`](../findings/FND-0035-rp2354a-order-code-stock-correction.md)

## Проверки

| Проверка | Результат |
|---|---|
| exact S3/C5 module variants проверены по current primary docs | да |
| C5 MPN отделён от silicon revision/lot | да; MPN alone cannot enforce v1.2 |
| current C5 errata сопоставлены с accepted `≥v1.0` | да; одно owner decision открыто |
| exact RP2354A A4 manufacturer order codes найдены | да, `SC1511-A4` / packaging-equivalent `SC1511(13)-A4` |
| прежний RP qty-500 shortage claim перепроверен | да; ошибочный вывод исправлен в `FND-0035` |
| RP crystal reference перестал быть generic | да; `ABM8-272-T3` и recommended 3.3 V network записаны |
| TCA status/reset/interrupt contract проверен | да; exact circuit proof ещё открыт |
| recovery and link support parts имеют complete obligations | да; exact implementation/HIL ещё открыт |
| supplier stock выдан за qualification | нет |
| хотя бы одна строка ошибочно получила `Q` | нет |

## Self-review result

Проверенные факты непротиворечивы `PKG-0001/PIN-0002/BUD-0002`. `FND-0035` устраняет supply-chain ошибку без смены architecture. На момент review `IMP-0024` был выделен отдельно, поскольку смена production stepping влияет на procurement, manufacturing identity и firmware restrictions. Владелец позднее принял A как `DEC-0029`; propagation проверяет `REV-0004C`.

Статус **«Проведено ревью фактов»** не закрывает `BOM-0002` целиком. До owner disposition и физической qualification `C-001…007` остаются unqualified prerequisites; `BOM-0003` не должен считать их окончательно закрытыми.
