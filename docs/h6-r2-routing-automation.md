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
