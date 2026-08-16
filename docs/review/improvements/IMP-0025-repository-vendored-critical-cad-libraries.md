# ⚠️ IMP-0025 — repository-vendored critical CAD libraries

- Статус: **Принято вариантом A; реализовано и проведено ревью**
- Дата: 2026-08-16
- Основание: `LIB-0001`, `FND-0036`, решение владельца A
- Затрагивает: CAD reproducibility, review diffs, KiCad toolchain, future schematic/PCB maintenance

## Current state

At least C5 requires a custom symbol/footprint. Other critical rows are split between exact upstream entries, an S3 symbol/footprint mismatch and a crystal footprint named for a different Abracon variant. The current tsCircuit parts engine is mutable and contains the obsolete architecture.

## Options

### A — recommended: vendor all critical compute libraries

Create a small project-owned KiCad library snapshot for `C-001…005`:

- exact project symbols and footprints live in the repository;
- upstream KiCad assets may be imported where correct, with license/commit/source attribution;
- S3/C5/ABM8 assets are explicitly bound to exact target variants;
- RP/TCA retain verified upstream geometry but gain target MPN/stepping metadata;
- checks compare pins, pad counts/key dimensions, fields and hashes; later upstream/manufacturer changes arrive as reviewed diffs.

Consequences: self-contained/reproducible releases and visible geometry changes; modest maintenance and attribution burden. Five critical rows are small enough that this burden is controlled.

### B — use pinned global KiCad libraries where available

- pin KiCad/library version 10.0.5;
- store only missing C5 and exact ABM8/S3 overrides locally;
- reference global RP/TCA/other footprints.

Consequences: less duplicated library content, but builds depend on workstation library installation and future migration must recreate the exact global snapshot. A tool version pin does not by itself preserve independently updated library packages.

## Recommendation

Choose **A**. The product has RF modules, a new C5 variant, QFN60, recovery/safety obligations and a long owner-controlled lifecycle. A small self-contained critical library gives materially stronger reproducibility than mutable parts-engine or workstation-global geometry, without requiring the whole KiCad standard library to be copied.

This proposal changes the artifact-production method, not hardware functions or owners.

## Decision outcome

Владелец выбрал **A**. Решение зафиксировано в
[DEC-0030](../decisions/DEC-0030-vendored-critical-cad-libraries.md), а
реализация и проверки — в
[REV-0004E](../reviews/REV-0004E-vendored-critical-cad-libraries.md).
