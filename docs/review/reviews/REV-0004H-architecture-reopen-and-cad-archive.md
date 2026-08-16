# REV-0004H — architecture reopen and premature-CAD archive

- Статус: **Проведено ревью исправления**
- Дата: 2026-08-16
- Decision: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)
- Finding: [`FND-0039`](../findings/FND-0039-architecture-frozen-before-product-design.md)

## Review matrix

| Check | Result |
|---|---|
| owner selected reopen option A | yes |
| current architecture still presented as final | no; `DEC-0028/PKG-0001/SYN-3A` superseded as target and retained as candidate/reference |
| accepted capabilities silently dropped | no |
| all selected programmable chips still require independent programming/recovery/diagnostics | yes; retained as implementation-neutral requirement |
| exact three-USB/DBG10/pin/component topology still normative | no; returned to candidate space |
| active exact compute/service CAD remains | no; snapshots archived outside active `hardware/kicad` |
| old CAD CI can imply canonical status | no; workflow archived with snapshot |
| correct product/optimality/concept-placement gates precede architecture | yes; `FLOW-0001` |
| target/current-state documents in both repositories distinguish requirement from candidate | yes |
| final architecture or component Q accidentally granted | no |

## Corrected mismatch ledger

| Mismatch | Correction | Status |
|---|---|---|
| electronic placement study called whole-product optimum | reclassified as candidate/reference | closed |
| exact pins/components consumed before physical design | downstream work stopped and archived | closed |
| permanent debug-access requirement conflated with one connector/pin solution | requirement retained; implementation reopened | closed |
| stage ordering placed physical design after architecture/BOM | product design and conceptual co-design moved before atomic architecture/component/CAD gates | closed |

This review closes only the correction. `G3` target product design is now the
active open stage; it has not yet received **«Проведено ревью»**.
