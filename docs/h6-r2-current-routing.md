# H6.0.3-R1 · Current 80-mm routing

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)

**Status:** ▶️ corrected placement accepted; routing restarted; H6 is not closed.

| Board | Traces | Vias | Resolved | Remaining | DRC |
| --- | ---: | ---: | ---: | ---: | --- |
| UI | 100 | 5 | 31 | 1,196 | 0 |
| RF/power | 607 | 165 | 183 | 1,855 | 0 |

## What we want

Produce electrically valid 80 × 150-mm PCBs: local high-frequency loops stay at their owning devices, then every copper connection is routed and checked without a DRC exception.

## What we decided

The former collision-free seed was electrically invalid because some bypass, feedback and bootstrap parts were tens of millimetres from their owners. The old routes remain available only in Git; the live PCBs were cleared and rebuilt. The 80 × 150-mm outline remains because the corrected placement fits; 85 × 150 mm is considered only after a demonstrated routing blockage.

## What we obtained

All 1,208 bodies are placed; all 310 local-part → owner pairs meet their limits; 22 actual pad-centre pairs cover every switching-node net and selected local bypasses with zero violations. All five oscillator cells — two RP2354s, CC1101, Si5351A and Si4732 — are routed and DRC-clean. 36 manual controlled-RF routes close 42 connections: in addition to the local CC1101 and Airband networks plus the AM/LW input boundary, the complete S3, C5 and all three nRF24 paths from U.FL to external SMA and their detector branches are routed. 30 routes remain via-free; 6 reviewed 0.50/0.25-mm B.Cu-to-F.Cu transitions are necessary only because the edge-launch SMA centre land is on F.Cu. Their ground-return pairs are deferred until the continuous plane fill so this checkpoint does not create floating copper islands. Both boards have zero native DRC findings. The deliberate restart leaves 3,051 physical connections, summarized in the table above.

## What happens next

Order: four DC/DC islands and power protection → RF/clock clusters → USB and direct i8080 → remaining digital/control copper → planes and return paths → full DRC and release checks.

## Live images

These are direct exports from the current `.kicad_pcb` files; each SVG embeds its board hash.

**Front/UI board**

[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)

**Rear RF/power board**

[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)

## Completion criterion

H6.0.3 closes when connectivity reaches zero, every mandatory class and return path is routed, and native DRC is rerun clean on both boards.
