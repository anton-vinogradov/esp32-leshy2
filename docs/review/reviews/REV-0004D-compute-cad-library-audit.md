# REV-0004D — compute CAD library audit

- Статус: **Проведено ревью фактов; superseded by DEC-0030/REV-0004E**
- Дата: 2026-08-16
- Артефакт: [`LIB-0001`](../components/LIB-0001-compute-cad-library-audit.md)
- Finding: [`FND-0036`](../findings/FND-0036-current-cad-cannot-represent-target-compute.md)

## Проверки

| Проверка | Результат |
|---|---|
| installed KiCad version recorded | да, 10.0.5 snapshot |
| all `C-001…005` symbol/footprint availability checked | да |
| exact upstream entries distinguished from similar-name candidates | да |
| absent C5 library entry detected | да |
| S3 symbol default-footprint mismatch detected | да |
| ABM8G footprint not accepted as exact ABM8-272 without comparison | да |
| RP2354A/TCA exact upstream identities recorded | да |
| mutable/current tsCircuit limitations recorded | да |
| stage-4 library work separated from stage-8 schematic implementation | да |
| strategy choice isolated instead of silently copying assets | да, `IMP-0025` |

## Результат

CAD-library facts receive **«Проведено ревью»**. At this historical checkpoint
`FND-0036` was confirmed and strategy remained open. The owner later selected
`IMP-0025/A`; `DEC-0030/REV-0004E` implement and review the snapshot. No
final schematic is implied by either review.
