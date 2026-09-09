# Components of both boards · four faces

[Home](../README.md) · [Review findings](h6-r2-interface-review.md) · [Русский](h6-r2-component-views.ru.md)

Direct views of the current KiCad PCBs, **at the same scale**, without tracks
or unrouted connection lines. Click a view to open the full SVG and zoom into
small components without losing detail.

The microphone correction below is included in these refreshed, hash-bound
views, with fresh native intent/label checks and visual review.

| Front/UI board | Rear/RF board |
| --- | --- |
| **Outer F — 30 items + 4 mounting footprints** | **Outer F — 12 items + 4 mounting footprints** |
| [![UI outer](images/h6-r2-components-ui-outer.svg)](images/h6-r2-components-ui-outer.svg) | [![RF outer](images/h6-r2-components-rf-outer.svg)](images/h6-r2-components-rf-outer.svg) |
| **Inner B — 398 items** | **Inner B — 768 items** |
| [![UI inner](images/h6-r2-components-ui-inner.svg)](images/h6-r2-components-ui-inner.svg) | [![RF inner](images/h6-r2-components-rf-inner.svg)](images/h6-r2-components-rf-inner.svg) |

[All four views on one sheet](images/h6-r2-components-overview.svg).

[Interface-label meanings and coverage](h6-r2-interface-silkscreen.md): user,
service and assembly labels are checked separately from Fab/reference graphics.

## How to read

- Grey: current Fab body outlines and component references. References added
  for inspection **are not new production silkscreen**.
- Blue: actual silkscreen on the selected PCB face.
  Antenna labels sit closer to the connectors, with a single lawful-use
  sentence below: English on UI, Russian on RF.
- Ochre: drilled holes and the dashed L32 NFC reservation. **The loop is not routed yet**.
- Gold fill: **all 50 actual SMA copper solder lands** — three
  on F and two on B per connector, read directly from the native PCB. Small
  labels identify connector and pad. They are drawing annotations, not new
  silkscreen; gold denotes neither deposited solder nor paste/mask openings.
  B-side lands remain visible even though the SMA footprint body belongs to F.
  The same colour also shows **37 physical through-hole interface lands**
  (16 USB shell, 14 Cap, 7 encoder) on both faces, plus the **two L32 NFC
  endpoints**, which are not component leads or a routed antenna. Real drill
  openings remain visible inside these lands. Thermal-via fields are outside
  this finite interface overlay; the colour does not certify a solder joint.
- Inner views show the board after turning it around its vertical axis:
  `x′ = 80 − x`, with the antenna edge still at the top. These are individual
  board-face views, not a single assembled-device coordinate system.
- Opposite-face protrusions appear faintly only outside the board outline.
  They provide placement context, not a 3D visibility calculation.

All **1208 items** in the current native inventory and 8 mounting footprints
are included. The display, cells, external antennas, loose cables and enclosure
are not invented: these are PCBs before final assembly. The large UI area is
the display bonding location; the RF outline is the current holder without cells.

The UI inner drawing also registers the separate speaker body, marked
`SPEAKER / ASSEMBLY`; it is not another PCB footprint. RF `LS1` is its two-wire
termination, not the speaker body. See [placement corrections](h6-r2-placement-repair.md)
for the maximum-body envelope and the limits of the mounting-space check.

MK1 belongs on **RF inner B0 [47,147.4]**, not on the outer view; the former
**F180 [8,112]** placement was incorrect and is superseded. **UI F `MIC`
[33,148.9]** identifies bottom access to that RF microphone, not a UI footprint.
The top port faces the inter-board space, with sound access through the designed
open bottom gap, not a downward port normal. The [seven-reference follow-up](../hardware/layout/h6-r2-microphone-bottom-candidate.json)
changes no MPN, net or copper. The capsule has an internal FET with a 2.2-kΩ load;
noise performance, actual routing and acoustic transfer remain unqualified.

**Open mechanical questions remain open.** In particular, this sheet does not
qualify holder geometry or solder-tool access, and does not replace the
[open findings](h6-r2-interface-review.md) with a readiness claim. Fab geometry
is not a qualified 3D model of every component.

## SMA solder-site checks

The [native pad-and-neighbour report](../hardware/layout/generated/H6-R2-sma-solder-access-audit.json)
checks both PCBs, keeping pad copper, Fab outlines and neighbouring component
courtyards separate. Provisionally expanding each land's bounding rectangle
by **1 mm along each axis** screens for tight areas: this is an engineering
review filter, not a factory requirement
or a model of a particular soldering tip. Entering that margin does not mean a
body collision or short circuit. Tool approach, heating and joint inspection
still need review; the previous “solder windows” checked only connector count
and pitch.

<!-- SMA-SOLDER-ACCESS:BEGIN -->

Current result: **50 lands**, 0 contacts/overlaps with foreign copper pads, 0 overlaps with available Fab bounding boxes and 0 courtyard overlaps. The provisional margin flagged **0 lands for review**.

Courtyard distances refer to mounting envelopes, **not physical bodies**; separate copper and Fab measurements are in the report. These are solder-access review items, not a list of shorts. `status: no_candidates_in_screened_scope`; `solder_process_qualified: false`.

<!-- SMA-SOLDER-ACCESS:END -->

## Freshness

Hashes of both source PCBs, the renderer and all five SVGs are recorded in the
[visualization snapshot](../hardware/layout/generated/H6-R2-component-views.json).
Rendering does not change PCB files. The normal routing-image command now
refreshes both routing exports, these five component SVGs and the
[current exterior preview](images/h6-r2-product-exterior.svg). It also checks
independent [placement requirements](../hardware/layout/generated/H6-R2-placement-intent.json):

```sh
python3 hardware/layout/h6_r2_routing_render.py --write
python3 hardware/layout/h6_r2_routing_render.py --check
```

The common check fails if either image group is stale. It is also run by the
architecture regression suite, including CI. Refresh after PCB changes before
publishing a checkpoint; this is not a background watcher of an open editor.

The dedicated `h6_r2_component_render.py --write/--check` commands remain
available. Dedicated writes require KiCad's Python (`pcbnew`) and KiCad CLI;
checks require only ordinary Python.

The SMA clearance report and its marked tables have a separate native command:
run `python3 hardware/layout/h6_r2_sma_solder_access.py --write` using Python
with `pcbnew`, then `--check` to recompute and compare. Refresh it after PCB
changes as well as the images; regression tests reject stale source hashes or
tables. Neither command changes the PCB.
