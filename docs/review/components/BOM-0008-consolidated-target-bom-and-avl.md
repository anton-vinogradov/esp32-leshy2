# BOM-0008 — consolidated target BOM, AVL and cost workbench

- Статус: **I8 inventory coverage проведено ревью; qualification active**
- Дата: 2026-08-19
- Finding: [`FND-0109`](../findings/FND-0109-machine-map-was-not-a-complete-physical-bom.md)
- Generated review: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)
- Factory-oriented manifest: [`G2F-3I-target-bom.csv`](generated/G2F-3I-target-bom.csv)

## Boundary

Этот artifact заменяет ручное сложение прежних частичных оценок. Каноническая
строка берётся только из current `G2F-3I.instances` и exact device database;
comparison-only definitions не попадают в target quantity. Отдельный gap
register не позволяет исчезнуть ещё не instantiated connector, cable,
calibration или accessory item.

## Current measured coverage

- 816 current placements;
- 187 used exact-device/MPN lines;
- 813 base-product placements;
- 2 separately supplied regional cell-kit placements;
- 1 optional U214 accessory placement;
- 153/187 used lines already carry dated orderability evidence;
- 34/187 require current source verification;
- 187/187 still require machine-readable quantity-100 cost and
  alternate/no-substitution disposition.

The generated review intentionally uses vertical `<details>` cards rather than
one over-wide table. CSV retains every quantity and placement for scripts and
future factory RFQ.

## Ordered closure

1. ~~Repair prerequisite MAX17320 electrical residues exposed by
   consolidation.~~ **Проведено ревью** by `PWR-0022/DEC-0100/REV-0005BF`.
2. Convert the five remaining connector/cable/calibration/antenna gap families into exact first-target or
   received-item gates without guessing unavailable contacts.
3. Recheck the 34 used lines with no dated orderable source; replace a part
   automatically only when function, performance, safety, reliability,
   serviceability and assembly remain equivalent.
4. Attach one substitution class to every used line: qualified exact alternate,
   parametric passive policy, or explicit no-drop-in-substitute/requalification.
5. Record comparable USD qty-100 component snapshots and keep PCB, PCBA,
   enclosure, fixture, battery logistics and antenna-kit variants separate.
6. Run the consolidated self-review and only then mark I8 «Проведено ревью».

No incomplete line is assigned a zero price. No broad family name is an AVL.
No substitute may change a pin, rail, RF path, STOP behavior or product
capability silently.
