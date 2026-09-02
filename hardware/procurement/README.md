# Procurement evidence workspace

These files preserve the reviewed H5 component/factory evidence used by current
H6 layout work. They are not part of the public finished-product narrative, do not
authorize a purchase and do not replace H7/H8 owner bring-up on the sole prototype.
The active policy is source research first, mapping to the selected assembly
platform second, a documented replacement or exact-part sourcing route third,
and one prototype order only after H6/F-PO and explicit approval. There is no
separate engineering-sample or H5 coupon purchase.
H1 through H5, including the joined pre-layout and component/factory reviews,
are complete. H6.0.2-R1 routing and net parity are current after the complete
H6.0.1 placement/mechanical/cable closure. JLCPCB Standard PCBA is the
non-exclusive reference, and the full 210-line BOM is mapped to `J0`–`J3`, `J4-F`, `J4-P` or `J5-U`
in the [public manufacturing baseline](../../docs/manufacturing-platform.md).
The controlling state is
[`hardware/verification/h5-component-evidence-plan.json`](../verification/h5-component-evidence-plan.json).

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| exact display and owner installation | [`ER-TFT035IPS-6-display-assembly.md`](ER-TFT035IPS-6-display-assembly.md) | exact `ER-TFT035IPS-6 + ER-TPC035-6 option 5344`, direct `FH34SRJ-50S-0.5SH(50)`, ready-made 3M (TC) `4910SQ-2(5)` 50.8-mm PSA and the relaxed one-fold FPC route are selected; the HMX donor, adapter, untraceable reseller pads and full 33-m tape roll are rejected routes | current-lot dry fit proves the ≤24.66-mm neutral-axis path, ≥5.00-mm relaxed reserve, correct contact orientation, ≤0.714-mm folded stack and ≥0.20-mm pad clearance before owner bonding; owner verifies image/backlight/touch in H7/H8 |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | H1 paper geometry closed with pass-through `HLE-107-02-G-DV-PE-LC`; optional manufacturer confirmation retained | exact U214 is packed with the sole prototype; owner performs ordinary mating, continuity and retention checks in H7/H8 |
| dual-SA818S and owner final assembly | [`original inquiry`](H5.0.3-R1-no-order-supplier-inquiry.md) + [`initial reply`](H5.0.3-R1-jlcpcb-response-2026-08-26.md) + [`substantive 2 September reply`](H5.0.3-R1-jlcpcb-response-2026-09-02.md) + [`machine record`](H5.0.3-R1-supplier-response.json) + [`ticket merge notice`](H5.0.3-R1-jlcpcb-ticket-merge-2026-09-02.md) | JLCPCB confirms exact `SA818S-U/V` placement at separate designators, exact-MPN incoming control and no replacement without confirmation, with PCBA MOQ 2. The owner accepts post-PCBA display/PSA/FPC, microcoax, knob and enclosure assembly, so the recorded JLCPCB box-build decline is non-gating. The substantive reply went to `av@apache.org` and appears in Gmail account `no.mail.in@gmail.com` | ✅ `H5-EVR07` passes the PCBA supplier gate; H6 creates quoteable outputs and order-time checks final VHF terms/stock |
| optional Parts API | [`H5.0.3-R1-parts-api-support-inquiry.md`](H5.0.3-R1-parts-api-support-inquiry.md) | support attributes rejection to a new account with no order history, but is not the API review team and gives no threshold; no reapplication submitted | Parts is actually approved after sufficient order history or an accepted exception case; manual evidence remains authoritative meanwhile |
| optional full-device comparison | [`sent PCBWay inquiry`](H5.0.3-R1-pcbway-fallback-inquiry.md) + [`H5-EVR08`](../verification/generated/H5-EVR08-fallback-factory-readiness.json) | The information-only exact-one questionnaire was sent on 2026-09-02 from `vinogradov.anton@gmail.com` to `service@pcbway.com`; Gmail confirmed submission. Owner final assembly removes this response from the release gate. Seeed remains the PCBA second source. No commercial action was created | Record PCBWay's answer when it arrives and compare cost/convenience; do not wait before H6 |
| sole-prototype article manifest | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | ✅ 33-line `$267.91` known-material manifest published, including exact panel, ready-cut `3M (TC) 4910SQ-2(5)` and exact `Ettinger 007.02.611` 11-mm stops; all routes mapped and purchase not authorized | H6 locks exact M2.5 nylon screw length and emits Gerber/BOM/CPL; quote and final VHF/stock checks follow immediately before the one order |

The current evidence does not authorize a purchase. KiCad PCB placement/routing
is authorized under H6; prototype fabrication remains a separate later gate.
