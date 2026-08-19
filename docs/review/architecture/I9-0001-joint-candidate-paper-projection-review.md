# I9-0001 — joint candidate paper-projection self-review

- Статус: **Проведено ревью working-candidate paper scope; not G7 atomic architecture**
- Дата: 2026-08-19
- Candidate: `G2F-3I`
- Finding: [`FND-0116`](../findings/FND-0116-i9-abstract-and-stage-labels-were-not-closed.md)
- Review: [`REV-0005CD`](../reviews/REV-0005CD-i9-joint-candidate-projection-propagation.md)

## Joint result

| Domain | Проверенный результат | Downstream reopen |
|---|---|---|
| compute/service | S3 `33/3/0`, C5 `14/6/1`, RP `48/0/0`; complete independent service alternatives and accounted real exposed contacts | erased-image, SI/backfeed and physical fixture HIL |
| safety/power | non-programmable STOP/reset/TX-gate/evidence path; exact supervised 2S, rails, protection and fault aggregation | exact lot, thermal, source-transition and controlled-destructive HIL |
| UI/storage/display | full controls retained; main slow I/O `24/0/0`, dedicated UI I/O `7/1/0`; exact electrical endpoints and bounded shared-interface contracts | G3 mechanics plus display/storage/USB/UI HIL |
| audio/receiver/RF/IR | exact paper endpoints, all signal groups, quiet states, transitions, actual-TX evidence and no-stall criteria are complete; three nRF retain full simultaneous PTX/PRX mix | conducted/OTA/optical/acoustic/coexistence/thermal HIL |
| expansion | independent U214 Cap and native Unit power/signal boundaries plus three-domain recovery remain complete | received connector/cable coupons and hot-plug/fault HIL |
| procurement feasibility | I8 reviewed at 857 supplied placements / 187 lines, 175 prices + 12 gates, 187 substitution dispositions and 4/4 physical-family gates | G3 physical inputs and selected-G7 G8 frozen BOM/RFQ/alternates/COGS |
| landing diagrams | 858/858 physical architecture instances render one device per node; landing views start from owners and detailed atlas stays under GitHub limits | any accepted device/owner/path change regenerates all views |

## Abstract endpoint closure

The 970 abstract-route occurrences collapse to 59 unique named boundaries.
Every label is assigned exactly once:

| Class | Unique labels | Meaning |
|---|---:|---|
| `electrical_plane_rail_or_wired_logic` | 14 | conductive rail/plane, supervised cell node or explicit wired aggregation |
| `intentional_no_connect_or_open_strap` | 2 | reviewed NC/open configuration, not a component |
| `pcb_geometry_test_or_reserved_feature` | 24 | via/copper/ground geometry, protected fixture point or reserved pad |
| `g3_physical_purchase_resolution_gate` | 18 | fixed electrical endpoint whose exact connector/cable/antenna identity belongs to a `BOM-0027` G3 gate |
| `external_fixture_source_boundary` | 1 | isolated recovery-fixture source, not a product rail |

There are **0 unclassified**, **0 multiply classified**, **0 stale** abstract
labels and **0 unresolved owner decisions** inside the working candidate.

## Mismatch repair made during self-review

- `I8/procurement` XTAR evidence → downstream `G8 procurement`;
- physical NTC compression/response `I8/HIL` → `G11 prototype HIL`;
- old nRF subblock cost estimate is retained only as superseded history;
  current machine cost/gates are authoritative;
- I9 wording no longer claims the later G7 atomic-architecture output.

## Verdict and handoff

I1…I9 receive **«Проведено ревью»** for the current G2F working-candidate
paper scopes. `G2F-3I` is internally consistent enough to drive G3 physical
design, but it remains a provisional candidate: G3 conflicts loop back, G4
must still produce whole-device alternatives, G5 selects by optimality, G6
co-designs placement, and only G7 may accept an atomic architecture.

The paused integrated mockup may now resume. KiCad remains forbidden.
