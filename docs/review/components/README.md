# Component/BOM workspace

- Статус: **current I8 workbench active; former stage-4 package historical**
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
9. [`BOM-0009`](BOM-0009-current-orderability-recheck.md) — exact-line source recheck: 187/188 current orderability records and isolated display residue.
10. [`BOM-0010`](BOM-0010-display-procurement-and-alternate-disposition.md) — display specimen/RFQ boundary and explicit no-drop-in policy.

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
- [`BOM-0008`](BOM-0008-consolidated-target-bom-and-avl.md) / [`FND-0109`](../findings/FND-0109-machine-map-was-not-a-complete-physical-bom.md) — machine-derived I8 coverage and explicit physical-gap register; **Проведено ревью inventory coverage**, qualification active.
- [`PWR-0022`](../architecture/PWR-0022-exact-max17320-2s-support-profile.md) / [`DEC-0100`](../decisions/DEC-0100-exact-max17320-2s-support-closure.md) / [`REV-0005BF`](../reviews/REV-0005BF-max17320-support-repair-propagation.md) — exact MAX17320/MSPM0 support repair; **Проведено ревью paper electrical scope**, physical/HIL open.
- [`SAFE-0003`](../architecture/SAFE-0003-exact-actual-tx-threshold-and-isolation.md) / [`DEC-0101`](../decisions/DEC-0101-exact-actual-tx-threshold-and-domain-isolation.md) / [`REV-0005BG`](../reviews/REV-0005BG-actual-tx-threshold-propagation.md) — eight exact threshold networks and AON-to-main evidence isolation; **Проведено ревью paper electrical scope**, measured calibration/HIL open.
- [`BOM-0009`](BOM-0009-current-orderability-recheck.md) / [`FND-0111`](../findings/FND-0111-orderability-audit-exposed-pseudo-mpn-and-display-gap.md) / [`DEC-0102`](../decisions/DEC-0102-exact-sc1512-a4-order-identity.md) / [`REV-0005BH`](../reviews/REV-0005BH-orderability-propagation.md) — previously missing exact-line sources rechecked, `SC1512-A4` order identity repaired and only `HMX035CTFT-001` left unresolved; **Проведено ревью current sourcing batch**, cost/alternates and full I8 remain open.
- [`DSP-0008`](../architecture/DSP-0008-display-procurement-boundary-and-rfq.md) / [`BOM-0010`](BOM-0010-display-procurement-and-alternate-disposition.md) / [`REV-0005BI`](../reviews/REV-0005BI-display-procurement-propagation.md) — exact display donor/specimen sources, production RFQ packet and no-drop-in disposition; **Проведено ревью sourcing strategy**, standalone panel RFQ/HIL open.

Статус `REV-0004A` относится к полноте входного реестра, а не к квалификации перечисленных компонентов.
