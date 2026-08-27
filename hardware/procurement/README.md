# Procurement evidence workspace

These files are engineering inputs for the current H5 component-qualification
phase. They are not part of the public finished-product narrative, do not
authorize a purchase and do not replace received-part tests.
The active policy is source research first, mapping to the selected assembly
platform second, a documented replacement or exact-part sourcing route third,
and purchasing only as a separately approved last resort.
H1 through H4, including the joined pre-layout review, are complete. H5.0.1 and
H5.0.2 are reviewed; H5.0.3 is current. JLCPCB Standard PCBA is the
non-exclusive reference, and the full 210-line BOM is mapped to `J0`–`J3`, `J4-F` or `J4-P`
in the [public manufacturing baseline](../../docs/manufacturing-platform.md).
The controlling state is
[`hardware/verification/h5-component-evidence-plan.json`](../verification/h5-component-evidence-plan.json).

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| standalone display production identity | [`HMX035CTFT-001-display-rfq.md`](HMX035CTFT-001-display-rfq.md) | H1 main-board geometry closed by replaceable `L2-DISP-ADP-001-A`; optional no-order identity request retained | controlled standalone lifecycle identity plus received-tail fit on an adapter revision in H5; commercial/sample work stays deferred |
| exact nRF miniature RF mate | [`E01-ML01IPX-data-request.md`](E01-ML01IPX-data-request.md) | H1 paper path closed as Gen1; optional no-order lot confirmation retained | received lot proves Gen1 fit/retention and complete-feed RF performance in H5 |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | H1 paper geometry closed with pass-through `HLE-107-02-G-DV-PE-LC`; optional manufacturer confirmation retained | received U214 passes insertion/withdrawal, continuity, repeated-cycle and retention checks in H5 |
| dual-SA818S lead time and final assembly | [`original inquiry`](H5.0.3-R1-no-order-supplier-inquiry.md) + [`partial reply`](H5.0.3-R1-jlcpcb-response-2026-08-26.md) + [`machine record`](H5.0.3-R1-supplier-response.json) + [`clarification draft`](H5.0.3-R1-jlcpcb-clarification-reply.md) | JLCPCB confirms exact VHF MOQ 1, typical 8–15-working-day pre-order and conditional Function Test pricing; accumulators are owner-confirmed `J5-U`, not part of delivery or supplier gate; `H5-EVR07` remains fail-closed with 16 unanswered fields | supplier confirms the actual two-designator U/V job and itemizes remaining `J4-F/P` plus exact-MPN control |
| optional Parts API | [`H5.0.3-R1-parts-api-support-inquiry.md`](H5.0.3-R1-parts-api-support-inquiry.md) | support attributes rejection to a new account with no order history, but is not the API review team and gives no threshold; no reapplication submitted | Parts is actually approved after sufficient order history or an accepted exception case; manual evidence remains authoritative meanwhile |
| fallback full-device factory | [`H5.0.3-R1-pcbway-fallback-inquiry.md`](H5.0.3-R1-pcbway-fallback-inquiry.md) + [`H5-EVR08`](../verification/generated/H5-EVR08-fallback-factory-readiness.json) | PCBWay publicly covers the needed supplier/PCBA/test/OEM classes; Seeed is retained as PCBA-only second source; no fallback contact is authorized or sent | if JLCPCB fails `H5-EVR07`, obtain separate authority and submit the same no-order gate questionnaire to PCBWay |
| complete minimum first lot | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | 33-line `$286.43` basket published; all 210 sourcing/final-assembly routes mapped and purchase not authorized | supplier-response gates close, then a separate order decision is made |

The current schematic specification and pre-layout review do not authorize a
purchase. KiCad PCB placement/routing and prototype fabrication also remain
separate later gates.
