# H6.0.3-R1 · Current 80-mm routing

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)

**Status:** ▶️ checked progress snapshot, not H6 closure. The two live PCBs contain 5,290 copper items; native KiCad connectivity reports 2,555 remaining and 710 already resolved physical connections.

| Board | Traces | Vias | Resolved | Remaining | DRC |
| --- | ---: | ---: | ---: | ---: | --- |
| UI | 1,132 | 222 | 227 | 1,000 | 0 |
| RF/power | 3,204 | 732 | 483 | 1,555 | 2 assigned BT1/J12 |

## What changed in this snapshot

After the 75 → 80 mm transition, conflict-free analogue/audio/sense routing was transferred by exact pad anchors. Old branches that conflicted with the new geometry were discarded rather than forced into the board; the remaining eight UI connections were then rerouted in the live geometry and passed DRC. `ANALOG_AUDIO_SENSE` now has 25 physical connections left: 0 on UI and 25 on RF/power.

Native KiCad DRC reports zero UI findings. RF/power retains only the two already assigned findings at the single `BT1`/`J12` location: hole clearance and a front-mask aperture bridge. The new routing adds no violation.

## Live images

These are direct exports from the live `.kicad_pcb` files; each SVG embeds its board hash.

**Front/UI board**

[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)

**Rear RF/power board**

[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)

## What is not proven yet

The available area and 5-mm corridor are sufficient for the accepted copper so far, but final margin cannot be claimed before power, USB/i8080/clocked buses, RF and reference planes are complete. H6.0.3 closes only with no unexplained connectivity residual.
