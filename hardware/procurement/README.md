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
non-exclusive reference, and the full 212-line BOM is mapped to `J0`–`J3`, `J4-F`, `J4-P` or `J5-U`
in the [public manufacturing baseline](../../docs/manufacturing-platform.md).
The controlling state is
[`hardware/verification/h5-component-evidence-plan.json`](../verification/h5-component-evidence-plan.json).

| Gate | Prepared artifact | Current state | Closure condition |
|---|---|---|---|
| exact display and factory installation | [`ER-TFT035IPS-6-display-assembly.md`](ER-TFT035IPS-6-display-assembly.md) | exact `ER-TFT035IPS-6 + ER-TPC035-6 option 5344`, direct `FH34SRJ-50S-0.5SH(50)`, ready-made 3M (TC) `4910SQ-2(5)` 50.8-mm PSA candidate and the relaxed one-fold FPC route are selected; the HMX donor, adapter, untraceable reseller pads and full 33-m tape roll are rejected routes | current-lot dry fit proves the ≤24.66-mm neutral-axis path, ≥5.00-mm relaxed reserve, ≤0.714-mm folded stack and ≥0.20-mm pad clearance; written factory acceptance covers customer-supplied pad, supported 100-kPa application and dwell; owner verifies image/backlight/touch in H7/H8 |
| exact U214 mating stack | [`U214-mating-data-request.md`](U214-mating-data-request.md) | H1 paper geometry closed with pass-through `HLE-107-02-G-DV-PE-LC`; optional manufacturer confirmation retained | exact U214 is packed with the sole prototype; owner performs ordinary mating, continuity and retention checks in H7/H8 |
| dual-SA818S lead time and final assembly | [`original inquiry`](H5.0.3-R1-no-order-supplier-inquiry.md) + [`initial reply`](H5.0.3-R1-jlcpcb-response-2026-08-26.md) + [`substantive 2 September reply`](H5.0.3-R1-jlcpcb-response-2026-09-02.md) + [`machine record`](H5.0.3-R1-supplier-response.json) + [`ticket merge notice`](H5.0.3-R1-jlcpcb-ticket-merge-2026-09-02.md) | JLCPCB confirms exact `SA818S-U/V` placement at separate designators, exact-MPN incoming control and no replacement without confirmation. It also sets PCBA MOQ 2, defers adhesive/FPC/microcoax feasibility until after order and explicitly declines complete enclosure/final-device assembly. `H5-EVR07` therefore records an explicit required-operation failure. The substantive reply went to the original ticket address `av@apache.org` and appears in Gmail account `no.mail.in@gmail.com`; the merge notice separately reached `vinogradov.anton@gmail.com` | JLCPCB is retained as PCBA-only; full-device closure moves to the active PCBWay gate |
| optional Parts API | [`H5.0.3-R1-parts-api-support-inquiry.md`](H5.0.3-R1-parts-api-support-inquiry.md) | support attributes rejection to a new account with no order history, but is not the API review team and gives no threshold; no reapplication submitted | Parts is actually approved after sufficient order history or an accepted exception case; manual evidence remains authoritative meanwhile |
| active full-device factory | [`sent PCBWay inquiry`](H5.0.3-R1-pcbway-fallback-inquiry.md) + [`H5-EVR08`](../verification/generated/H5-EVR08-fallback-factory-readiness.json) | After JLCPCB's explicit final-device decline, PCBWay is the active candidate. The information-only exact-one questionnaire was sent on 2026-09-02 from `vinogradov.anton@gmail.com` to `service@pcbway.com`; Gmail confirmed submission. Seeed remains the PCBA-only second source. No quote, sourcing request, reservation, purchase or order was created | PCBWay supplies a written line-by-line answer for exact SA818S-U/V, the four required final-assembly operations and exact-MPN/no-substitution control |
| sole-prototype article manifest | [`pre-kicad-sample-plan.md`](pre-kicad-sample-plan.md) | 32-line `$265.91` known-material manifest published, including exact panel and one ready-cut `3M (TC) 4910SQ-2(5)`; all 212 sourcing/final-assembly routes mapped and purchase not authorized | measured display-stack and written J4-F process gates close, supplier-response gates close, H6/F-PO release, then the existing one-prototype order approval; no separate sample/coupon decision |

The current schematic specification and pre-layout review do not authorize a
purchase. KiCad PCB placement/routing and prototype fabrication also remain
separate later gates.
