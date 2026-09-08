# H6.0.1-R1 - Microcoax service and inspection closure

[Home](../README.md) - [Roadmap](roadmap.md) - [Русский](h6-r2-microcoax-service.ru.md) - [Exact placement](h6-r2-exact-placement.md) - [Mechanical stack](h6-r2-mechanical-stack.md)

<!-- BEGIN GENERATED MICROCOAX status -->
**Machine result: `pass` — nominal geometry only.** The audit covers 5 paths on the 80 × 150 mm board; 5 nominal curves are checked against the 6-mm design-radius target. The minimum relaxed reserve is 5.223 mm. Source windows `N24-0`, `N24-1`, `N24-2` still require actual-axis and three-dimensional forming checks in `H6.0.7`. `all_source_positions_planar_radius_verified: false`. Antenna-window checks cover contract count and pitch only; this audit does not establish solder access. `native_solder_access_verified_by_this_audit: false`.
<!-- END GENERATED MICROCOAX status -->

This updates `H6.0.1-R1` within current `H6.0.3-R1` routing requalification. Purchase and fabrication remain unauthorized.

![Five H6 microcoax service corridors](images/h6-r2-microcoax-service.svg)

## Result

The complete front radio bank remains local to the UI PCB:

<!-- BEGIN GENERATED MICROCOAX results -->
| Path | Exact cable / length | Corridor, max | Reserve, min | Planar radius, min |
|---|---|---:|---:|---:|
| `N24-0` | `TE Connectivity 1-2118651-0`, 60 mm | 52.343 mm | 7.657 mm | 6.000 mm |
| `S3-2G4` | `TE Connectivity 2118651-2`, 30 mm | 24.777 mm | 5.223 mm | 308.971 mm |
| `N24-1` | `TE Connectivity 1-2118651-0`, 60 mm | 45.372 mm | 14.628 mm | 6.000 mm |
| `C5-2G4/5` | `TE Connectivity 2118651-2`, 30 mm | 13.519 mm | 16.481 mm | 14.650 mm |
| `N24-2` | `TE Connectivity 1-2118651-0`, 60 mm | 42.474 mm | 17.526 mm | 6.000 mm |

Cable diameter is 1.13 mm; corridor width is 2.50 mm. Each saddle has a 5 × 3 mm landing with a 0.25 mm courtyard margin. At least 5 mm of routed length is required from each mating axis to the saddle centre, plus 5 mm of relaxed total-length reserve.

S3: source axis [30.500; 23.615] mm → board U.FL axis [19.040; 3.480] mm; saddle centre [24.535; 13.549] mm. Its conservative length includes 1.604 mm for both height transitions.
<!-- END GENERATED MICROCOAX results -->

Every route has one removable polyimide-tape saddle on a machine-checked clear landing. Apply it only after both ends are mated and a visible relaxed bow exists: it retains the route without flattening the cable or loading the connectors. Four saddles sit on PCB solder mask. The S3 saddle sits on the documented flat central portion of the module's metal shield, clear of its rim and connector notch. The planar radius in the table does not prove the combined three-dimensional bends at the shield transitions.

Source geometry is derived from manufacturer-local coordinates, then transformed by native **B.Cu reflection and the actual footprint rotation**. Board-side U.FL destinations use the mating/body axis, not the centre of their asymmetric courtyard. The [generated audit](../hardware/layout/generated/H6-R2-microcoax-service-audit.json) owns the complete current coordinates and clearances; source and destination axes are checked against the native placement freeze.

The S3 and C5 source axes are dimensioned in the module drawings. Ebyte locates IPEX at the lower-left corner in module top view, opposite the digital pads, without dimensioning its centre. The nRF checks therefore transform the conservative corner envelopes in the source contract and calculate reach from their farthest points.

The N24 paths use actual tangent circular arcs, with an enlarged final arc around the left screw on N24-0. The generator checks tangent lengths, analytic arc lengths and the full-width curved envelope, including a conservative bound on sampling error. Tape centres lie on these curves. For Ebyte, these shapes start at the **window centre**: the length calculation covers the farthest source position, but radius/clearance for every possible position in that window remains the explicit `H6.0.7` gate.

## Display and enclosure clearance

`N24-0` passes left of the display FPC slot and ZIF; `N24-1` passes right. The audit checks the complete nominal curved corridor and every tape saddle against the slot and ZIF latch exclusions.

<!-- BEGIN GENERATED MICROCOAX clearance -->
The minimum centreline distance to the display exclusions is 3.843 mm, against the required 2.00 mm corridor-plus-clearance envelope.

The route-prism reservation above the UI inner face is 4.70 mm; at least 1.00 mm free height above the cable is also required. The maximum combined S3 shield, cable and tape height is 4.58 mm. The connector-inspection cylinder diameter is 6 mm.

The minimum 2D clearance from the full corridor edge to screw/stop keepouts is 0.757 mm on `N24-2`; `N24-0` clears by 1.875 mm. These are service-corridor clearances, not clearances from the thinner cable.

The contract defines 10 nominal solder-inspection windows of width 10.00 mm for the two antenna banks. The minimum port pitch from the placement contract is 14.700 mm, leaving 4.700 mm between adjacent windows. This checks window count and pitch, not native pads: it does not detect solder-land obstruction by neighbouring bodies, tool access or solder-fillet visibility. See the [separate native screening](../hardware/layout/generated/H6-R2-sma-solder-access-audit.json); its engineering clearances are not factory solder-process qualification.
<!-- END GENERATED MICROCOAX clearance -->

No enclosure rib, stop, screw, adhesive or loose hardware may enter a corridor or connector inspection cylinder. The audit checks every nominal full-width corridor and tape landing against the screw/head keepouts; tape landings also respect the inner-face solder lands of front-mounted SMA connectors. The assembled STEP repeats the exact opposing-body and enclosure check in `H6.0.7`: this 2D result does not establish assembled clearance. Before enclosure closure, both edge-soldered ground tabs and the centre launch of every SMA/RP-SMA must remain visible through the inspection windows.

## Owner assembly order

1. With both PCBAs open and unpowered, check centre continuity, shield continuity and centre-to-shield isolation on every loose cable.
2. Mate each plug straight down by its metal cap. Never push, pull or unmate by the cable.
3. Route the cable inside its named corridor, form the visible non-taut bow and apply its one removable tape saddle: S3 on the indicated flat shield area, the other four on their clear PCB landings.
4. Inspect all ten microcoax mates and all ten two-sided antenna solder windows.
5. Confirm that no cable crosses M1, a stop, screw axis, display slot or ZIF latch; then seat the four stops and mate M1 in the parallel fixture.

The formed-radius target is a conservative H6 design choice, not an unpublished TE requirement. Received-cable bend, strain and mating behaviour remain physical H7/H8 evidence; a received Ebyte connector outside its published-corner window reopens this result instead of forcing the cable.

## Reproduce

```bash
python3 hardware/layout/h6_r2_microcoax_service.py --check
```

Expected result:

<!-- BEGIN GENERATED MICROCOAX reproduce -->
```text
H6-R2 microcoax service pass: 5 paths; 5 clear saddles; 5.22 mm minimum reserve
```
<!-- END GENERATED MICROCOAX reproduce -->

The same command checks the numerical blocks in both language versions. Machine evidence: [source contract](../hardware/layout/h6-r2-microcoax-service.json) and [generated audit](../hardware/layout/generated/H6-R2-microcoax-service-audit.json).
