# H6.0.3-R1 · Current 80-mm routing

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)

**Status:** ▶️ routing and physical-interface corrections continue; H6 is not closed. The [native PCB review](h6-r2-interface-review.md) found orientation, mating and required-hole defects; clean DRC does not establish assembly readiness.

| Board | Traces | Vias | Resolved | Remaining | DRC |
| --- | ---: | ---: | ---: | ---: | --- |
| UI | 82 | 10 | 17 | 1,212 | 0 |
| RF/power | 600 | 165 | 180 | 1,859 | 0 |

## What we want

Produce electrically valid 80 × 150-mm PCBs: local high-frequency loops stay at their owning devices, then every copper connection is routed and checked without a DRC exception.

## What we decided

The former collision-free seed was electrically invalid because some bypass, feedback and bootstrap parts were tens of millimetres from their owners. The old routes remain available only in Git; the live PCBs were cleared and rebuilt. The 80 × 150-mm outline remains because the corrected placement fits; 85 × 150 mm is considered only after a demonstrated routing blockage.

## What we obtained

All 1,208 bodies are placed; all 311 local-part → owner pairs meet their limits; 54 actual pad-centre pairs cover every switching-node net and selected local bypasses with zero violations. All ten edge-launch SMA bodies face outward; their F.Cu and B.Cu solder lands remain inside the PCB outline, and the corrected placement is frozen again. The PCB-thickness and SMA-slot tolerance fit remains an open item in the [mechanical stack](h6-r2-mechanical-stack.md). The historical S3/C5 power aliases are corrected: both domains now use `3V3_MAIN`; ten bypass parts were returned to their owners and the LNA choke locality was corrected. These electrical-realization and placement fixes do not change product functionality. All five oscillator cells — two RP2354s, CC1101, Si5351A and Si4732 — remain routed and DRC-clean; the RF-package correction did not change them.

Primary-drawing review found TTM top/bottom-view numbering errors, CP0603 port-orientation errors and incorrect WBC lands. After correcting the footprints, 23 affected RF routes were withdrawn from the current routing: they no longer count as complete, and their former copper remains available in Git. The exact list and reason are recorded in the [manual-copper contract](../hardware/layout/h6-r2-manual-copper.json). The current audit contains 115 active manual routes across all classes; the withdrawn routes are already excluded from these counts and the connectivity table. The remaining 13 controlled-RF routes close 16 connections; 12 are via-free and 1 use vias. The S3, C5, three nRF24, CC1101 and Airband paths are not claimed to be fully routed: the affected RF interconnects and detector branches must be rerouted to the corrected pads. RF launches, continuous planes and return paths still require completion and verification. Both boards have zero native DRC findings. The deliberate restart leaves 3,071 physical connections, summarized in the table above.

Hand-reviewed UI `GENERAL_CONTROL` proposals cover 9 nets: `C5_TX_LED_A`, `CC_TX_LED_A`, `EXT_TX_LED_A`, `IR_TX_LED_A`, `NRF0_TX_LED_A`, `NRF1_TX_LED_A`, `NRF2_TX_LED_A`, `S3_TX_LED_A`, `VOICE_TX_LED_A`. Together they contain 61 traces of 0.15 mm and 10 through vias of 0.4/0.2 mm. Their vias are outside bodies on both faces; existing copper and every placement are retained. `FAULT_LED_A` is excluded: it belongs to `SAFETY_CONTROL`. The finite net allowlist, geometry hashes, connectivity and native DRC are checked separately: permission to use a routing helper does not automatically admit its result.

## Current ERC limitation

The production library still uses `passive` for connectable pins; its zero ERC result does not establish supply availability or compatible outputs. Reviewed types are applied only to isolated schematic copies: original and typed XML reference/pin-to-net membership must remain identical, without topology changes. The current [typed ERC](h6-r2-electrical-semantics.md) retains 24 findings: 22 `power_pin_not_driven`, one ACDRV1/ACDRV2 output conflict and one `pin_not_driven` on SA818S H/L. The [source-path triage](../hardware/verification/h6-electrical-source-triage.json) remains `triaged_not_cleared`: source/configuration explanations do not suppress ERC, add unconditional power sources or qualify rail and startup behavior. The electrical gate remains `review_required`; reviewed types have not been promoted to the production library and manufacturing is not authorized.

The first [electrical-review pass](h6-r2-electrical-semantics.md) corrected three device pin maps and restored both RP2354 internal-flash supplies. Their bypasses moved beside pad 69. Partial ERC has run on copies with reviewed pin types; this does not close the whole electrical review.

## What happens next

Continue `H6-NATIVE-ELECTRICAL-SEMANTICS`: remaining physical-pin types, rail sources, output conflicts and fresh ERC. Then four DC/DC islands and power protection → RF/clock clusters → USB and direct i8080 → remaining digital/control copper → planes and return paths → full DRC and release checks.

## Live images

These are direct exports from the current `.kicad_pcb` files; each SVG embeds its board hash.

**Front/UI board**

[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)

**Rear RF/power board**

[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)

## Completion criterion

H6.0.3 closes when `H6-NATIVE-ELECTRICAL-SEMANTICS` passes, connectivity reaches zero, every mandatory class and return path is routed, and native DRC is rerun clean on both boards.
