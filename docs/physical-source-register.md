# Physical source register

[Hardware](hardware.md) · [Roadmap](roadmap.md) · [Русский](physical-source-register.ru.md)

Every body drawn in the product views is generated from one machine row with
an exact selected MPN (or an explicit TBD), manufacturer-backed envelope, named
coordinate frame, orientation and interface direction. No H1 geometry blocker
remains; received fit, RF, acoustic, thermal and endurance checks stay in H5.

| Coverage | Result |
|---|---:|
| Rendered physical instances | 171 |
| Exact-MPN instances | 171 |
| Explicit MPN TBD instances | 0 |
| H1 geometry blockers | 0 |
| H5 received-sample gates | 13 |

## Coordinate frames

| Frame | Datum | Bodies |
|---|---|---:|
| `display-adapter` | L2-DISP-ADP-001-A top-left, viewed from its panel-facing side | 2 |
| `display-assembly` | HMX035CTFT-001 screen-body top-left, front view | 1 |
| `front-outer` | UI PCB top-left, viewed from the front/exterior | 19 |
| `rear-outer` | RF/power PCB top-left, viewed from the rear/exterior | 15 |
| `rf-inner` | RF/power PCB top-left, viewed from the rear/exterior | 100 |
| `rf-inner-route` | RF/power PCB top-left, viewed from the rear/exterior | 3 |
| `ui-inner` | UI PCB top-left, viewed from the front/exterior | 29 |
| `ui-inner-route` | UI PCB top-left, viewed from the front/exterior | 2 |

The complete per-instance table is retained as
[`H1-physical-source-table.json`](../hardware/product-design/generated/H1-physical-source-table.json)
for deterministic rendering, review and later ECAD transfer. The resolved
front-facing X/Y/Z projection is
[`H1-unified-coordinate-table.json`](../hardware/product-design/generated/H1-unified-coordinate-table.json).
