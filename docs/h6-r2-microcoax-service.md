# H6.0.1-R1 - Microcoax service and inspection closure

[Home](../README.md) - [Roadmap](roadmap.md) - [Русский](h6-r2-microcoax-service.ru.md) - [Exact placement](h6-r2-exact-placement.md) - [Mechanical stack](h6-r2-mechanical-stack.md)

**Status:** all five nominal microcoax centreline shapes pass H6 clearance, retention and relaxed-length checks on the 80 × 150 mm baseline. Their real tangent curves meet the 6-mm planar-radius target. **The three Ebyte source windows still require forming/envelope validation at the actual connector axes in `H6.0.7`; this is not an all-source-position radius approval.** This updates `H6.0.1-R1` within current `H6.0.3-R1` routing requalification. Purchase and fabrication remain unauthorized.

![Five H6 microcoax service corridors](images/h6-r2-microcoax-service.svg)

## Result

The complete front radio bank remains local to the UI PCB:

| Path | Exact cable | Conservative corridor, max | Relaxed reserve, min |
|---|---|---:|---:|
| `N24-0` | `TE Connectivity 1-2118651-0`, 60 mm | 50.743 mm | 9.257 mm |
| `S3-2G4` | `TE Connectivity 2118651-2`, 30 mm | 24.564 mm | **5.436 mm** |
| `N24-1` | `TE Connectivity 1-2118651-0`, 60 mm | 45.372 mm | 14.628 mm |
| `C5-2G4/5` | `TE Connectivity 2118651-2`, 30 mm | 13.519 mm | 16.481 mm |
| `N24-2` | `TE Connectivity 1-2118651-0`, 60 mm | 42.474 mm | 17.526 mm |

Each 1.13-mm cable gets a 2.50-mm-wide service corridor and one **5 × 3 mm** machine-checked clear landing for a removable polyimide-tape saddle. The audit measures at least 5 mm of routed length from each mating axis to the saddle centre. It is applied only after both ends are mated and a visible relaxed bow exists; it retains the route but does not flatten the cable or become connector strain. Four saddles sit on PCB solder mask. The S3 saddle sits on the documented flat central portion of the module's metal shield, clear of its rim and connector notch. Its conservative length includes a **1.604-mm** allowance for both height transitions. The analytic planar curves have minimum radii of **13.135 mm for S3** and **14.650 mm for C5**; combined three-dimensional forming remains a physical check.

The source geometry is derived from manufacturer-local coordinates, then transformed by native **B.Cu reflection and footprint rotation**. C5 is at 180° and the three Ebyte modules at 270°. This puts their real connector ends in the intended service bays. S3's actual source axis is at `[31.000, 23.615]` mm, at the lower-right of its placed body. Board-side U.FL destinations use the mating/body axis; their asymmetric courtyard centres are displaced by 0.375 mm and are not cable endpoints.

The two 30-mm source axes are dimensioned in the module drawings. Ebyte locates IPEX at the lower-left corner in module top view, opposite the eight digital pads, without dimensioning its centre. The three nRF checks therefore transform a conservative **5 × 5 mm corner envelope** and calculate reach from its farthest point. All five routes retain the common minimum 5-mm reserve. The [generated audit](../hardware/layout/generated/H6-R2-microcoax-service-audit.json) owns the full current coordinates and clearances.

The N24 paths now use actual tangent circular arcs of radius 6 mm, with a 7-mm final arc around the left screw on N24-0. The generator checks tangent lengths, analytic arc lengths and the full-width curved envelope, including a conservative bound on sampling error. Tape centres lie on these curves. For Ebyte, these shapes start at the **window centre**; the length calculation covers the farthest source position, but radius/clearance for every possible position in that window remains the explicit `H6.0.7` gate. The audit reports five nominal radius-checked paths and `all_source_positions_planar_radius_verified: false`.

## Display and enclosure clearance

`N24-0` passes left of the display FPC slot and ZIF; `N24-1` passes right. The generated audit buffers the complete nominal curved corridor and proves at least **3.843 mm centreline distance** to those exclusions, above the required 2.00 mm corridor-plus-clearance envelope. No nominal cable route or tape saddle crosses the slot or the ZIF latch.

The enclosure contract reserves a **4.70-mm-high** route prism above the UI inner face and at least 1.00 mm free height above the cable. S3's maximum shield height, cable and tape together occupy 4.58 mm. No enclosure rib, stop, screw, adhesive or loose hardware may enter a corridor or a 6-mm-diameter connector inspection cylinder. The machine audit checks every nominal full-width corridor and tape landing against all four 4-mm-radius screw/head keepouts, and also checks the inner-face solder lands of front-mounted SMA connectors. The smallest remaining 2D edge clearance is **0.757 mm on N24-2**, measured from the reserved 2.50-mm-wide corridor rather than the thinner 1.13-mm cable. The rounded N24-0 route clears its screw envelope by **1.879 mm**. These corridor changes require no component moves. The assembled STEP repeats the exact opposing-body and enclosure check in `H6.0.7`; the 2D result does not establish assembled clearance.

Both PCB antenna banks also receive five non-overlapping 10.0-mm-wide solder-inspection windows. Before enclosure closure, both edge-soldered ground tabs and the centre launch of every SMA/RP-SMA remain visible. The current 11.75-mm minimum port pitch leaves at least 1.75 mm between adjacent windows.

## Owner assembly order

1. With both PCBAs open and unpowered, check centre continuity, shield continuity and centre-to-shield isolation on every loose cable.
2. Mate each plug straight down by its metal cap. Never push, pull or unmate by the cable.
3. Route the cable inside its named corridor, form the visible non-taut bow and apply its one removable tape saddle: S3 on the indicated flat shield area, the other four on their clear PCB landings.
4. Inspect all ten microcoax mates and all ten two-sided antenna solder windows.
5. Confirm that no cable crosses M1, a stop, screw axis, display slot or ZIF latch; then seat the four stops and mate M1 in the parallel fixture.

The 6-mm formed-radius value is a conservative H6 design target, not an unpublished TE requirement. Received-cable bend, strain and mating behaviour remain physical H7/H8 evidence; a received Ebyte connector outside its published-corner window reopens this result instead of forcing the cable.

## Reproduce

```bash
python3 hardware/layout/h6_r2_microcoax_service.py --check
```

Expected result:

```text
H6-R2 microcoax service pass: 5 paths; 5 clear saddles; 5.44 mm minimum reserve
```

Machine evidence: [source contract](../hardware/layout/h6-r2-microcoax-service.json) and [generated audit](../hardware/layout/generated/H6-R2-microcoax-service-audit.json).
