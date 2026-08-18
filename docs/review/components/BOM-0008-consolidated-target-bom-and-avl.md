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

- 858 current placements;
- 188 used exact-device/MPN lines;
- 855 base-product placements;
- 2 separately supplied regional cell-kit placements;
- 1 optional U214 accessory placement;
- 187/188 used lines already carry dated orderability evidence;
- 1/188 requires current source verification: standalone
  `HMX035CTFT-001` orderability remains unproved;
- 188/188 still require machine-readable quantity-100 cost and
  alternate/no-substitution disposition.

The generated review intentionally uses vertical `<details>` cards rather than
one over-wide table. CSV retains every quantity and placement for scripts and
future factory RFQ.

## Ordered closure

1. ~~Repair prerequisite MAX17320 electrical residues exposed by
   consolidation.~~ **Проведено ревью** by `PWR-0022/DEC-0100/REV-0005BF`.
2. ~~Instantiate eight actual-TX threshold/hysteresis networks and repair the
   AON-to-main observation boundary.~~ **Проведено ревью** by
   `SAFE-0003/DEC-0101/REV-0005BG`.
3. Convert the four remaining connector/cable/antenna gap families into exact
   first-target or received-item gates without guessing unavailable contacts.
4. ~~Recheck the 33 used lines with no dated orderable source.~~ **32 lines
   closed** by `BOM-0009/DEC-0102/REV-0005BH`; `HMX035CTFT-001` remains an
   explicit unresolved sourcing line. Replace a part automatically only when
   function, performance, safety, reliability, serviceability and assembly
   remain equivalent.
5. Attach one substitution class to every used line: qualified exact alternate,
   parametric passive policy, or explicit no-drop-in-substitute/requalification.
6. Record comparable USD qty-100 component snapshots and keep PCB, PCBA,
   enclosure, fixture, battery logistics and antenna-kit variants separate.
7. Run the consolidated self-review and only then mark I8 «Проведено ревью».

No incomplete line is assigned a zero price. No broad family name is an AVL.
No substitute may change a pin, rail, RF path, STOP behavior or product
capability silently.
