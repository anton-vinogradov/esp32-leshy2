# Active KiCad gate

- Status: **blocked by upstream design gates; no canonical symbols, schematic or PCB**
- Superseding process decision: [`DEC-0032`](../../docs/review/decisions/DEC-0032-reopen-product-design-before-cad.md)
- Archived premature snapshot: [`drafts/premature-compute-cad-2026-08-16`](../../drafts/premature-compute-cad-2026-08-16/README.md)

KiCad implementation may start only after all of these outputs are reviewed:

1. complete product requirements and constraints;
2. target physical/industrial design contract;
3. several whole-device architecture candidates derived from those inputs;
4. explicit optimality/Pareto comparison and owner selection;
5. conceptual mechanical, RF, power and service placement proving feasibility;
6. accepted architecture, resource and interface package;
7. exact component shortlist with current lifecycle/supply evidence.

Early component and CAD searches are allowed only as feasibility probes. Their
outputs stay in drafts and cannot become normative pins, footprints, BOM rows
or enclosure constraints before the gates above pass.
