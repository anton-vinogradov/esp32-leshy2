# H6.0.3-R1 · Exact-footprint placement

[Home](../README.md) · [Current routing](h6-r2-current-routing.md) · [Русский](h6-r2-exact-placement.ru.md)

**Status:** ✅ the corrected 80 × 150-mm placement is accepted and its anchors
are frozen. The live boards are partially routed; placement acceptance is not
routing completion or electrical sign-off. `H6-NATIVE-ELECTRICAL-SEMANTICS`
remains open, and fabrication or purchase is not authorized.

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
- All **788** global canonical / **822** board-local H2 nets bound to real pads.
- Zero hard same-face courtyard conflicts, zero unplaced bodies and zero
  net/footprint mapping errors.
- **311/311** local-part → owner pairs within their permitted courtyard or
  owner-pad gaps;
  zero locality violations.
- **34/34** electrically critical pad-centre pairs pass their explicit limits.
  This covers every switching-node net and selected local bypasses, including
  the detector and service-logic ICs, S3 supply and the supply side of the
  Airband LNA bias choke. Useful pad orientation is checked as well as body
  locality; these distances do not certify the final routed current loops.
- A deterministic generator, a hash-bearing
  [machine audit](../hardware/layout/generated/H6-R2-placement-audit.json) and
  an exact 1,208-anchor freeze.

The rejected seed remains in Git history. The corrected placement is the
baseline for the live routing; current copper and DRC evidence belong to the
[current-routing page](h6-r2-current-routing.md).

These placement checks do not establish electrical validity of the schematic.
The current all-passive symbol-pin typing limits what native ERC can detect;
the electrical-semantics gate remains required.

## What happens next

First close [`H6-NATIVE-ELECTRICAL-SEMANTICS`](h6-r2-current-routing.md): review
physical-pin types, rail sources and output conflicts, then rerun ERC. Resume
routing and final return-path checks in the sequence maintained on the
current-routing page, the sole owner of live copper counts and routing progress.

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
