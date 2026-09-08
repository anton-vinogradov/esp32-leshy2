# H6.0.1-R1 · Mechanical stack and M1 load relief

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-mechanical-stack.ru.md) · [Exact placement](h6-r2-exact-placement.md)

**Status, 2026-09-08:** the declared screw/stop/capture tolerance checks pass, but physical battery contact is **reopened**. The previous 3.3-mm cell-floor and 20% compression claims are withdrawn. The [five nominal microcoax paths](h6-r2-microcoax-service.md) retain their scoped result; **H6.0.3 routing is current.** Neither purchase, fabrication nor battery energization is authorized.

**Open before production release:** SMA / finished-thickness fit, exact holder mounting geometry and power routing, and `H6-CELL-NTC-HEIGHT-FIT`. A fastener or XY-placement pass does not close any of these conditions.

![H6 mechanical stack](images/h6-r2-mechanical-stack.svg)

## Result

The four existing M2.5 axes now use one exact, serviceable stack:

- four `Ettinger 007.02.611` polyamide pass-through stops set the **11.00 mm** PCB-to-PCB gap;
- four `Essentra 50M025045P020` fully threaded nylon-6/6 pan-head screws provide **20.00 mm below-head length**;
- four `Essentra 04M025045HN` M2.5 nylon-6/6 hex nuts snap into anti-rotation rear-shell pockets;
- both enclosure halves provide **1.40 mm** local bearing floors and 7.00-mm bearing annuli inside the existing 8.00-mm-diameter PCB keepouts;
- four 2.45-mm shell pilot shoulders locate each PCB in the existing 2.70-mm holes, while four short edge-lip segments retain each PCB independently.

M1 is not used as a clamp, stop or shear pin. The assembly procedure first seats both boards and all four exact stops, mates M1 in a parallel fixture, and only then tightens the screws diagonally to the low **0.05 N·m** seating target. The **0.09 N·m** limit is a conservative ceiling for the nylon fasteners, not an invitation to add preload after the stops touch.

## Cell-temperature contact

**What is required.** Each of the two NTCs must measure its own cell rather than air or FR-4 temperature, while neither PCB copper nor a sensor electrode may touch the cell can.

**Current design.** Factory-fitted `TDK B57332V5103F360` sensors sit on the RF PCB outer face at `(33.44, 85.00)` and `(52.54, 85.00)` mm. Their nominal transverse cell-axis alignment is checked, not the full three-dimensional channel fit. The selected ready-cut insulating `t-Global TG-A3500-5-5-3.0` 5×5×3-mm pads remain planning parts: their thickness has **not** been qualified for this holder. The PCB has clear contact beds with `NTC0 PAD` / `NTC1 PAD` corner marks. No parts have been replaced or ordered by this correction.

**Correction and remaining evidence.** The full [manufacturer-authored 1048P Rev A sheet](https://file.aichiplink.com/r/datasheets/keystoneelectronics-1048p-datasheets-1060.pdf) identifies 3.43 mm as retaining-post projection **below** the PCB; the catalogue gives 3.3 mm for that feature. These source values are not a reconciled tolerance range. Neither is the cell bottom above the PCB. The previous 20% calculation therefore had no valid floor datum. A maximum NTC height is also insufficient to prove a nominal or worst-case compression range. The audit now reports both floor height and compression as `null`, with `physical_contact_proved: false`.

Before selecting the final pad thickness, establish the registered cell surface and channel dimensions, NTC/pad height tolerances, and an acceptable contact-force window. Each can must touch only insulating material without lifting or rocking. A later non-destructive dry-fit verifies the received parts; it does not replace this missing design work. The [native holder-polarity correction](../hardware/layout/h6-r2-holder-polarity-integration.json) does not qualify this contact or complete the affected power routing.

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

## SMA fit before production release

**Checked on 2026-09-07.** The exact GCT `RFPC-SMA31-FN-175-A` and `RFPC-SMA32-FN-175-A` use a **1.75 ± 0.10 mm** PCB slot, according to the [SMA31](https://www.mouser.com/datasheet/3/1507/1/RFPC-SMA31-FN.pdf) and [SMA32](https://www.mouser.com/datasheet/3/1507/1/RFPC_SMA32_FN.pdf) A1 drawings. [JLCPCB's published finished-thickness tolerance](https://jlcpcb.com/capabilities/pcb-capabilities) for the selected nominal 1.60-mm PCB is ±10%, or **1.44…1.76 mm**, matching both existing PCB allowances in this contract.

The nominal assembly clearance is **+0.15 mm**, but the smallest slot and thickest board give **−0.11 mm**: the declared tolerances permit interference. The audit therefore records `H6-SMA-FINISHED-THICKNESS-FIT` as `requires_confirmation`, blocking production release while routing continues. It does not assume that bending the brass prongs is an acceptable assembly operation.

Before H6.0.9 acceptance, obtain a supplier-supported fit: either factory confirmation of a finished-thickness range compatible with the exact slot and declared clearance, or documented GCT/factory acceptance of the full current tolerance range. JLCPCB invites finished-thickness requirements in the order notes or stack-up drawing, but a tighter standard thickness tolerance has not been verified. The selected stack, MPNs and fabrication authorization remain unchanged.

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

## Scope of the earlier H6.0.1 result

The [microcoax service result](h6-r2-microcoax-service.md) covers nominal corridors, relaxed length and 2D keepouts; it does not close the reopened holder/contact findings. Current H6.0.3 continues routing. Assembled opposing-body clearance and all Ebyte source-position envelopes still require verification in H6.0.7.

## Reproduce

```bash
python3 hardware/layout/h6_r2_mechanical_stack.py --check
```

Expected result:

```text
H6-R2 mechanical stack review_required: 4 axes; 2 NTC XY placements; thermal contact unverified; 2.18 mm minimum nut thread; 0.38 mm tip clearance; SMA fit requires_confirmation
```

`--check` verifies reproduction of this open report. Add `--require-release-ready` to reject the still-open release gates (exit 2).
