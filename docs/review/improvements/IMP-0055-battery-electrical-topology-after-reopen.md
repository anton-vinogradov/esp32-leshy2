# IMP-0055 — battery electrical topology after reopen

- Статус: **⚠️ Ожидает решения владельца**
- Дата: 2026-08-18
- Decision that reopened the input: [`DEC-0064`](../decisions/DEC-0064-reopen-battery-electrical-topology.md)
- Comparison: [`PWR-0006`](../architecture/PWR-0006-one-or-two-cell-topology-comparison.md)
- Finding: [`FND-0076`](../findings/FND-0076-parallel-cells-shift-admission-risk.md)
- Affects: `I3`, rail topology, battery mechanics, runtime, cost and firmware state model

## Context

The product still has two physically replaceable 18650 slots, but `2S` is no
longer presumed. Two equal cells have the same watt-hours and ideal cell
current in `2S` and balanced `1S2P`. A `1S` common bus doubles shared current,
requires buck-boost/boost rails and cannot safely connect removable cells
directly. Its unique product benefit is running from either qualified slot.

## Options

### A — retain supervised 2S — recommended

- both cells are required for battery operation;
- lowest shared-path current and simplest efficient 3.3/4/5-V rail tree;
- keeps full two-cell energy and the accepted two replaceable slots;
- `PWR-0005` manager candidate can resume after the choice.

This is the only option presently aligned with lower cost **without** deleting
runtime, a cell slot or peak-load behavior.

### B — controlled two-slot 1S bus

- either admitted cell can run the complete product and removal of the other
  need not interrupt it;
- every slot needs an isolated normally-open power path, protection,
  measurement and bounded precharge before sharing;
- likely adds about `$1…3` in the lower-cost implementation or `$5…8` with two
  integrated MAX17300 gauges, before final RFQ;
- approximately doubles common-path current and changes all major rail classes.

Choose this only if one-cell operation/hot removal is worth the cost and HIL
burden. It is an improvement, not a cost reduction.

### C — one-slot 1S cost-down variant

- simplest cell management and potentially modestly lower hardware cost;
- roughly half the energy/runtime and deletes one accepted physical slot;
- the sole cell must carry the full high-current load.

This is a different reduced-runtime product variant, not a no-loss replacement.

## Recommendation

Accept **A**. Continue from the already reviewed 2S branch, then close exact
cells, manager FETs/fuses/NTCs/shunt and the complete rail/loss/thermal tree.
Keep B documented as a future premium/hot-swap variant rather than making the
base device pay for it.

## Owner decision

Open: choose `A`, `B` or `C`.

