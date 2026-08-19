# REV-0004I — neutral-input correction before competitor delta

- Статус: **Проведено ревью исправления**
- Дата: 2026-08-16
- Finding: [`FND-0041`](../findings/FND-0041-owner-assumptions-remained-in-neutral-inputs.md)
- Decision: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)

## Проверка

| Check | Result |
|---|---|
| `INV-0002` still fixes C5 IR owner | no; dual-path behavior remains, owner open |
| `INV-0002` still fixes S3 BLE owner | no; native BLE/product-identity requirement remains, owner open |
| active `REQ-IR/W5/W24/BLE` silently reselect exact backend | no; named chips are explicitly reference profiles |
| former `CAP/CON/RES` can be consumed as reviewed neutral prerequisites | no; all are candidate/reference and must be re-derived after G3 |
| root target/current EN/RU pages claim target S3/C5 owners | no |
| firmware target/current pages consume former owners/images/IPC | no |
| capability was removed while reopening owners | no |

## Result

The correction receives **«Проведено ревью»**. This does not close
[`FND-0040`](../findings/FND-0040-current-competitor-benchmark-missing.md): G2
remains in repeat review until every competitor-delta candidate receives owner
disposition and propagation review.
