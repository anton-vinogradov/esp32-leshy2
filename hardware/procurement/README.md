# Procurement evidence workspace

These files are engineering inputs for the current H5 component-qualification
phase. They are not part of the public finished-product narrative, do not
authorize a purchase and do not replace H7/H8 owner bring-up on the sole prototype.
The active policy is source research first, mapping to the selected assembly
platform second, a documented replacement or exact-part sourcing route third,
and one prototype order only after H6/F-PO and explicit approval. There is no
separate engineering-sample or H5 coupon purchase.
H1 through H4, including the joined pre-layout review, are complete. H5.0.1 and
H5.0.2 are reviewed; H5.0.3 is current. JLCPCB Standard PCBA is the
non-exclusive reference, and the full 210-line BOM is mapped to `J0`–`J3`, `J4-F` or `J4-P`
in the [public manufacturing baseline](../../docs/manufacturing-platform.md).
The controlling state is
[`hardware/verification/h5-component-evidence-plan.json`](../verification/h5-component-evidence-plan.json).

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| standalone display production identity | [`HMX035CTFT-001-display-rfq.md`](HMX035CTFT-001-display-rfq.md) | H1 main-board geometry closed by replaceable `L2-DISP-ADP-001-A`; HMX donor route rejected and optional no-order identity evidence retained | exact documented production panel and deterministic factory mating close before release; owner verifies image/backlight/touch in H7/H8 |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | H1 paper geometry closed with pass-through `HLE-107-02-G-DV-PE-LC`; optional manufacturer confirmation retained | exact U214 is packed with the sole prototype; owner performs ordinary mating, continuity and retention checks in H7/H8 |
| dual-SA818S lead time and final assembly | [`original inquiry`](H5.0.3-R1-no-order-supplier-inquiry.md) + [`partial reply`](H5.0.3-R1-jlcpcb-response-2026-08-26.md) + [`machine record`](H5.0.3-R1-supplier-response.json) + [`clarification draft`](H5.0.3-R1-jlcpcb-clarification-reply.md) | JLCPCB confirms exact VHF MOQ 1, typical 8–15-working-day pre-order and conditional Function Test pricing; accumulators are owner-confirmed `J5-U`, not part of delivery or supplier gate; `H5-EVR07` remains fail-closed with 16 unanswered fields | supplier confirms the actual two-designator U/V job and itemizes remaining `J4-F/P` plus exact-MPN control |
| optional Parts API | [`H5.0.3-R1-parts-api-support-inquiry.md`](H5.0.3-R1-parts-api-support-inquiry.md) | support attributes rejection to a new account with no order history, but is not the API review team and gives no threshold; no reapplication submitted | Parts is actually approved after sufficient order history or an accepted exception case; manual evidence remains authoritative meanwhile |
| fallback full-device factory | [`H5.0.3-R1-pcbway-fallback-inquiry.md`](H5.0.3-R1-pcbway-fallback-inquiry.md) + [`H5-EVR08`](../verification/generated/H5-EVR08-fallback-factory-readiness.json) | PCBWay publicly covers the needed supplier/PCBA/test/OEM classes; Seeed is retained as PCBA-only second source; no fallback contact is authorized or sent | if JLCPCB fails `H5-EVR07`, obtain separate authority and submit the same no-order gate questionnaire to PCBWay |
| sole-prototype article manifest | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | 30-line `$232.52` known-material manifest published; all 210 sourcing/final-assembly routes mapped and purchase not authorized | supplier-response gates close, H6/F-PO release, then the existing one-prototype order approval; no separate sample/coupon decision |

The current schematic specification and pre-layout review do not authorize a
purchase. KiCad PCB placement/routing and prototype fabrication also remain
separate later gates.
