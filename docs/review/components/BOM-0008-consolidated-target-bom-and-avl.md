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

- 858 architecture instances, including 1 explicit assembly-internal evidence
  node excluded from purchasing by `BOM-0011`;
- 857 supplied/costed placements;
- 187 used exact-device/MPN purchase lines;
- 854 base-product purchase placements;
- 2 separately supplied regional cell-kit placements;
- 1 optional U214 accessory placement;
- 186/187 used lines already carry dated orderability evidence;
- 1/187 requires current source verification: standalone
  `HMX035CTFT-001` orderability remains unproved;
- 52/187 now have machine-readable quantity-100 cost by
  `BOM-0013…0016/DEC-0105…0106/REV-0005BL…BO`; they cover 614/857 placements,
  135/187 remain unpriced and the USD 102.2205 covered base subtotal is not
  complete COGS;
- 5/135 unpriced lines have explicit machine-readable RFQ/retail comparability
  gates; a gate never contributes a numeric subtotal;
- 187/187 now have alternate/no-substitution disposition by
  `BOM-0012/DEC-0104/REV-0005BK`; this is policy coverage, not 187 qualified
  second-source MPNs.

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
   `DSP-0008/BOM-0010/REV-0005BI` subsequently prove current prototype
   specimen access and exact RFQ inputs without misreporting a bundled board as
   standalone orderability.
5. ~~Attach one substitution class to every used line: qualified exact
   alternate, parametric passive policy, or explicit
   no-drop-in-substitute/requalification.~~ **Проведено ревью** by
   `BOM-0012/DEC-0104/REV-0005BK`; specific proposed alternates remain subject
   to their class gates.
6. Record comparable USD qty-100 component snapshots and keep PCB, PCBA,
   enclosure, fixture, battery logistics and antenna-kit variants separate.
   **First 52/187 lines / 614 placements reviewed** by
   `BOM-0013…0016/DEC-0105…0106/REV-0005BL…BO`; continue through the remaining
   135 lines without assigning zero or retail multiplication to missing
   evidence. Five researched gaps already carry an explicit RFQ/retail gate.
7. Run the consolidated self-review and only then mark I8 «Проведено ревью».

No incomplete line is assigned a zero price. No broad family name is an AVL.
No substitute may change a pin, rail, RF path, STOP behavior or product
capability silently.
