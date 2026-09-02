# H6.0.1-R1 · Mechanical stack and M1 load relief

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-mechanical-stack.ru.md) · [Exact placement](h6-r2-exact-placement.md)

**Status:** ✅ the local screw, stop, enclosure-bearing and independent PCB-capture geometry is locked and machine-checked. The [five microcoax service loops](h6-r2-microcoax-service.md) now close H6.0.1; **H6.0.2 routing is current.** Purchase and fabrication remain unauthorized.

![H6 mechanical stack](images/h6-r2-mechanical-stack.svg)

## Result

The four existing M2.5 axes now use one exact, serviceable stack:

- four `Ettinger 007.02.611` polyamide pass-through stops set the **11.00 mm** PCB-to-PCB gap;
- four `Essentra 50M025045P020` fully threaded nylon-6/6 pan-head screws provide **20.00 mm below-head length**;
- four `Essentra 04M025045HN` M2.5 nylon-6/6 hex nuts snap into anti-rotation rear-shell pockets;
- both enclosure halves provide **1.40 mm** local bearing floors and 7.00-mm bearing annuli inside the existing 8.00-mm-diameter PCB keepouts;
- four 2.45-mm shell pilot shoulders locate each PCB in the existing 2.70-mm holes, while four short edge-lip segments retain each PCB independently.

M1 is not used as a clamp, stop or shear pin. The assembly procedure first seats both boards and all four exact stops, mates M1 in a parallel fixture, and only then tightens the screws diagonally to the low **0.05 N·m** seating target. The **0.09 N·m** limit is a conservative ceiling for the nylon fasteners, not an invitation to add preload after the stops touch.

## Worst-case stack

The [machine audit](../hardware/layout/generated/H6-R2-mechanical-stack-audit.json) evaluates enclosure-floor, both PCB, stop, screw and nut receipt allowances together:

| Quantity | Result |
|---|---:|
| Under-head clamp path, nominal | 17.00 mm |
| Under-head clamp path, full range | 16.38…17.62 mm |
| Thread available at the nut, worst minimum | 2.18 mm |
| Thread beyond a 2.00-mm nut, worst minimum | 0.18 mm |
| Thread beyond a 1.80-mm nut, worst maximum | 2.02 mm |
| Screw-tip clearance to rear exterior, worst minimum | 0.38 mm |
| Pilot-to-hole diametral clearance, worst minimum | 0.15 mm |

Thus even the short-screw/thick-stack corner fully engages the conservative 2.00-mm nut envelope, while the long-screw/thin-stack corner remains buried inside the 4.20-mm rear recess.

## If one screw is loose

One screw backed off by one pitch does not transfer the enclosure job to M1:

1. the other three screws still clamp the four-stop sandwich;
2. four shell pilots on each enclosure half carry in-plane PCB shear;
3. four edge-lip segments per PCB prevent the corresponding board leaving its shell seat;
4. the captured rear nuts cannot rotate or fall into the electronics during ordinary service.

This is robust-by-design for the single hobby prototype. It does not invent drop, vibration or prescribed-cycle qualification that the project does not need.

## Supply and receipt boundary

These are owner-installed enclosure parts, not JLCPCB PCBA placements. The exact screw is active and distributor-stocked, with its 20.00-mm length, 5.00-mm head diameter and 2.10-mm head height published by [DigiKey](https://www.digikey.com/en/products/detail/essentra-components/50M025045P020/11637969). The exact nut identity and 5.00-mm across-flats / 2.00-mm current dimensional presentation are published by [Essentra](https://www.essentracomponents.com/en-gb/p/standard-hex-nuts-plastic/04m025045hn?indexed=true); the audit intentionally admits the 1.80-mm distributor/catalog presentation as the other height corner. The selected 11-mm stop remains traceable through the [exact Bürklin listing](https://www.buerklin.com/en/p/ettinger/spacer-bolts/007-02-611/18H0210/).

Before final assembly, measure the four screws, nuts and stops against the receipt windows in the [source contract](../hardware/layout/h6-r2-mechanical-stack.json). A part outside that window is rejected; the PCB or enclosure is not silently reworked around it.

## H6.0.1 closure

The [microcoax service result](h6-r2-microcoax-service.md) replaces the old illustrative cable lines with five exact H6 corridors and tape-saddle positions. It proves relaxed cable length, connector inspection access, the display/FPC pocket and 2D mechanical keepout clearance. H6.0.1 is closed; H6.0.2 now routes the boards, while the assembled STEP repeats exact opposing-body clearance in H6.0.6.

## Reproduce

```bash
python3 hardware/layout/h6_r2_mechanical_stack.py --check
```

Expected result:

```text
H6-R2 mechanical stack pass: 4 axes; 2.18 mm minimum nut thread; 0.38 mm tip clearance
```
