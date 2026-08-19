# Component/BOM workspace

- Статус: **I8 and I9 working-candidate paper scopes reviewed; G3 active; former stage-4 package historical**
- Former prerequisite: superseded `DEC-0028/PKG-0001/SYN-3A`
- Current use: candidate facts and risks only

This workspace preserves component facts collected for the former candidate,
but [`BOM-0008`](BOM-0008-consolidated-target-bom-and-avl.md) is now the
current machine-derived I8 workbench. Historical `BOM-0001…0007` rows are not
silently promoted into the target; only current `G2F-3I` instances and its
explicit physical-gap register feed the generated manifest.

## Каноническая цепочка

1. [`BOM-0001`](BOM-0001-stage4-component-evidence-register.md) — полный реестр component functions, evidence state, dependencies и порядок qualification;
2. `BOM-0002` — compute modules, clocks, boot/debug/recovery and compatibility identities;
3. `BOM-0003` — AON/STOP, battery input and all power rails/branch protection;
4. `BOM-0004` — UI/display/touch/storage/USB and non-safety slow control;
5. `BOM-0005` — receive/audio/IR signal chain;
6. `BOM-0006` — packet RF, analog voice and antenna/front-end assemblies;
7. `BOM-0007` — external M5 profiles/connectors/power-isolation;
8. [`BOM-0008`](BOM-0008-consolidated-target-bom-and-avl.md) — current consolidated sourcing, alternates, lifecycle, cost and assembly manifest.
9. [`BOM-0009`](BOM-0009-current-orderability-recheck.md) — exact-line source recheck; current corrected denominator is 186/187 with isolated display residue.
10. [`BOM-0010`](BOM-0010-display-procurement-and-alternate-disposition.md) — display specimen/RFQ boundary and explicit no-drop-in policy.
11. [`BOM-0011`](BOM-0011-assembly-internal-purchase-boundary.md) — explicit assembly-internal node exclusion and corrected 857/187 purchase view.
12. [`BOM-0012`](BOM-0012-complete-substitution-policy.md) — all 187 purchase lines mapped to one conservative no-silent-substitution class.
13. [`BOM-0013`](BOM-0013-first-quantity-100-cost-evidence.md) — validated USD quantity-100 cost contract and first 15/187 exact-MPN lines.
14. [`BOM-0014`](BOM-0014-high-placement-cost-and-explicit-gates.md) — second high-placement price batch: reviewed 23/187-line snapshot and five explicit RFQ/retail gates.
15. [`BOM-0015`](BOM-0015-third-high-placement-cost-evidence.md) — reviewed third-batch snapshot: 39/187 lines / 578 placements / USD 79.0660.
16. [`BOM-0016`](BOM-0016-high-value-ic-rf-cost-evidence.md) — high-value IC/RF fourth-batch checkpoint: 52/187 lines / 614 placements / USD 102.2205 partial base subtotal.
17. [`BOM-0017`](BOM-0017-power-ui-rf-cost-evidence.md) — power/UI/receiver fifth-batch checkpoint: 61/187 lines / 623 placements / USD 109.8573.
18. [`BOM-0018`](BOM-0018-audio-power-mechanical-cost-evidence.md) — audio/power/mechanical sixth-batch checkpoint plus two currency-comparability gates: 76/187 lines / 643 placements / USD 130.7216 partial base subtotal.
19. [`BOM-0019`](BOM-0019-high-placement-passive-cost-evidence.md) — high-placement passive/discrete seventh-batch checkpoint: 91/187 lines / 708 placements / USD 133.4711 partial base subtotal.
20. [`BOM-0020`](BOM-0020-control-protection-rf-cost-evidence.md) — control/protection/RF-passive eighth-batch checkpoint: 106/187 lines / 747 placements / USD 140.7642 partial base subtotal.
21. [`BOM-0021`](BOM-0021-control-logic-passive-cost-evidence.md) — control/logic/passive ninth-batch checkpoint plus one RFQ gate: 118/187 lines / 771 placements / USD 142.1808 partial base subtotal.
22. [`BOM-0022`](BOM-0022-rf-timing-indicator-passive-cost-evidence.md) — RF/timing/indicator/passive tenth-batch checkpoint: 133/187 lines / 787 placements / USD 143.6995 partial base subtotal.
23. [`BOM-0023`](BOM-0023-logic-interface-ir-cost-evidence.md) — logic/interface/IR eleventh-batch checkpoint: 148/187 lines / 802 placements / USD 150.1783 partial base subtotal.
24. [`BOM-0024`](BOM-0024-resistor-cost-evidence.md) — exact-resistor twelfth-batch checkpoint: 162/187 lines / 816 placements / USD 150.4157 partial base subtotal.
25. [`BOM-0025`](BOM-0025-specialty-cost-and-gates.md) — specialty-component thirteenth-batch checkpoint: 169/187 lines / 823 placements / USD 157.1927 partial base subtotal and twelve explicit gates.
26. [`BOM-0026`](BOM-0026-high-q-rf-capacitor-cost-evidence.md) — exact high-Q RF-capacitor fourteenth batch, current 175/187 lines / 829 placements / USD 157.3727 partial base subtotal; all twelve remaining unpriced lines have explicit gates.
27. [`BOM-0027`](BOM-0027-physical-purchase-family-resolution-gates.md) — machine-readable prerequisite and acceptance gates for all four physical purchase families / 28 items; exact MPN and physical HIL remain open.
28. [`BOM-0028`](BOM-0028-i8-consolidated-paper-procurement-review.md) — consolidated I8 paper procurement-feasibility review; separates reviewed candidate evidence from downstream G3/G8 exact physical/frozen-BOM work.

Каждый `BOM-*` сначала проверяет primary facts, затем electrical/reset/pin fit, supply/AVL/cost и HIL/substitution evidence. Следующий artifact не использует строку как закрытый пререквизит, пока соответствующее review явно не дало статус **«Проведено ревью»**.

## Правила

- exact architecture-locked part нельзя заменить «аналогом» только по названию или цене;
- conditional candidate не становится target до полного evidence и явного disposition;
- abstract circuit function обязательно получает exact implementation до schematic stage;
- external accessory не попадает в base BOM, но его connector/power/isolation обязан попасть;
- zero-loss saving требует proof capability, performance, safety, reliability, autonomy, serviceability and testability equivalence;
- по `DEC-0029` newest stable manufacturer-supported hardware revision предпочтительна на BOM freeze только после compatibility/errata/toolchain/supply/requalification proof; больший номер не означает automatic substitution;
- новая лишняя функция/деталь сначала помечается и выносится владельцу как **⚠️ Предложение**, если она не является очевидным implementation prerequisite уже принятого target;
- component mismatch создаёт finding; молчаливое изменение owner/pin/power/STOP/RF/update contract запрещено.

## Review

- [`REV-0004A`](../reviews/REV-0004A-stage4-entry-register.md) — completeness и ordering реестра; **Проведено ревью**.
- [`REV-0004B`](../reviews/REV-0004B-compute-clock-recovery-evidence.md) — compute/clock/recovery primary facts; **Проведено ревью фактов**.
- [`REV-0004C`](../reviews/REV-0004C-c5-v1.2-propagation.md) — C5 v1.2 production floor; **Проведено ревью**.
- [`REV-0004D`](../reviews/REV-0004D-compute-cad-library-audit.md) — historical availability/provenance audit; **Проведено ревью фактов**.
- [`REV-0004E`](../reviews/REV-0004E-vendored-critical-cad-libraries.md) — `DEC-0030/IMP-0025-A`, project-local critical CAD snapshot, provenance and tests; **Проведено ревью**.
- [`REC-0001`](REC-0001-compute-recovery-and-link-prerequisites.md) / [`REV-0004F`](../reviews/REV-0004F-compute-recovery-link-prerequisites.md) — ROM/debug/link prerequisites and corrected C5 strap; **Проведено ревью**.
- [`SVC-0001`](SVC-0001-three-domain-development-access.md) / [`REV-0004G`](../reviews/REV-0004G-three-domain-development-access.md) — historical permanent-access topology review.
- [`SVC-0002`](../architecture/SVC-0002-exact-three-domain-service-recovery-boundary.md) / [`REV-0005BE`](../reviews/REV-0005BE-i7-service-recovery-propagation.md) — exact USB/DBG10/BOOT/RESET and conflict-free hard-STOP reset implementation; **Проведено ревью paper electrical scope**, physical/HIL open.
- [`BOM-0008`](BOM-0008-consolidated-target-bom-and-avl.md) / [`FND-0109`](../findings/FND-0109-machine-map-was-not-a-complete-physical-bom.md) — machine-derived I8 coverage and explicit physical-gap register; **Проведено ревью inventory checkpoint**, later consolidated by `BOM-0028/REV-0005CC`.
- [`PWR-0022`](../architecture/PWR-0022-exact-max17320-2s-support-profile.md) / [`DEC-0100`](../decisions/DEC-0100-exact-max17320-2s-support-closure.md) / [`REV-0005BF`](../reviews/REV-0005BF-max17320-support-repair-propagation.md) — exact MAX17320/MSPM0 support repair; **Проведено ревью paper electrical scope**, physical/HIL open.
- [`SAFE-0003`](../architecture/SAFE-0003-exact-actual-tx-threshold-and-isolation.md) / [`DEC-0101`](../decisions/DEC-0101-exact-actual-tx-threshold-and-domain-isolation.md) / [`REV-0005BG`](../reviews/REV-0005BG-actual-tx-threshold-propagation.md) — eight exact threshold networks and AON-to-main evidence isolation; **Проведено ревью paper electrical scope**, measured calibration/HIL open.
- [`BOM-0009`](BOM-0009-current-orderability-recheck.md) / [`FND-0111`](../findings/FND-0111-orderability-audit-exposed-pseudo-mpn-and-display-gap.md) / [`DEC-0102`](../decisions/DEC-0102-exact-sc1512-a4-order-identity.md) / [`REV-0005BH`](../reviews/REV-0005BH-orderability-propagation.md) — previously missing exact-line sources rechecked, `SC1512-A4` order identity repaired and only `HMX035CTFT-001` left unresolved; **Проведено ревью current sourcing batch**, cost/specific-alternate qualification and full I8 remain open.
- [`DSP-0008`](../architecture/DSP-0008-display-procurement-boundary-and-rfq.md) / [`BOM-0010`](BOM-0010-display-procurement-and-alternate-disposition.md) / [`REV-0005BI`](../reviews/REV-0005BI-display-procurement-propagation.md) — exact display donor/specimen sources, production RFQ packet and no-drop-in disposition; **Проведено ревью sourcing strategy**, standalone panel RFQ/HIL open.
- [`FND-0112`](../findings/FND-0112-assembly-internal-controller-was-double-counted.md) / [`BOM-0011`](BOM-0011-assembly-internal-purchase-boundary.md) / [`DEC-0103`](../decisions/DEC-0103-separate-architecture-nodes-from-purchase-bom.md) / [`REV-0005BJ`](../reviews/REV-0005BJ-assembly-internal-bom-propagation.md) — ST77922 remains a distinct architecture node but is no longer double-counted as a purchase line; **Проведено ревью corrected purchasing coverage**.
- [`BOM-0012`](BOM-0012-complete-substitution-policy.md) / [`DEC-0104`](../decisions/DEC-0104-complete-no-silent-substitution-policy.md) / [`REV-0005BK`](../reviews/REV-0005BK-substitution-policy-propagation.md) — exactly one conservative substitution/requalification class for every current purchase line; **Проведено ревью policy coverage 187/187**, specific alternates stay evidence-driven.
- [`BOM-0013`](BOM-0013-first-quantity-100-cost-evidence.md) / [`DEC-0105`](../decisions/DEC-0105-machine-readable-quantity-100-cost-evidence.md) / [`REV-0005BL`](../reviews/REV-0005BL-first-cost-evidence-propagation.md) — strict comparable-price contract plus first 15/187 lines and 22/857 placements; **Проведено ревью first batch**, USD 57.2502 remains a partial base-product subtotal, not COGS.
- [`BOM-0014`](BOM-0014-high-placement-cost-and-explicit-gates.md) / [`DEC-0106`](../decisions/DEC-0106-explicit-unpriced-cost-gates.md) / [`REV-0005BM`](../reviews/REV-0005BM-second-cost-evidence-propagation.md) — eight high-placement prices plus five explicit RFQ/retail gates; **Проведено ревью second-batch snapshot**, 23/187 lines / 440/857 placements and USD 68.8226 partial base subtotal at that checkpoint.
- [`BOM-0015`](BOM-0015-third-high-placement-cost-evidence.md) / [`REV-0005BN`](../reviews/REV-0005BN-third-cost-evidence-propagation.md) — 16 further exact-MPN quantity-100 prices and three source-link repairs; **Проведено ревью third-batch snapshot**.
- [`BOM-0016`](BOM-0016-high-value-ic-rf-cost-evidence.md) / [`REV-0005BO`](../reviews/REV-0005BO-high-value-cost-evidence-propagation.md) — 13 higher-value IC/RF/interconnect prices; **Проведено ревью fourth-batch checkpoint**, 52/187 lines / 614/857 placements and USD 102.2205 partial base subtotal.
- [`BOM-0017`](BOM-0017-power-ui-rf-cost-evidence.md) / [`REV-0005BQ`](../reviews/REV-0005BQ-power-ui-rf-cost-evidence-propagation.md) — nine exact power/UI/RF prices and one explicit new-part quotation gate; **Проведено ревью fifth batch**, current coverage 61/187 lines / 623/857 placements and USD 109.8573 partial base subtotal.
- [`BOM-0018`](BOM-0018-audio-power-mechanical-cost-evidence.md) / [`REV-0005BR`](../reviews/REV-0005BR-audio-power-mechanical-cost-propagation.md) — 15 exact audio/power/mechanical prices, two currency-comparability gates and one exact source-link repair; **Проведено ревью sixth-batch checkpoint**.
- [`BOM-0019`](BOM-0019-high-placement-passive-cost-evidence.md) / [`REV-0005BS`](../reviews/REV-0005BS-high-placement-passive-cost-propagation.md) — 15 exact high-placement passive/discrete prices; **Проведено ревью seventh-batch checkpoint**.
- [`BOM-0020`](BOM-0020-control-protection-rf-cost-evidence.md) / [`REV-0005BT`](../reviews/REV-0005BT-control-protection-rf-cost-propagation.md) — 15 exact control/protection/RF-passive prices and one high-Q RF quote gate; **Проведено ревью eighth-batch checkpoint** at 106/187 lines / 747/857 placements and USD 140.7642 partial base subtotal.
- [`BOM-0021`](BOM-0021-control-logic-passive-cost-evidence.md) / [`REV-0005BU`](../reviews/REV-0005BU-control-logic-passive-cost-propagation.md) — 12 exact control/logic/passive prices and one balance-resistor quote gate; **Проведено ревью ninth-batch checkpoint**.
- [`BOM-0022`](BOM-0022-rf-timing-indicator-passive-cost-evidence.md) / [`REV-0005BV`](../reviews/REV-0005BV-rf-timing-indicator-passive-cost-propagation.md) — 15 exact RF/timing/indicator/passive prices; **Проведено ревью tenth-batch checkpoint**.
- [`BOM-0023`](BOM-0023-logic-interface-ir-cost-evidence.md) / [`REV-0005BW`](../reviews/REV-0005BW-logic-interface-ir-cost-propagation.md) — 15 exact logic/interface/IR prices; **Проведено ревью eleventh-batch checkpoint**.
- [`BOM-0024`](BOM-0024-resistor-cost-evidence.md) / [`REV-0005BX`](../reviews/REV-0005BX-resistor-cost-propagation.md) — 14 exact resistor prices; **Проведено ревью twelfth-batch checkpoint**.
- [`BOM-0025`](BOM-0025-specialty-cost-and-gates.md) / [`REV-0005BY`](../reviews/REV-0005BY-specialty-cost-gate-propagation.md) — seven exact specialty prices, two explicit gates and one source repair; **Проведено ревью thirteenth-batch checkpoint** at 169/187 lines / 823/857 placements and USD 157.1927 partial base subtotal.
- [`BOM-0026`](BOM-0026-high-q-rf-capacitor-cost-evidence.md) / [`REV-0005CA`](../reviews/REV-0005CA-high-q-rf-capacitor-cost-propagation.md) — six exact high-Q RF-capacitor prices; **Проведено ревью fourteenth batch**, current coverage 175/187 lines / 829/857 placements and USD 157.3727 partial base subtotal, with explicit gates on all twelve remaining unpriced lines.
- [`BOM-0027`](BOM-0027-physical-purchase-family-resolution-gates.md) / [`REV-0005CB`](../reviews/REV-0005CB-physical-purchase-gate-propagation.md) — explicit owner/prerequisite/acceptance contracts for 4/4 physical purchase families / 28 items; **Проведено ревью gate coverage**, exact parts and physical/HIL results stay open.
- [`FND-0115`](../findings/FND-0115-i8-exit-mixed-g2f-with-downstream-g8.md) / [`BOM-0028`](BOM-0028-i8-consolidated-paper-procurement-review.md) / [`REV-0005CC`](../reviews/REV-0005CC-i8-consolidated-paper-procurement-propagation.md) — circular G2F/G3/G8 exit repaired; **I8 paper procurement-feasibility scope проведено ревью**.
- [`FND-0116`](../findings/FND-0116-i9-abstract-and-stage-labels-were-not-closed.md) / [`I9-0001`](../architecture/I9-0001-joint-candidate-paper-projection-review.md) / [`REV-0005CD`](../reviews/REV-0005CD-i9-joint-candidate-projection-propagation.md) — all machine boundaries jointly classified; **I9 working-candidate paper scope проведено ревью**, G3 active.

Статус `REV-0004A` относится к полноте входного реестра, а не к квалификации перечисленных компонентов.
