# H6.0.3-R1 · Current 80-mm routing

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)

**Status:** ▶️ routing and physical-interface corrections continue; H6 is not closed. The [native PCB review](h6-r2-interface-review.md) found orientation, mating and required-hole defects; clean DRC does not establish assembly readiness.

| Board | Traces | Vias | Resolved | Remaining | DRC |
| --- | ---: | ---: | ---: | ---: | --- |
| UI | 21 | 0 | 8 | 1,221 | 0 |
| RF/power | 601 | 165 | 180 | 1,859 | 0 |

## What we want

Produce electrically valid 80 × 150-mm PCBs: local high-frequency loops stay at their owning devices, then every copper connection is routed and checked without a DRC exception.

## What we decided

The former collision-free seed was electrically invalid because some bypass, feedback and bootstrap parts were tens of millimetres from their owners. The old routes remain available only in Git; the live PCBs were cleared and rebuilt. The 80 × 150-mm outline remains because the corrected placement fits; 85 × 150 mm is considered only after a demonstrated routing blockage.

## What we obtained

All 1,208 bodies are placed; all 311 local-part → owner pairs meet their limits; 36 actual pad-centre pairs cover every switching-node net and selected local bypasses with zero violations. All ten edge-launch SMA bodies face outward; their F.Cu and B.Cu solder lands remain inside the PCB outline, and the corrected placement is frozen again. The PCB-thickness and SMA-slot tolerance fit remains an open item in the [mechanical stack](h6-r2-mechanical-stack.md). The historical S3/C5 power aliases are corrected: both domains now use `3V3_MAIN`; ten bypass parts were returned to their owners and the LNA choke locality was corrected. These electrical-realization and placement fixes do not change product functionality. All five oscillator cells — two RP2354s, CC1101, Si5351A and Si4732 — remain routed and DRC-clean; the RF-package correction did not change them.

Primary-drawing review found TTM top/bottom-view numbering errors, CP0603 port-orientation errors and incorrect WBC lands. After correcting the footprints, 23 affected RF routes were withdrawn from the current routing: they no longer count as complete, and their former copper remains available in Git. The exact list and reason are recorded in the [manual-copper contract](../hardware/layout/h6-r2-manual-copper.json). The current audit contains 106 active manual routes across all classes; the withdrawn routes are already excluded from these counts and the connectivity table. The remaining 13 controlled-RF routes close 16 connections; 12 are via-free and 1 use vias. The S3, C5, three nRF24, CC1101 and Airband paths are not claimed to be fully routed: the affected RF interconnects and detector branches must be rerouted to the corrected pads. RF launches, continuous planes and return paths still require completion and verification. Both boards have zero native DRC findings. The deliberate restart leaves 3,080 physical connections, summarized in the table above.

## Current ERC limitation

The current library assigns `passive` to every connectable symbol pin. Zero ERC findings therefore do not confirm that every power input has a source or that outputs cannot conflict. Production release requires a reviewed electrical-type map for the physical pins, rail-source and output-conflict checks, followed by fresh ERC on both schematics.

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
