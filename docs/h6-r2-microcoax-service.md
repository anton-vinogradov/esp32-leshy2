# H6.0.1-R1 - Microcoax service and inspection closure

[Home](../README.md) - [Roadmap](roadmap.md) - [Русский](h6-r2-microcoax-service.ru.md) - [Exact placement](h6-r2-exact-placement.md) - [Mechanical stack](h6-r2-mechanical-stack.md)

**Status:** ✅ all five owner-installed microcoax routes now have exact H6 corridors, clear retention landings, relaxed length reserve and connector/antenna inspection access. This closes `H6.0.1-R1`; **`H6.0.2-R1` routing and net parity are current.** Purchase and fabrication remain unauthorized.

![Five H6 microcoax service corridors](images/h6-r2-microcoax-service.svg)

## Result

The complete front radio bank remains local to the UI PCB:

| Path | Exact cable | Conservative corridor, max | Relaxed reserve, min |
|---|---|---:|---:|
| `N24-0` | `TE Connectivity 1-2118651-0`, 60 mm | 45.064 mm | 14.936 mm |
| `S3-2G4` | `TE Connectivity 2118651-2`, 30 mm | 15.280 mm | 14.720 mm |
| `N24-1` | `TE Connectivity 1-2118651-0`, 60 mm | 49.524 mm | 10.476 mm |
| `C5-2G4/5` | `TE Connectivity 2118651-2`, 30 mm | 20.870 mm | **9.130 mm** |
| `N24-2` | `TE Connectivity 1-2118651-0`, 60 mm | 42.457 mm | 17.543 mm |

Each 1.13-mm cable gets a 2.50-mm-wide service corridor and one **5 × 3 mm** machine-checked clear landing for a removable polyimide-tape saddle. The saddle is at least 5 mm of routed length away from both connectors. It is applied only after both ends are mated and a visible relaxed bow exists; it retains the route but does not flatten the cable or become connector strain.

The two 30-mm source axes are exact drawing coordinates. The Ebyte specification locates each nRF IPEX in one module corner but does not dimension its centre. Therefore the three nRF checks deliberately use the farthest point of a generous **5 × 5 mm published-corner access window**, rather than inventing a precise axis from the picture. All three still exceed the common 5-mm reserve rule.

## Display and enclosure clearance

`N24-0` passes left of the display FPC slot and ZIF; `N24-1` passes right. The generated audit buffers the complete cable corridor and proves at least **2.255 mm centreline distance** to those exclusions, above the required 2.00 mm corridor-plus-clearance envelope. No cable or tape saddle crosses the slot or the ZIF latch.

The enclosure contract reserves a 4.50-mm-high route prism above the UI inner face and at least 1.00 mm free height above the cable. No enclosure rib, stop, screw, adhesive or loose hardware may enter a corridor or a 6-mm-diameter connector inspection cylinder. The machine audit now checks every full-width corridor and tape landing against all four 4-mm-radius screw/head keepouts; the smallest remaining 2D edge clearance is **0.456 mm**. The assembled STEP repeats the exact opposing-body and enclosure check in `H6.0.6`; this is not silently claimed from a 2D drawing.

Both PCB antenna banks also receive five non-overlapping 10.0-mm-wide solder-inspection windows. Before enclosure closure, both edge-soldered ground tabs and the centre launch of every SMA/RP-SMA remain visible. The current 11.75-mm minimum port pitch leaves at least 1.75 mm between adjacent windows.

## Owner assembly order

1. With both PCBAs open and unpowered, check centre continuity, shield continuity and centre-to-shield isolation on every loose cable.
2. Mate each plug straight down by its metal cap. Never push, pull or unmate by the cable.
3. Route the cable inside its named corridor, form the visible non-taut bow and apply its one removable tape saddle.
4. Inspect all ten microcoax mates and all ten two-sided antenna solder windows.
5. Confirm that no cable crosses M1, a stop, screw axis, display slot or ZIF latch; then seat the four stops and mate M1 in the parallel fixture.

The 6-mm formed-radius value is a conservative H6 design target, not an unpublished TE requirement. Received-cable bend, strain and mating behaviour remain physical H7/H8 evidence; a received Ebyte connector outside its published-corner window reopens this result instead of forcing the cable.

## Reproduce

```bash
python3 hardware/layout/h6_r2_microcoax_service.py --check
```

Expected result:

```text
H6-R2 microcoax service pass: 5 paths; 5 clear saddles; 7.69 mm minimum reserve
```

Machine evidence: [source contract](../hardware/layout/h6-r2-microcoax-service.json) and [generated audit](../hardware/layout/generated/H6-R2-microcoax-service-audit.json).
