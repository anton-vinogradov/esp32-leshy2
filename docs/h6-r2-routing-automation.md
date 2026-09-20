# H6 · Routing benchmark

[Home](../README.md) · [Current PCBs](h6-r2-current-routing.md) · [Русский](h6-r2-routing-automation.ru.md)

**2026-09-20: the default command passed UI 252 + RF 222 = 474/474 connections in 225.129 s**, including an initial route and three identical cold replays per block. Native DRC, schematic parity and region-boundary findings were zero; all 1,218 footprints, source files and unselected copper were preserved. No model decisions occurred inside the command. [Measured evidence](../hardware/layout/benchmarks/2026-09-20-474-one-command-results.json).

This accepts the geometry of two selected blocks. Each starts with zero selected-net copper; the original copper outside that scope remains as context. It does **not** qualify complete boards, electrical behavior, EMI, RF performance, ESD topology or production readiness. Production routing remains paused; H6 is open and the firmware boundary is unchanged.

## Run it

From the repository root:

```sh
python3 tools/route_474.py
```

The [default repeat portfolio](../hardware/layout/h6-r2-474-repeat-portfolio.json) runs the two selected profiles, then six fresh cold replays. This prepared-runtime, one-command workflow passed all eight attempts and the final evidence-hash gate.

Prepared KRT/Python and native KiCad runtimes are required; a portable dependency installer is **not included**. Runtime locations can be overridden with `--engine-root` and `--engine-python`. The pinned KRT revision and combined NPTH/pending-pad patch are documented in the [engine patch instructions](../hardware/layout/engine-patches/README.md); the combined patch replaces the earlier NPTH-only patch. The UI winner uses bus ordering, a 0.05-mm grid, via cost 75, heuristic weight 1.3, `endpoint_reservations_all`, `dense_first` and `pending_pad_protection`; RF uses `rf-target5`. Exact settings are in the portfolio.

Before routing, the command checks both original copies with native KiCad. Every candidate receives independent geometry, all-net and component-inventory checks. Before accepting the result, it rechecks input pins and five saved proof hashes for each initial result and replay. Only `status=pass`, `resolved=474` and exit 0 accept both blocks; partial results receive no acceptance credit. Output is compact JSON with a summary path; detailed evidence stays in `work/`. On macOS, a checked `caffeinate` assertion prevents idle sleep during the run and is released on exit; closing the lid or explicit sleep can still suspend the laptop.

The earlier serial wrapper remains available for smaller manifests, using the [prepared runtime profile](../hardware/layout/h6-r2-autorouter-profile.json):

```sh
python3 tools/route_board.py \
  --case hardware/layout/benchmarks/ui-inputs-service-id-82.json
```

It tries the established profile, adds alternatives on failure and requires three identical replays. Changed sources need a newly reviewed manifest; stale hashes are rejected. Neither wrapper applies experimental copper to production PCBs.

## Design acceptance before the next rebuild

```sh
python3 tools/check_design.py
```

This read-only entrypoint reuses the existing auditors: eleven implemented scoped checks and six mandatory, explicitly unqualified coverage domains. Earlier four-native-worker runs took **27–43 s**, with eight total worker slots on this 12-logical-core laptop ([benchmark record](../hardware/layout/benchmarks/2026-09-20-design-acceptance-results.json)); `--jobs` and `--native-jobs` override the limits. It verifies `caffeinate`, guards source membership/content and evidence hashes, and stops owned process groups on cancellation or timeout. It does not generate circuits, edit boards or approve manufacture. Prepared native KiCad Python is required (`--kicad-python` overrides its path).

The latest completed run took **25.839 s**: four scoped passes, two failures and eleven unqualified results. The current boards correctly receive **`not_accepted`**, not a success badge. Power prerequisites fail; native connectivity reports **UI 1,226 + RF 1,859 = 3,085** remaining connections, independent of the truncated DRC item lists. Complete pin/state models, routed electrical behavior, assembled geometry, manufacturing parity and prototype measurements remain mandatory. Typed ERC evidence is hash-validated, not rerun by this command. Missing, stale or incomplete evidence cannot become PASS.

The new `electrical.power_domain_crossings` check scans both boards for potential live-rail/direct-drive/pullup paths into unpowered inputs, using reviewed pin types and the existing H3 commanded AON-only state. It already exposes a concrete missing proof: C5 U14 GPIO23/pad21 and GPIO24/pad23 directly share `EV_N1_C5`/`EV_N7_IR` with AON pullups R88/R124 while C5 is MAIN-powered. A fresh native schematic export and PCB read confirm the connections. The [C5 module datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf), v1.3 pp.32–33, specifies its DC table at 3.3 V/25°C; it does not justify substituting VDD=0 into the operating input-level formula as a powered-off absolute limit. These paths remain **unqualified**, not proven damage. Configurable outputs, unknown supply ownership and unmodeled loading are explicit; no schematic changes or MPN adoption occur. Ready EDG static digital checks were inspected, but they do not infer these native powered-off states or missing exact-pin evidence; the added adapter reuses the existing state and acceptance machinery, not a new electrical solver.

Exit codes: **0** = every declared check passes its scope; **1** = design not accepted; **2** = execution/evidence error; **130** = cancellation. Completed runs save scopes, findings, hashes and timing in a unique `work/design-check-*/result.json`; bootstrap failures and cancellation report `report: null`, never an older result. Do not confuse an expected exit 1 on this unfinished design with a failed software regression test. Negative tests include a declared 5-V rail against its fitted 3.222-V divider, omitted components, stale proof, invalid protocol, incomplete coverage, capped DRC, cancellation and orphaned processes.

Development proceeds as **mechanism → current project → independent validation**. The [MAIN variant command](../tools/compare_main_feedback.py), `python tools/compare_main_feedback.py` in the prepared EDG 0.5.2 environment, now compares [seven explicit hypotheses](../hardware/verification/h6-main-feedback-variants.json). Ready EDG chooses **both** preferred resistor nominals; separate exact voltage/impedance corners and all 58 load cases check each candidate. Load and voltage demands cannot be overridden by a variant. H3 evidence is regenerated in memory, source changes are rejected, and a fresh `work/feedback-variants-*/result.json` is saved. The command establishes/releases its own `caffeinate`; exit 1 means **not qualified**, 2 an execution/evidence error, 130 cancellation. No PCB or MPN changes.

Current requirements remain infeasible even if only the resistors, or only the voltage reference, become ideal. Lower-loss hypotheses can fit: the explicit 20-mΩ eFuse / 30-mV distribution target gives 44.2k/10.2k and about 8.50 mV conditional lower margin. This is **not a qualified replacement cell**: actual VIN, leakage, lifetime, ripple, hot RON/current, dynamics, monitoring and physical behavior remain open. [Evidence, repeat runs and preparation-cost scope](../hardware/layout/benchmarks/2026-09-20-feedback-variants-results.json).

The same command now checks [reviewed RON source conditions](../hardware/verification/h6-main-ron-sources.json) against every load case. The fitted TPS25974 maximum is specified at 3 A / 25°C; candidate TPS259814 covers the screening temperature range, but its maximum is also specified at 3 A, not our 4.25-A target. These are evidence gaps, not proof that either part fails physically. Typical values, missing axes, changed source records and wrong fitted identities cannot become acceptance. Other table-header conditions remain unmodeled; numeric coverage never qualifies a cell. **113 tests pass**, including 22 new negative/regression tests; two fresh commands agree in 0.251–0.271 s, without LLM calls. Source pages were visually checked; repeating the command uses pinned transcriptions, not a live PDF audit. Next: qualify a complete candidate cell, including protection/monitoring and exact-part supply, before schematic replacement.

Before new research, check existing tools and reusable work first. The current implementation keeps ready [EDG](https://github.com/BerkeleyHCI/PolymorphicBlocks) for resistor selection and reuses our existing interval/native-source checks. The bounded check of [atopile](https://github.com/atopile/atopile) and related tools found no verified drop-in model for these exact source rows; only the missing RON applicability adapter was added. No new solver or migration was justified by this task.

The ready [TI TPS25981 calculator](https://www.ti.com/tool/download/SLVRBL3), version 01.00.00.0A (2022), was also inspected rather than reimplemented. It remains a design reference, not an admitted automatic checker: its current-limit equations use 6595 instead of the 6585 in our reviewed datasheet, its tolerance formula uses root-sum-square rather than worst-case limits, and its loss calculation uses typical RON. Our available spreadsheet engine did not reproduce the original cached R2 selection. Macros were not run, the original workbook was not changed, and native Excel recalculation was not claimed. These findings do not prove that every intended native Excel calculation is broken; they prevent treating this unverified path as acceptance.

## Rebuild the existing indicator network

```sh
python3 tools/rebuild_indicators.py
```

This bounded next step uses the prepared EDG 0.5.2 compiler to regenerate a netlist, BOM and compiled model for the **ten UI indicator branches (20 components)** in fresh `work/indicator-rebuild-*` directories. It preserves the fitted 2.2-kΩ nominal/tolerance and LED polarity; it does not select a new brightness target or redesign the external drivers. Nine transmit indicators share AON power; FAULT has a separate source and ground return. The command compares all 40 pads and 22 canonical nets with reviewed source records and an independent native KiCad read, then requires two fresh-process replays. It checks its own `caffeinate` assertion and cleans up owned workers. Prepared EDG, Java and KiCad runtimes are required; CLI overrides are available and no dependencies are downloaded.

The generated resistor is generic; the fitted exact MPN remains a checked source reference, **not a newly selected or supply-approved BOM part**. Shared pullups, hysteresis, both VOICE drivers and other external loads are listed but not generated or electrically qualified. Exit **1** means reconstruction checks passed but hardware remains **not qualified**; **2** means execution/evidence error and **130** cancellation. No production schematic, placement, copper or hardware/firmware boundary is changed. The next useful extension is a source-qualified complete driver/load recipe, not an approval inferred from matching topology.

Two independently invoked commands agree in **2.656–2.694 s**, each including two cold workers. **127 tests pass**, including 24 new focused tests; independent mutations of actual exported part/value/return names are rejected. No LLM calls occur inside the command. [Evidence and preparation-cost scope](../hardware/layout/benchmarks/2026-09-20-indicator-rebuild-results.json); parent-token savings and payback remain unmeasured.

## Local helper pilot

The first blind Qwen3.8-27B 4-bit MLX run, **with thinking disabled**, finished in 16.2 minutes without intervention between cases. **9/10 proposed rules** passed their hidden counterexamples (46/47 individual probes), but **only 2/10 complete answers** passed: arithmetic, verdicts and evidence provenance failed. One valid control was falsely rejected; one rule missed a changed required voltage. The predeclared eligibility bar was **not met**, and no new production checks were adopted. Parent-token savings remain unmeasured; this evaluates one configuration, not every possible Qwen mode. [Measurements, partial cost proxy and hashes](../hardware/layout/benchmarks/2026-09-20-local-qwen-pilot-results.json). Weights and the experimental environment remain local; design acceptance remains deterministic.

Follow-up: a bounded public-feedback repair harness passes 15 tests, but its first long expression response timed out; no repaired result was obtained. A separate short pin-review experiment completed all six requests: **3/3 correct without a skill and 3/3 with it**, with 1890 additional local input tokens for the skill. No quality lift or parent-token saving is demonstrated on these three controlled fixtures. The recipe remains experimental, not a production checker. [Results, limitations and preparation-cost proxy](../hardware/layout/benchmarks/2026-09-20-local-qwen-skills-results.json).

Refine narrow recipes when development exposes an actual failure; retain them only after improvement on separate held-out cases or measured reviewer effort. Reusing a disclosed case is a regression check, not new blind evidence. Deterministic checks remain independent of LM Studio.

## Preparation cost and unsuccessful attempts

The primary cost metric remains **model tokens per complete checked result**. Root-task journal snapshots recorded about **157k**, **909,031** and, during the resumed work, **199,005 uncached-input + output tokens**. These are preparation/development proxies, not billing or isolated repeat-routing costs. The second interval includes price/documentation work; the latest includes development, review, documentation and monitoring. Agent coverage is unverified and later work is excluded. Zero model decisions inside the command does not erase preparation cost. Total recurring usage, savings against the previous method and payback remain unmeasured.

| Earlier experiment | Result |
|---|---|
| Small blocks, 28 / 60 / 82 connections | Passed with three matching replays; an R64 move rebuilt the selected block. Two other moves failed baseline collision checks. |
| Eight stock / eight NPTH-patched cold candidates | No complete pass; 330.6 / 269.5 s. The patch removed observed hole-clearance defects, but opens and dangling vias remained. |
| RF-only replay series / UI rip-up pilot | RF 222 passed; both UI candidates left seven opens. Eight initial RF native checks aborted in the restricted environment; the same candidates later passed outside it without rerouting. |
| Original automatic portfolio | Failed in 875.0 s: RF passed its replays; all 16 UI candidates failed, best clean result two opens. |
| Twelve seeded UI orders / ten endpoint variants | Failed in 321.002 / 594.815 s; each left at least one UI connection open. |
| First successful combined campaign | 474/474 with three cold replays per block in 299.98 s, before the final default-command verification above. |

Setup failures and rejected candidates remain in the evidence. Earlier records: [small blocks](../hardware/layout/benchmarks/2026-09-16-results.json), [larger block and usage](../hardware/layout/benchmarks/2026-09-16-larger-results.json), [stock queue](../hardware/layout/benchmarks/2026-09-16-parallel-474-results.json), [NPTH patch queue](../hardware/layout/benchmarks/2026-09-16-patched-474-results.json), [RF replays and usage](../hardware/layout/benchmarks/2026-09-16-rf-222-replay-results.json), [UI pilot](../hardware/layout/benchmarks/2026-09-16-ui-rip-pilot-results.json). The [latest campaign record](../hardware/layout/benchmarks/2026-09-20-474-one-command-results.json) covers the subsequent failed portfolios and successful block result.

## Remaining gate

The owner-confirmed target is a **cold rebuild of both complete boards** from the schematic, chosen placement and verified constraints/recipes on every invocation, with every mandatory check automated. Previous-build tracks must not become routing inputs; critical islands must be regenerated. The 474-connection result does not yet demonstrate that workflow.

Next: measure isolated recurring model usage; test every net class and both KRT and Freerouting; qualify reusable RF/power/crystal/decoupling groups with impedance, current, returns and surrounding-region checks; then test full rebuilds after placement, schematic, footprint and rule changes. The production policy still covers only 342 of 3,085 remaining connections, including 1,724 ground/power connections outside that policy; experimental scope does not remove `manual_only` restrictions.

Comparing proposed interface/antenna layouts through constrained group placement, routing and mandatory checks remains a plan. Board assignment and layer-count changes require separate architecture variants. Complete-cycle timing is unmeasured; the owner's target remains 2 hours as excellent and 8+ hours as acceptable. Resume production only after both boards and every class have a demonstrated process, known manual residuals and electrical/mechanical qualification. Unknown mandatory criteria block acceptance; plugin, local-LLM and new-engine work still require measured necessity and payback.
