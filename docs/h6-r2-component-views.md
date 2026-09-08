# Components of both boards · four faces

[Home](../README.md) · [Review findings](h6-r2-interface-review.md) · [Русский](h6-r2-component-views.ru.md)

Direct views of the current KiCad PCBs, **at the same scale**, without tracks
or unrouted connection lines. Click a view to open the full SVG and zoom into
small components without losing detail.

| Front/UI board | Rear/RF board |
| --- | --- |
| **Outer F — 30 items + 4 mounting footprints** | **Outer F — 16 items + 4 mounting footprints** |
| [![UI outer](images/h6-r2-components-ui-outer.svg)](images/h6-r2-components-ui-outer.svg) | [![RF outer](images/h6-r2-components-rf-outer.svg)](images/h6-r2-components-rf-outer.svg) |
| **Inner B — 398 items** | **Inner B — 764 items** |
| [![UI inner](images/h6-r2-components-ui-inner.svg)](images/h6-r2-components-ui-inner.svg) | [![RF inner](images/h6-r2-components-rf-inner.svg)](images/h6-r2-components-rf-inner.svg) |

[All four views on one sheet](images/h6-r2-components-overview.svg).

## How to read

- Grey: current Fab body outlines and component references. References added
  for inspection **are not new production silkscreen**.
- Blue: actual silkscreen on the selected PCB face.
  Antenna labels sit closer to the connectors, with a single lawful-use
  sentence below: English on UI, Russian on RF.
- Ochre: drilled holes and the dashed L32 NFC reservation. **The loop is not routed yet**.
- Inner views show the board after turning it around its vertical axis:
  `x′ = 80 − x`, with the antenna edge still at the top. These are individual
  board-face views, not a single assembled-device coordinate system.
- Opposite-face protrusions appear faintly only outside the board outline.
  They provide placement context, not a 3D visibility calculation.

All **1208 items** in the current native inventory and 8 mounting footprints
are included. The display, cells, external antennas, loose cables and enclosure
are not invented: these are PCBs before final assembly. The large UI area is
the display bonding location; the RF outline is the current holder without cells.

**Known footprint defects remain visible.** In particular, this sheet does not
fix the missing audio cutout or holder geometry, and does not replace the
[open findings](h6-r2-interface-review.md) with a readiness claim. Fab geometry
is not a qualified 3D model of every component.

## Freshness

Hashes of both source PCBs, the renderer and all five SVGs are recorded in the
[visualization snapshot](../hardware/layout/generated/H6-R2-component-views.json).
Rendering does not change PCB files. The normal routing-image command now
refreshes both routing exports and these five component SVGs:

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
