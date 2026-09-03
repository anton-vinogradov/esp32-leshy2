# H6.0.1-R1 · Exact-footprint placement

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-exact-placement.ru.md)

**Status:** ✅ the native-PCB placement slice of H6.0.1 is reproducible and
collision-free. The [mechanical stack](h6-r2-mechanical-stack.md) and
[microcoax service closure](h6-r2-microcoax-service.md) now complete H6.0.1.
**H6.0.2 routing and native net parity are current.** This result does not
authorize fabrication or purchase.

![Exact H6 placement of both accessible inner faces](images/h6-r2-exact-placement.svg)

## What now exists

- two native six-copper-layer KiCad 10 boards beside the reviewed H2
  schematics: [UI PCB](../hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb)
  and [RF/power PCB](../hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb);
- all **1,208/1,208** reviewed fitted schematic instances placed using their
  selected KiCad footprints: 428 on UI and 780 on RF/power;
- all **789** global canonical / **823** board-local H2 nets assigned to their real footprint pads;
- four M2.5 stop axes on each PCB, the rounded 75 × 150 mm outlines, the exact
  display bed, ready-cut PSA guide and relaxed FPC slot on the UI board;
- the current 5+5 direct-source antenna bank and user-facing board/screen
  silkscreen in the native boards;
- one deterministic unrouted-seed generator, machine contract, hash-bearing
  placement audit and an exact **1,208-anchor freeze** that prevents a local
  route-driven correction from repacking unrelated components.

The [machine audit](../hardware/layout/generated/H6-R2-placement-audit.json)
reports zero hard courtyard conflicts, zero unplaced instances and zero
net/footprint mapping errors. Unrouted-seed regeneration is byte-for-byte
reproducible. The routine `--check` uses a routing-insensitive placement
signature: footprints, pad/net binding, setup, constraints and board geometry
must still match, while tracks, vias and copper pours are preserved and ignored.
The deliberately destructive `--write` mode remains only for rebuilding a clean
unrouted seed. KiCad 10 parses both native boards and exports placement files
from them.

The freeze also records two reviewed local H6.0.2 corrections: `R59` moved to
open the encoder-side U12 pin-2/pin-3 fan-out, and `R109` moved to open the U12
pin-7 C5 service-USB fan-out. All other anchors remain exactly where accepted;
the regenerated placement still reports 1,208/1,208 positions and zero hard
conflicts.

## Exact-footprint corrections to the H1 drawing

H1 was a physically reviewed body model, not a claim that every illustrative
rectangle already equalled a KiCad courtyard. Loading the selected production
footprints exposed and corrected four real issues:

1. each five-port antenna bank moved to symmetric centres
   **14.00 / 25.75 / 37.50 / 49.25 / 61.00 mm**, clearing the upper screw-head
   keepouts while keeping all RF feeds on their source PCB;
2. the complete display, slot and ZIF system moved 8.50 mm away from the exact
   edge-SMA courtyards; their relative geometry and at least 5 mm relaxed FPC
   slack are unchanged;
3. the side function switches rotate 90° and the D-pad pitch becomes 10.5 mm,
   so the exact OMRON B3S courtyards do not overlap each other or the display;
4. the encoder land pattern rotates 90° around the same user-visible shaft
   axis, leaving 0.91 mm to the battery-holder courtyard.

These are production-footprint corrections, not product-function changes.

## Stack candidate and H6.0.1 closure

The current factory calculator identifies the standard/recommended 1.6-mm
order option as [`JLC06161H-3313`](https://jlcpcb.com/pcb-impedance-calculator/),
with a calculated finished thickness of 1.54 mm ±10%: 0.035-mm outer copper,
0.0152-mm inner copper, 0.0994-mm outer 3313 prepreg, 0.1088-mm centre 2116
prepreg and two 0.55-mm cores. The current outer-layer geometry is now bound
in the routing policy; an order-time calculator recheck remains mandatory.

The [mechanical-stack slice](h6-r2-mechanical-stack.md) now locks the enclosure
capture lips, four pilot datums, wall bearings and exact 20-mm nylon
screw/captive-nut geometry. Its worst tolerance corner still provides 2.18 mm
of thread at the nut and keeps the screw tip buried; M1 has no structural role.
The [five relaxed microcoax service-loop corridors](h6-r2-microcoax-service.md),
clip positions and enclosure/inspection clearances are now machine-checked.
They close H6.0.1 and release H6.0.2 routing without changing this placement;
H6.0.2 owns zero-finding DRC plus schematic/PCB parity.

## Reproduce

Run with KiCad's bundled Python:

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_placement.py --check
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_placement_freeze.py --check
```

Expected result:

```text
H6-R2 placement pass: 1208/1208 positions; 0 hard conflicts; 0 unplaced
H6-R2 placement freeze pass: 1208 exact anchors
```

This is safe on a routed board. Do not run `--write` after routing has begun: it
intentionally replaces each PCB with the reviewed unrouted seed.
