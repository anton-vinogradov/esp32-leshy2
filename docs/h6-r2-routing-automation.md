# H6 · Routing benchmark

[Home](../README.md) · [Current PCBs](h6-r2-current-routing.md) · [Русский](h6-r2-routing-automation.ru.md)

**2026-09-16: experiments on copies only. Production routing is paused.** Minimize recurring model-token cost while retaining checkable results; use laptop computation for automatic search.

Owner-confirmed target: rebuild each board variant from schematic, placement and verified constraints/recipes, rather than stitching it into historical routing. Upfront development is justified by repeated rebuilds. Run all checks automatically on **every** build; the model handles exceptions only. Full clean rebuilding is not yet demonstrated: these experiments preserve source copper outside the added region. Machine tests cover stated properties, not physical qualification of the first prototype.

## Measured result

**The primary metric is model tokens per complete checked result, not engine seconds.** Separate one-time development/audit from repeat operation. During the 00:20–00:39 UTC research pass, the root-task journal recorded **about 157k uncached input + output tokens** (a cost proxy), 3.757M including reread cached context, 36 recorded tool calls and one compaction. This is not billing/quota; separate usage for one agent with three bounded assignments is unverified, and subsequent work after the snapshot is excluded. Zero model calls inside the engine **does not mean zero total research cost**.

| Region | Connections | Three full replays, including checks | Vias | Length |
|---|---:|---:|---:|---:|
| Upper keys, 7 nets | 28/28 | 9.37–9.44 s | 19 | 463.54 mm |
| All keys, 15 nets | 60/60 | 15.15–15.67 s | 43 | 1,153.74 mm |
| Keys + encoder, touch/IR and static IDs, 29 nets | 82/82 | 19.30–20.32 s | 64 | 1,778.56 mm |
| That larger region after moving R64 −0.5 mm in X | 82/82 | 22.37–44.05 s | 64 | 1,778.56 mm |
| First region after moving R64 −0.5 mm in X | 28/28 | 8.87–8.92 s | 19 | 463.51 mm |

Geometry matched within each replay set, excluding UUIDs. Native DRC and parity are clean; original rules, copper and all other nets are preserved. These are geometric candidates: ESD topology, returns and electrical qualification are not claimed.

Eight settings were tested on the small region and twelve on the larger one. The large batch selected its only complete profile and replayed it three times automatically: **238.5 s for the complete search, with zero model calls inside the batch**. Selection: 0.05-mm grid, via cost 75, mps ordering, four permitted layers. Other profiles were incomplete or violated checks; faster incomplete output is not a win.

The 82-connection case is 37% larger by connection count and retains full-board obstacles (421 footprint centres in its ROI). Full search plus three replays took 310.9 s. Another profile also closed 82 connections with 62 vias but failed DRC and was rejected. Net classes were expanded only after exact endpoint review, without changing production policy. After the move, the established profile passed again: four runs in 134.4 s without parameter search or between-attempt intervention. Timing spread is an observation, not proof of acceleration; the changed geometry repeats although total length matches.

Two other R64 moves were rejected before routing due to baseline collisions. The successful move test rebuilds the whole selected block; **it does not prove incremental repair of existing routed copper**.

[Initial attempts and evidence hashes](../hardware/layout/benchmarks/2026-09-16-results.json) · [Larger test and usage counters](../hardware/layout/benchmarks/2026-09-16-larger-results.json). Two initial Python-environment failures and one netcode-renumbering checker failure are accounted for as setup. Integration is outside table timings. Total usage including agents and the savings multiplier against the old method remain unmeasured.

## One command instead of manual iterations

From the repository root, with prepared KRT/Python runtimes from the [pinned profile](../hardware/layout/h6-r2-autorouter-profile.json):

```sh
python3 hardware/layout/h6_r2_autorouter_benchmark.py \
  --case hardware/layout/benchmarks/ui-inputs-service-id-82.json \
  --adaptive --repeat-best 3 --quiet
```

The script creates separate snapshots and tries the manifest's first established profile. Only if independent checks fail does it add the other 11 settings, select a complete passing candidate and replay it three times. Original-rule restoration, every-net checks, DRC/parity, copper preservation and ROI checks remain intact. `--quiet` returns launch/final summaries only; logs/candidates stay on disk. Repeat operation needs one launch and reading its result, without model parameter decisions between attempts. This is a control contract, **not a measurement of total recurring token use**.

For geometric research, retain `--sweep --repeat-best 3 --quiet`: minimize vias among all passing settings, then length, then time. Adaptive mode does not promise globally best geometry: it accepts a checked seed without searching alternatives. Nothing is applied to production PCBs. Changed sources require a newly reviewed manifest; stale hashes are intentionally rejected.

The failing-seed path was also tested: a manifest copy starts with `coarse_via75`. It failed; without intervention the controller added 11 alternatives, selected the only complete passing profile, and performed three identical replays—15 attempts in 304.9 s. This extension contains 34 attempts in total, including failures; negative results are not hidden.

Replay after a change: `--profiles fine_via75 --repeats 3 --move R64 -0.5 0`, using the default small case. Supply engine/runtime locations through `--engine` and `--engine-python`.

Repeat usage measurement locally with `python3 hardware/layout/h6_r2_benchmark_usage.py --session <explicit-journal.jsonl> --since <UTC-time>`. It exports aggregates only; conversation text, journal paths and account identifiers are not copied into the public report. Cached input is separated from uncached input/output; counter resets are rejected.

## Next steps and readiness gate

1. Remove the model from recurring decisions: established profile → automatic fallback → checked replays → compact result. Implemented; next measure an isolated repeat with model usage, without concurrent development. Do not read detailed logs when all gates pass. Do not spend tokens micro-optimizing A* seconds.
2. Test other classes and both executors: KRT and [Freerouting 2.4.1](https://github.com/freerouting/freerouting/releases/tag/v2.4.1). Current automatic policy covers only 342 of 3,085 remaining connections. Ground/power account for 1,724; GPIO results cannot be extrapolated to them, RF or USB. No blanket removal of `manual_only`.
3. Prepare reusable critical islands with impedance, current, return-path and surrounding-region checks; test full rebuild and incremental ECO after placement, schematic, footprint and rule changes. Explicitly measure manual residuals and requalification.
4. Resume production routing only after demonstrating a process for both boards and every class, with no unknown manual-repair workload or untested cheap high-impact acceleration option. Electrical/mechanical gates remain mandatory. Plugin, local LLM and new-engine work wait for measured necessity and payback.
