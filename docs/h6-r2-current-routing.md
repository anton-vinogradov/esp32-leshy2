# H6.0.3-R1 · Current 80-mm routing

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)

**Status:** ▶️ corrected placement accepted; routing restarted; H6 is not closed.

| Board | Traces | Vias | Resolved | Remaining | DRC |
| --- | ---: | ---: | ---: | ---: | --- |
| UI | 4 | 0 | 1 | 1,226 | 0 |
| RF/power | 449 | 139 | 132 | 1,906 | 0 |

## What we want

Produce electrically valid 80 × 150-mm PCBs: local high-frequency loops stay at their owning devices, then every copper connection is routed and checked without a DRC exception.

## What we decided

The former collision-free seed was electrically invalid because some bypass, feedback and bootstrap parts were tens of millimetres from their owners. The old routes remain available only in Git; the live PCBs were cleared and rebuilt. The 80 × 150-mm outline remains because the corrected placement fits; 85 × 150 mm is considered only after a demonstrated routing blockage.

## What we obtained

All 1,208 bodies are placed; all 310 local-part → owner pairs meet their limits; 22 actual pad-centre pairs cover every switching-node net and selected local bypasses with zero violations. Both boards have zero native DRC findings. The deliberate restart leaves 3,132 physical connections, summarized in the table above.

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
