# Procurement evidence workspace

These files are parked engineering inputs for later component qualification.
They are not the next project step, are not part of the public finished-product
narrative, do not authorize a purchase and do not replace received-part tests.
The active policy is source research first, a documented replacement second,
a no-order manufacturer data request third, and purchasing only as a separately
approved last resort.
The controlling gate is
[`hardware/verification/preorder-verification-contract.json`](../verification/preorder-verification-contract.json):
mechanical design approval, a current schematic, virtual electrical analysis,
an executable firmware model, target builds/emulation and joined pre-layout
review come first.

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| standalone display production identity | [`HMX035CTFT-001-display-rfq.md`](HMX035CTFT-001-display-rfq.md) | no-order technical request ready | controlled approval drawing and standalone lifecycle identity; commercial/sample work stays deferred |
| exact nRF miniature RF mate | [`E01-ML01IPX-data-request.md`](E01-ML01IPX-data-request.md) | no-order technical request ready; public evidence strongly indicates Gen1 | supplier names exact receptacle/mate; current-lot verification remains a later incoming gate |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | no-order technical request ready | M5Stack names fitted header/socket and controls post, mated-height and retention geometry |
| exact SA518 geometry, variant and supply | [`SA518-sample-rfq.md`](SA518-sample-rfq.md) | ready to send; price and inventory are RFQ-only | controlled land pattern + resolved UPDATE/H-L semantics + two received modules pass incoming/HIL |
| complete minimum first lot | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | parked; purchase not authorized and P1–P6 remain open | P1–P6 pass, then every listed acceptance record passes or an explicit architecture exception is reviewed |

A new current schematic is required before ordering. KiCad PCB placement and
routing remain unauthorized until the joined pre-layout gate passes.
