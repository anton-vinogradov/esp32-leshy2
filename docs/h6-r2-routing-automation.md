# H6 · Routing benchmark

[Home](../README.md) · [Current PCBs](h6-r2-current-routing.md) · [Русский](h6-r2-routing-automation.ru.md)

**2026-09-16: experiments on copies only. Production routing is paused.** Minimize recurring model-token cost while retaining checkable results; use laptop computation for automatic search.

Owner-confirmed target: **every invocation rebuilds all routing from scratch** using the schematic, chosen placement and verified constraints/recipes. Previous-build traces are not inputs to the next build; critical islands are regenerated from verified recipes. Within one invocation the algorithm may rip up its unsuccessful routes and try again. Upfront development is justified by repeated rebuilds. Run all checks automatically on **every** build; the model handles exceptions only. Full clean rebuilding is not yet demonstrated: current experiments preserve untested source copper only to isolate the experiment. Machine tests cover stated properties, not physical qualification of the first prototype.

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

The expansion to **UI 252 + RF 222 = 474 connections** has not passed the strict gate in full. The [eight cold-candidate queue](../hardware/layout/benchmarks/2026-09-16-parallel-474-results.json) finished in 330.6 s with 0 complete passing candidates; best partial results were UI 243/252 and RF 220/222. None is accepted: opens and DRC violations remain. The preceding serial stock search also produced no complete result: eight UI attempts, six completed RF attempts, then the next attempt was stopped to switch to parallel scheduling. Production boards remain unchanged.

Concrete engine NPTH-clearance defects were identified in smoothing and rule resynchronization, followed by a separate via-handling path. Disabling the first two mechanisms helped some candidates but did not eliminate the defect universally. A [local patch](../hardware/layout/engine-patches/README.md) aligned via obstacles, nudging and internal DRC without relaxing rules. The [next eight candidates](../hardware/layout/benchmarks/2026-09-16-patched-474-results.json) completed in 269.5 s with no hole-clearance violations in any candidate and all 1,218 footprints confirmed. Two matched RF candidates reduced DRC findings from 8 to 2 while retaining their 3/2 open connections. At that stage complete passes remained 0: opens and dangling vias persist. Search depth and blocker selection were tested next; their result follows below. The second queue sampled 8 engines, 742.5% CPU, 6.53 GiB RSS and zero swap; different candidate sets prevent a clean queue-speedup claim.

The next [RF repeatability test](../hardware/layout/benchmarks/2026-09-16-rf-222-replay-results.json) passed: **222/222 connections, two alternative profiles × four identical cold results**, an initial attempt plus three replays for each profile. These are the same 222 connections, not 444. The unchanged `tools/route_board.py` criterion passed: zero DRC/parity/ROI findings, all 1,218 footprints retained, original dependencies and unselected copper preserved. Selected-only rip-up of up to five blockers and an upfront 0.30-mm board-edge clearance helped. Each engine run took 110.7–114.8 s and native validation 8.7–9.5 s; no model decisions occurred inside the series. All eight first native checks aborted in the restricted environment: those failures were preserved, and the same candidates passed validation outside it without rerouting. This qualifies block geometry, not an entire board or electrical behavior; UI 252 remains unaccepted. Production PCBs were unchanged.

Preparation cost is recorded too: the **00:49–02:59 UTC** pass used **909,031 uncached-input + output tokens** in the root-task diagnostic proxy (773,359 + 135,672), alongside 32,446,720 cached input tokens, 264 tool calls and three compactions. Child-agent inclusion is unverified; work after the snapshot is excluded. The interval includes routing preparation and concurrent price/documentation work. This is not repeat routing cost or billing. No model decisions occurred inside the eight RF attempts, but **preparation has not demonstrated payback yet**.

Transferring the idea to UI did not succeed: [two new cold candidates](../hardware/layout/benchmarks/2026-09-16-ui-rip-pilot-results.json) each left 7 of 252 connections open; one had zero DRC findings and the other two dangling vias. Both were rejected. The successful RF profile does not automatically generalize to the other board.

## One command instead of manual iterations

The combined UI 252 + RF 222 experiment now has one command:

```sh
python3 tools/route_474.py
```

It uses the prepared pinned KRT with the published NPTH patch; override runtime locations with `--engine-root` and `--engine-python`. A bounded native check of both original copies precedes routing. The [portfolio](../hardware/layout/h6-r2-474-portfolio.json) allows at most 12 initial UI profiles, one additional round of four automatically derived failed-first orders and two RF profiles. A passing block receives three fresh cold replays instead of further search. Up to eight engines run concurrently; a 0.025-mm grid reserves two resource units, while native checks remain serial. Caffeinate, process-group cancellation, immutable inputs, the exact 1,218-footprint inventory and all-net checks are included. Details stay in `work/`; stdout returns compact JSON. Only `status=pass`, `resolved=474` and exit 0 qualify both blocks and their replays; partial candidates receive no acceptance credit. This is a geometry experiment, not board release or proof of full-device rerouting readiness.

The first complete automatic campaign took 875.0 s: RF passed with three identical cold replays, but none of 16 UI candidates passed. The best clean UI candidates retained two open connections. Thus the combined milestone remains **failed**, not 474/474. A second bounded [order-diversity portfolio](../hardware/layout/h6-r2-474-seeded-portfolio.json) runs with `--plan hardware/layout/h6-r2-474-seeded-portfolio.json`: twelve deterministic SHA256-seeded net permutations, unchanged scope and rules. Exact expanded orders are saved and reused in cold replays; no model chooses the next order inside a run. This is another experiment, not a claimed solution.

The earlier serial wrapper for smaller manifests remains available:

From the repository root, with prepared KRT/Python runtimes from the [pinned profile](../hardware/layout/h6-r2-autorouter-profile.json):

```sh
python3 tools/route_board.py \
  --case hardware/layout/benchmarks/ui-inputs-service-id-82.json
```

The wrapper creates separate snapshots and tries the manifest's first established profile. Only if independent checks fail does it add the other 11 settings, select a complete passing candidate and replay it three times. Original-rule restoration, every-net checks, DRC/parity, copper preservation and ROI checks remain intact. It returns one JSON result; logs/candidates stay on disk. Exit code 0 means complete checked geometry with three identical replays, not production readiness. Partial progress appears as `best_partial_resolved`, never credited as `resolved`. Repeat operation needs one launch and reading its result, without model parameter decisions between attempts. This is a control contract, **not a measurement of total recurring token use**.

Two `--case` arguments run two manifests serially; overlapping nets on the same board are rejected. `--portfolio` tries eight search-order/direction/grid alternatives without relaxing clearances or copper sizes; `--sweep` explores the earlier twelve settings. `--max-seconds 1800` is a scheduling budget **per case**, not a hard total deadline: an active attempt has its own timeout. Source, checker, candidate and independent DRC hashes are verified; incomplete or stale evidence is rejected. Raw declared-net checking is mandatory: KiCad can normalize an incorrectly assigned track net when loading the board.

On macOS, each invocation starts `caffeinate -i -w <PID>`, verifies its own sleep assertion and releases it on completion, error or cancellation. Display sleep remains allowed; lid closure and explicit sleep are not blocked. Losing the caffeinate process stops the computation with an error. `sleep_prevention` reports its state; persistent power settings are unchanged. Verified with 24 wrapper tests and a separate real assertion creation/release cycle.

Among complete passing settings, minimize vias, then length, then time. Adaptive mode does not promise globally best geometry: it accepts a checked seed without searching alternatives. Nothing is applied to production PCBs. Changed sources require a newly reviewed manifest; stale hashes are intentionally rejected. Prepared engine/Python runtimes from the profile are required; a dependency installer is not yet included.

The failing-seed path was also tested: a manifest copy starts with `coarse_via75`. It failed; without intervention the controller added 11 alternatives, selected the only complete passing profile, and performed three identical replays—15 attempts in 304.9 s. This extension contains 34 attempts in total, including failures; negative results are not hidden.

The research controller `hardware/layout/h6_r2_autorouter_benchmark.py` retains the move experiment: `--profiles fine_via75 --repeats 3 --move R64 -0.5 0`, using the default small case. The strict wrapper does not yet accept changed placements. Supply engine/runtime locations through `--engine` and `--engine-python`.

Repeat usage measurement locally with `python3 hardware/layout/h6_r2_benchmark_usage.py --session <explicit-journal.jsonl> --since <UTC-time>`. It exports aggregates only; conversation text, journal paths and account identifiers are not copied into the public report. Cached input is separated from uncached input/output; counter resets are rejected.

## Next steps and readiness gate

The next target is several proposed interface/antenna layouts → constrained group placement → routing → mandatory checks → comparison of passing candidates only. This is **a plan, not a working automatic board designer**. Within a chosen variant, mechanical features and interfaces are fixed; critical RF/power islands, crystals and decoupling move only as constrained groups. Changing a radio path's board assignment or layer count requires a separate architecture variant, not unconstrained individual-component moves. Geometric success does not replace power, impedance, return-path, interference or prototype qualification; an unknown mandatory criterion blocks acceptance rather than counting as passed.

The owner considers 2 hours for a complete automatic cycle excellent and 8+ hours acceptable. On the M3 Pro (12 cores, 36 GiB), sampled attempts used approximately one core and 2.7–5.1 GiB RSS depending on grid size; these are snapshots, not guaranteed peaks. The research queue now separates six engine slots from one serial validation slot: waiting for validation does not delay the next calculation. An actual eight-job cold queue measured **6 engines, 589% CPU, 7.96 GiB RSS and zero swap**. This proves utilization, not routing success. The [scheduler](../hardware/layout/h6_r2_parallel_jobs.py) passes ten tests covering slot refill, serialized validation, errors and cancellation; callbacks own process timeouts and cleanup. The strict user-facing wrapper still runs cases serially; parallel integration remains experimental. Full-cycle timing for both boards and all net classes is unmeasured; small-region timings cannot be extrapolated linearly.

A separate [component-completeness gate](../hardware/layout/h6_r2_component_inventory.py) derives expectations from the independent H2 chain, never from a previous PCB: **1,210 schematic positions + 8 required mounting holes = 1,218 footprints**, UI 434 / RF 784. It checks the assigned board, reference, schematic UUID, footprint, MPN/value, instance identity and assembly flags; DNP or BOM exclusion does not authorize a missing footprint. Real-board checks and copy-only negative tests catch omissions, duplicates, equal-count swaps and incorrect board assignments. This is an additional API gate, not yet integrated into the older wrapper; it does not qualify geometry or electrical behavior.

1. Remove the model from recurring decisions: established profile → automatic fallback → checked replays → compact result. Implemented; next measure an isolated repeat with model usage, without concurrent development. Do not read detailed logs when all gates pass. Do not spend tokens micro-optimizing A* seconds.
2. Test other classes and both executors: KRT and [Freerouting 2.4.1](https://github.com/freerouting/freerouting/releases/tag/v2.4.1). Current automatic policy covers only 342 of 3,085 remaining connections. Ground/power account for 1,724; GPIO results cannot be extrapolated to them, RF or USB. No blanket removal of `manual_only`.
3. Prepare reusable critical islands with impedance, current, return-path and surrounding-region checks; test **full rebuilds** after placement, schematic, footprint and rule changes. Incremental repair of old copper is not the target workflow. Explicitly measure manual residuals and requalification.
4. Resume production routing only after demonstrating a process for both boards and every class, with no unknown manual-repair workload or untested cheap high-impact acceleration option. Electrical/mechanical gates remain mandatory. Plugin, local LLM and new-engine work wait for measured necessity and payback.
