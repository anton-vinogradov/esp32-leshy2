# Procurement evidence workspace

These files are engineering inputs for the current H5 component-qualification
phase. They are not part of the public finished-product narrative, do not
authorize a purchase and do not replace received-part tests.
The active policy is source research first, mapping to the selected assembly
platform second, a documented replacement or exact-part sourcing route third,
and purchasing only as a separately approved last resort.
H1 through H4, including the joined pre-layout review, are complete. H5.0.1 and
H5.0.2 are reviewed; H5.0.3 is current. JLCPCB Standard PCBA is the
non-exclusive reference, and the full 209-line BOM is being mapped to `J0`–`J4`
in the [public manufacturing baseline](../../docs/manufacturing-platform.md).
The controlling state is
[`hardware/verification/h5-component-evidence-plan.json`](../verification/h5-component-evidence-plan.json).

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| standalone display production identity | [`HMX035CTFT-001-display-rfq.md`](HMX035CTFT-001-display-rfq.md) | H1 main-board geometry closed by replaceable `L2-DISP-ADP-001-A`; optional no-order identity request retained | controlled standalone lifecycle identity plus received-tail fit on an adapter revision in H5; commercial/sample work stays deferred |
| exact nRF miniature RF mate | [`E01-ML01IPX-data-request.md`](E01-ML01IPX-data-request.md) | H1 paper path closed as Gen1; optional no-order lot confirmation retained | received lot proves Gen1 fit/retention and complete-feed RF performance in H5 |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | H1 paper geometry closed with pass-through `HLE-107-02-G-DV-PE-LC`; optional manufacturer confirmation retained | received U214 passes insertion/withdrawal, continuity, repeated-cycle and retention checks in H5 |
| exact SA518 geometry, variant and supply | [`SA518-sample-rfq.md`](SA518-sample-rfq.md) | prepared as fallback but not authorized to send; selected-platform global sourcing/new-part route is checked first | controlled land pattern + resolved UPDATE/H-L semantics + one received module passes incoming/HIL |
| complete minimum first lot | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | generated H5.0.3 basket published; 10/209 critical/BOM lines mapped and purchase not authorized | all 209 lines have exact `J0`–`J4` routes, then a separate order decision is made |

The current schematic specification and pre-layout review do not authorize a
purchase. KiCad PCB placement/routing and prototype fabrication also remain
separate later gates.
