# H6 · Routing benchmark

[Home](../README.md) · [Current PCBs](h6-r2-current-routing.md) · [Русский](h6-r2-routing-automation.ru.md)

**2026-09-16: experiments on copies only. Production routing is paused.** Minimize recurring model-token cost while retaining checkable results; use laptop computation for automatic search.

## Measured result

| Region | Connections | Three full replays, including checks | Vias | Length |
|---|---:|---:|---:|---:|
| Upper keys, 7 nets | 28/28 | 9.37–9.44 s | 19 | 463.54 mm |
| All keys, 15 nets | 60/60 | 15.15–15.67 s | 43 | 1,153.74 mm |
| First region after moving R64 −0.5 mm in X | 28/28 | 8.87–8.92 s | 19 | 463.51 mm |

Geometry matched within each replay set, excluding UUIDs. Native DRC and parity are clean; original rules, copper and all other nets are preserved. These are geometric candidates: ESD topology, returns and electrical qualification are not claimed.

Eight settings were tested on the small region and twelve on the larger one. The large batch selected its only complete profile and replayed it three times automatically: **238.5 s for the complete search, with zero model calls inside the batch**. Selection: 0.05-mm grid, via cost 75, mps ordering, four permitted layers. Other profiles were incomplete or violated checks; faster incomplete output is not a win.

Two other R64 moves were rejected before routing due to baseline collisions. The successful move test rebuilds the whole selected block; **it does not prove incremental repair of existing routed copper**.

[Every attempt's metrics and evidence hashes](../hardware/layout/benchmarks/2026-09-16-results.json). Two initial Python-environment failures and one netcode-renumbering checker failure are accounted for as setup. One-time integration is outside the table's timings; total token consumption and the savings multiplier are not yet measured.

## One command instead of manual iterations

From the repository root, with prepared KRT/Python runtimes from the [pinned profile](../hardware/layout/h6-r2-autorouter-profile.json):

```sh
python3 hardware/layout/h6_r2_autorouter_benchmark.py \
  --case hardware/layout/benchmarks/ui-controls-60.json \
  --sweep --repeat-best 3
```

The script creates separate snapshots, searches 12 profiles, restores original rules after the engine, and checks every net, DRC/parity and region boundaries. Among complete passing candidates it minimizes vias, then length, then time; it replays the winner three times. Logs/candidates stay in `work/routing-benchmark-*`; output is a compact summary. Nothing is applied to production PCBs. Changed sources require a newly reviewed manifest; stale hashes are intentionally rejected.

Replay after a change: `--profiles fine_via75 --repeats 3 --move R64 -0.5 0`, using the default small case. Supply engine/runtime locations through `--engine` and `--engine-python`.

## Next steps and readiness gate

1. Use batch comparisons, not a model invocation per attempt. Scale successful methods and retain negative results; improve only measured bottlenecks.
2. Test other classes and both executors: KRT and [Freerouting 2.4.1](https://github.com/freerouting/freerouting/releases/tag/v2.4.1). Current automatic policy covers only 342 of 3,085 remaining connections. Ground/power account for 1,724; GPIO results cannot be extrapolated to them, RF or USB. No blanket removal of `manual_only`.
3. Prepare reusable critical islands with impedance, current, return-path and surrounding-region checks; test full rebuild and incremental ECO after placement, schematic, footprint and rule changes. Explicitly measure manual residuals and requalification.
4. Resume production routing only after demonstrating a process for both boards and every class, with no unknown manual-repair workload or untested cheap high-impact acceleration option. Electrical/mechanical gates remain mandatory. Plugin, local LLM and new-engine work wait for measured necessity and payback.
