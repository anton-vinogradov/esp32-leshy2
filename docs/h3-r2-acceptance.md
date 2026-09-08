# H3-R2 · current electrical diagnostics

[Русский](h3-r2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `applicability:crosscheck_inputs`.

[Machine evidence](../hardware/verification/generated/H3-R2-acceptance-package.json).

This publication recomputes 20 evidence artifacts and checks 155 source bindings. Source mismatches: 0. Open aggregate findings: 3. Current applicability is **not** inherited from historical H3 closure.

## Current analytical work

Raw supply, protected local supply and consumer endpoints are separate. The retained MAIN model still uses parameters for a different converter, has unqualified current/protection and thermal limits, and the AON resistance is not bound to the fitted setting. Existing numerical calculations are provisional, not permission to treat these inputs as qualified. The supervisor assertion maximum and minimum hysteresis also remain unspecified.

- H3-R2.1/rail-margins: review_required
- H3-R2.1/source-margins: review_required
- H3-R2.1/result: review_required
- H3-R2.2/sequences: review_required
- H3-R2.2/handover: review_required
- H3-R2.2/inrush-watchdog: review_required
- H3-R2.2/result: review_required
- H3-R2.3/result: review_required
- H3-R2.4/result: review_required
- H3-R2.5/result: review_required
- H3-R2.6/result: review_required

## Separate physical and firmware evidence

The [physical registry](physical-evidence-register-r2.md) retains 51 open rows with explicit owners. Those rows do not replace the analytical findings above. The F5/F6 i8080 implementation and `H6-NATIVE-ELECTRICAL-SEMANTICS` gate remain separate obligations; this report does not close them.

The next work is correction and verification of the current power model. Fresh diagnostics and matching hashes do not advance a phase or authorize hardware operation.

[Machine cross-check](../hardware/verification/generated/H3-R2-crosscheck.json)
