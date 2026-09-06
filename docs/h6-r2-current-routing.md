# H6.0.3-R1 · Current 80-mm routing

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)

**Status:** ▶️ checked progress snapshot, not H6 closure. The two live PCBs contain 5,453 copper items; native KiCad connectivity reports 2,541 remaining and 724 already resolved physical connections.

| Board | Traces | Vias | Resolved | Remaining | DRC |
| --- | ---: | ---: | ---: | ---: | --- |
| UI | 1,132 | 222 | 227 | 1,000 | 0 |
| RF/power | 3,320 | 779 | 497 | 1,541 | 0 |

## What changed in this snapshot

After the 75 → 80 mm transition, conflict-free analogue/audio/sense routing was transferred by exact pad anchors. Old branches that conflicted with the new geometry were discarded rather than forced into the board; the remaining eight UI connections were then rerouted in the live geometry and passed DRC. On RF/power, the U17 and U100 eFuse neighbourhoods were locally opened, five missing analogue connections were added, and the displaced safety/control copper was fully rerouted before acceptance. In the audio cluster, `CODEC_DACVREF` and both ADC inputs are now connected; the neighbouring headphone and `CODEC_TX_AC` routes were fully rerouted while preserving their original connectivity. For `AUDIO_CAPTURE_MIC_SEL`, the low-speed R53 pull-down was moved out of the U106 escape corridor, then both adjacent U106 nets received independent paths without a new DRC finding. The same cluster now closes `CAPTURE_MIC_BIASED`, while one continuous route joins the three previously separate `CC_BAND_V1_REQ` groups. A complete four-via `RX_VOICE_AFOUT_AC` path now also joins the vertically separated audio clusters without an acute branch. In the battery-safety cluster, `PACK_PCKP_SENSE` is now complete: one redundant `PACK_DIS_GATE` via was removed, its remote branch was moved to the inner layers, and the neighbouring `PACK_FET_OVERRIDE_N` via moved by 0.08 mm; all three nets retain connectivity and pass DRC. `ANALOG_AUDIO_SENSE` now has 11 physical connections left: 0 on UI and 11 on RF/power.

Native KiCad DRC reports zero findings on both boards. The former physical `BT1`/`J12` conflict was removed by shifting the unrouted SMT holder 3.00 mm; no DRC exception remains.

## Board-size decision

The 80 × 150-mm outline is retained for now. The highest sum of non-overlapping same-face courtyards is 61.474% (RF/power inner face); all footprints place, both boards have clean DRC and 724 connections are already routed. Expanding now would discard useful evidence without a demonstrated blockage. If a required power, USB/i8080, clocked-digital or RF route cannot pass after legal local rearrangement, the controlled next candidate is 85 × 150 mm followed by complete H1/H6 and both-suite requalification.

## Live images

These are direct exports from the live `.kicad_pcb` files; each SVG embeds its board hash.

**Front/UI board**

[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)

**Rear RF/power board**

[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)

## What is not proven yet

The available area and 5-mm corridor are sufficient for the accepted copper so far, but final margin cannot be claimed before power, USB/i8080/clocked buses, RF and reference planes are complete. H6.0.3 closes only with no unexplained connectivity residual.
