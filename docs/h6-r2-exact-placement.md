# H6.0.3-R1 · Exact-footprint placement

[Home](../README.md) · [Current routing](h6-r2-current-routing.md) · [Русский](h6-r2-exact-placement.ru.md)

**Status:** ✅ the corrected 80 × 150-mm placement is accepted as the new
unrouted H6.0.3 baseline. Routing is still in progress; this page does not
authorize fabrication or purchase.

![Exact H6 placement of both accessible inner faces](images/h6-r2-exact-placement.svg)

## What we want

Fit every selected production footprint on the two fixed-size boards while
preserving the reviewed mechanical interfaces and keeping electrically local
parts beside the device or network that owns them. A visually collision-free
placement alone is not sufficient.

## What we decided

- Retain the two 80 × 150-mm, six-copper-layer boards. The 85 × 150-mm fallback
  is considered only if a required route remains impossible after legal local
  rearrangement.
- Keep the accepted display bed, ready-cut PSA guide, relaxed FPC slot, four
  M2.5 stop axes per PCB and both five-port antenna banks fixed.
- Constrain bypass, feedback, bootstrap, clock-load, USB-PD, charger, eFuse and
  battery-protection parts to their owners. Critical converter parts use
  explicit owner and distance limits; the remaining local parts use
  deterministic owner rules. Fuses and the current shunt target the relevant
  electrical pad of the large battery-holder footprint, not its geometric
  centre.
- Freeze all 1,208 resulting anchors. Normal placement checks ignore copper so
  they can validate a routed board without moving anything; `--write` remains
  an intentionally destructive unrouted-seed rebuild.

## What we obtained

- Two native KiCad 10 boards containing all **1,208/1,208** fitted schematic
  instances: 428 on UI and 780 on RF/power.
- All **789** global canonical / **823** board-local H2 nets bound to real pads.
- Zero hard same-face courtyard conflicts, zero unplaced bodies and zero
  net/footprint mapping errors.
- **310/310** local-part → owner pairs within their permitted courtyard or
  owner-pad gaps;
  zero locality violations.
- **21/21** electrically critical pad-centre pairs pass their explicit limits.
  This covers every switching-node net and selected SD, I2S and charger-input
  bypasses, so useful pad orientation is checked as well as body locality.
- Zero native KiCad DRC findings on both corrected unrouted boards.
- A deterministic generator, a hash-bearing
  [machine audit](../hardware/layout/generated/H6-R2-placement-audit.json) and
  an exact 1,208-anchor freeze.

The previous routed seed is retained only in Git history. It was rejected
because several converter feedback/bootstrap parts and many bypass capacitors
were tens of millimetres from their owners. The corrected placement also lowers
the RF-board minimum-spanning net length from 18,372.9 to 14,687.4 mm; this is
a placement comparison, not routed-copper performance evidence.

## What happens next

Route the four DC/DC islands and protection first, then RF/clock clusters,
USB/direct-i8080, remaining digital/control nets, planes and return paths. The
[current-routing page](h6-r2-current-routing.md) is the sole owner of live
copper counts and routing progress.

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

Do not run `--write` after new routing has begun: it intentionally replaces
each PCB with the accepted unrouted seed.
