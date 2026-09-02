# H6.0.1-R1 · Exact-footprint placement

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-exact-placement.ru.md)

**Status:** ✅ the native-PCB placement slice of H6.0.1 is reproducible and
collision-free. **H6.0.1 and H6 as a whole remain in progress.** Routing has
not started and this result does not authorize fabrication or purchase.

![Exact H6 placement of both accessible inner faces](images/h6-r2-exact-placement.svg)

## What now exists

- two native six-copper-layer KiCad 10 boards beside the reviewed H2
  schematics: [UI PCB](../hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb)
  and [RF/power PCB](../hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb);
- all **1,208/1,208** reviewed fitted schematic instances placed using their
  selected KiCad footprints: 428 on UI and 780 on RF/power;
- all **823** canonical H2 nets assigned to their real footprint pads;
- four M2.5 stop axes on each PCB, the rounded 75 × 150 mm outlines, the exact
  display bed, ready-cut PSA guide and relaxed FPC slot on the UI board;
- the current 5+5 direct-source antenna bank and user-facing board/screen
  silkscreen in the native boards;
- one deterministic generator, machine contract and hash-bearing audit.

The [machine audit](../hardware/layout/generated/H6-R2-placement-audit.json)
reports zero hard courtyard conflicts, zero unplaced instances and zero
net/footprint mapping errors. Regeneration is byte-for-byte reproducible. KiCad
10 parses both native boards and exports placement files from them.

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

## Stack candidate and remaining H6.0.1 work

The board files use six copper layers and 1.6 mm finished thickness. The
[JLC3313 six-layer impedance candidate](https://jlcpcb.com/impedance) remains a
placement-time candidate only; H6.0.4/H6.0.5 must bind real trace widths,
dielectrics and order-calculator values before release.

The [mechanical-stack slice](h6-r2-mechanical-stack.md) now locks the enclosure
capture lips, four pilot datums, wall bearings and exact 20-mm nylon
screw/captive-nut geometry. Its worst tolerance corner still provides 2.18 mm
of thread at the nut and keeps the screw tip buried; M1 has no structural role.
H6.0.1 now remains open only for the five relaxed microcoax service-loop
corridors, clip positions and their enclosure/inspection clearances. Only after
those physical constraints are closed does H6.0.2 start routing and own
zero-finding DRC plus schematic/PCB parity.

## Reproduce

Run with KiCad's bundled Python:

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_placement.py --check
```

Expected result:

```text
H6-R2 placement pass: 1208/1208 positions; 0 hard conflicts; 0 unplaced
```
