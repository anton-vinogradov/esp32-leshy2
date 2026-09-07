# Physical source register

[Hardware](hardware.md) · [Roadmap](roadmap.md) · [Русский](physical-source-register.ru.md)

This is the retained H1 concept source register, not the current H6 native-PCB inventory.
R2 replacements and retirements are applied by the [H1 concept model](h1-r2-physical-layout.md);
use the [native H6 views](h6-r2-component-views.md) and [interface review](h6-r2-interface-review.md) for current geometry and open findings.
Each body in this historical source register has one machine row with
an exact selected MPN (or an explicit TBD), manufacturer-backed envelope, named
coordinate frame, orientation and interface direction. Historical H1 closure does not prove current
PCB correspondence, close H6 geometry gates or authorize manufacture; received fit, RF, acoustic, thermal and ordinary-operation checks remain separate.

| Coverage | Result |
|---|---:|
| Rendered physical instances | 231 |
| Exact-MPN instances | 231 |
| Explicit MPN TBD instances | 0 |
| H1 geometry blockers | 0 |
| H5 received-sample gates | 14 |

## Coordinate frames

| Frame | Datum | Bodies |
|---|---|---:|
| `display-assembly` | ER-TFT035IPS-6 + ER-TPC035-6 configured CTP-outline top-left, front view | 1 |
| `front-outer` | UI PCB top-left, viewed from the front/exterior | 31 |
| `rear-outer` | RF/power PCB top-left, viewed from the rear/exterior | 13 |
| `rf-inner` | RF/power PCB top-left, viewed from the rear/exterior | 148 |
| `rf-inner-route` | RF/power PCB top-left, viewed from the rear/exterior | 3 |
| `ui-inner` | UI PCB top-left, viewed from the front/exterior | 33 |
| `ui-inner-route` | UI PCB top-left, viewed from the front/exterior | 2 |

The complete per-instance table is retained as
[`H1-physical-source-table.json`](../hardware/product-design/generated/H1-physical-source-table.json)
as the historical rendering seed, not as authority to move current native components. The resolved
front-facing X/Y/Z projection is
[`H1-unified-coordinate-table.json`](../hardware/product-design/generated/H1-unified-coordinate-table.json).
