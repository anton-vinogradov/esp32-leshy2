# Leshy2 hardware roadmap

[Home](../README.md) · [Stage reports](stage-results.md) · [Русский](roadmap.ru.md)

<!-- current-substep: H6.0.3-R1 -->

**Current hardware boundary: `H6.0.3-R1`.**

This page owns only work order and transition criteria. Product decisions live
on the [landing page](../README.md), subject detail lives in focused documents,
and completed results live in the [report index](stage-results.md).

## Sequence

| Stage | Status | Exit criterion | Report |
|---|---|---|---|
| H0 · Requirements and architecture | ✅ Reviewed · R2 | functions, owners and safety boundary are coherent | [H0-R2](h0-r2-functional-architecture.md) |
| H1 · Physical design | Reviewed concept · `H1-R2.39`; native correspondence reopened | 223 concept bodies and four views; exact native mounting and assembled fit remain [open](h6-r2-interface-review.md) | [H1-R2](h1-r2-acceptance.md) |
| H2 · Production ECAD | ✅ Reviewed · `H2-R2.1.5` | two native schematics, pin/net parity and ERC pass | [H2-R2](h2-acceptance.md) |
| H3 · Virtual electrical verification | Reviewed analytical baseline · `H3-R2.7`; current native power [reopened in H6](h6-r2-electrical-semantics.md#native-power-prerequisites--reopened) | every pre-layout calculable corner passes against the fitted circuit and physical residuals are owned; retained calculations do not yet qualify current power | [H3-R2](h3-r2-acceptance.md) |
| H4 · Joined pre-layout gate | ✅ Reviewed · `H4-R2.3` | hardware and firmware boundaries reconcile | [H4-R2](h4-r2-acceptance.md) |
| H5 · Components and procurement routes | ✅ Reviewed · `H5-R2.1` | every group has a controlled route; order-time recheck remains mandatory | [H5-R2](h5-r2-current-route.md) |
| **H6 · Placement, routing and release candidate** | **▶ Current · `H6.0.3-R1`** | all copper, repeated electrical/mechanical checks and production outputs pass | [Current checkpoint](h6-r2-current-routing.md) |
| H7 · Build one device | ⏳ Waiting | two PCBAs and the parts for one prototype are received | — |
| H8 · Bring-up and physical verification | ⏳ Waiting | safe boot, programming and physical evidence pass | — |
| H9 · Manufacturing release | ⏳ Waiting | first-unit corrections become a reproducible release | — |

## Current H6

| Substage | Status | Exit |
|---|---|---|
| H6.0.1-R1 · Placement and mechanical stack | Historical 2D placement; [native interface/assembly findings reopened](h6-r2-interface-review.md) | 1,208/1,208 footprints; physical mating, openings and assembled access also require verification |
| H6.0.2-R1 · Routing policy | ✅ historical geometry | classes and native KiCad rules are frozen |
| **H6.0.3-R1 · 80-mm routing and parity** | **▶ Current** | [H6-NATIVE-ELECTRICAL-SEMANTICS](h6-r2-electrical-semantics.md) passes; every net is routed or explicitly NC; DRC and parity are zero |
| H6.0.4-R1 · Routed power and thermal | ⏳ | actual copper/via/rail margins pass |
| H6.0.5-R1 · Digital, USB and M1 SI | ⏳ | i8080‑8, USB and buses pass |
| H6.0.6-R1 · RF and Airband | ⏳ | ten paths, matching, isolation and parasitics pass |
| H6.0.7-R1 · STEP, enclosure and cables | ⏳ | assembled geometry and tolerances pass |
| H6.0.8-R1 · Production and bring-up outputs | ⏳ | Gerber/BOM/CPL/drawings/firmware are ready |
| H6.0.9-R1 · Independent DFM/CPL review | ⏳ | release candidate has no open blocker |

## Transition rules

- The 80 × 150-mm outline remains while the [machine size gate](../hardware/layout/generated/H6-R2-current-routing-audit.json) passes. If it triggers, 85 × 150 mm is evaluated and all H1/H6, ERC/DRC, electrical and firmware checks repeat.
- Work belonging to a later stage cannot be moved backwards and presented as closed evidence.
- The factory only fabricates and populates the two PCBAs; the owner performs solder-free final assembly and first power-on.
- Every MPN is rechecked against the live JLCPCB Standard PCBA surface before ordering.
- H7 starts only after the joined hardware/firmware pre-order gate and explicit approval of the actual one-device quote.

Machine sources: [hardware roadmap state](../hardware/verification/hardware-roadmap-state.json) · [H6 release plan](../hardware/verification/h6-layout-release-plan.json) · [pre-order contract](../hardware/verification/preorder-verification-contract.json).
