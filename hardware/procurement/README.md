# Procurement evidence workspace

These files are engineering inputs for the current H5 component-qualification
phase. They are not part of the public finished-product narrative, do not
authorize a purchase and do not replace received-part tests.
The active policy is source research first, a documented replacement second,
a no-order manufacturer data request third, and purchasing only as a separately
approved last resort.
H1 through H4, including the joined pre-layout review, are complete. H5.0.1 and
H5.0.2 are reviewed; H5.0.3 is current and has reduced the full evidence set to
one generated basket with one open manufacturer input. The controlling state is
[`hardware/verification/h5-component-evidence-plan.json`](../verification/h5-component-evidence-plan.json).

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| standalone display production identity | [`HMX035CTFT-001-display-rfq.md`](HMX035CTFT-001-display-rfq.md) | H1 main-board geometry closed by replaceable `L2-DISP-ADP-001-A`; optional no-order identity request retained | controlled standalone lifecycle identity plus received-tail fit on an adapter revision in H5; commercial/sample work stays deferred |
| exact nRF miniature RF mate | [`E01-ML01IPX-data-request.md`](E01-ML01IPX-data-request.md) | H1 paper path closed as Gen1; optional no-order lot confirmation retained | received lot proves Gen1 fit/retention and complete-feed RF performance in H5 |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | H1 paper geometry closed with pass-through `HLE-107-02-G-DV-PE-LC`; optional manufacturer confirmation retained | received U214 passes insertion/withdrawal, continuity, repeated-cycle and retention checks in H5 |
| exact SA518 geometry, variant and supply | [`SA518-sample-rfq.md`](SA518-sample-rfq.md) | prepared but not authorized to send; price and inventory are RFQ-only | controlled land pattern + resolved UPDATE/H-L semantics + one received module passes incoming/HIL |
| complete minimum first lot | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | generated H5.0.3 basket published; purchase not authorized | manufacturer response fixes the one open line, then a separate order decision is made |

The current schematic specification and pre-layout review do not authorize a
purchase. KiCad PCB placement/routing and prototype fabrication also remain
separate later gates.
