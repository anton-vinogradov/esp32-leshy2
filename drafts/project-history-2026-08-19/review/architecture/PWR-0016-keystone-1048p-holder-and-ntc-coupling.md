# PWR-0016 — exact polarized holder and three-NTC coupling contract

- Статус: **Проведено ревью бумажной механико-электрической схемы**
- Дата: 2026-08-18
- Decision: [`DEC-0077`](../decisions/DEC-0077-keystone-1048p-qualified-cell-profile.md)
- Corrected finding: [`FND-0081`](../findings/FND-0081-holder-contact-and-thermal-proof-gap.md)
- Propagation review: [`REV-0005AH`](../reviews/REV-0005AH-battery-holder-and-ntc-coupling.md)

## Boundary

This pass closes the paper choice that `DEC-0062` deliberately left open:
mechanical polarity before contact, an exact dual-cell holder envelope and a
physical coupling rule for all three accepted `B57332V5103F360` sensors. It
did not yet select the final cell MPN, enclosure door or thermal-interface
material and does not replace specimen continuity, insertion-cycle or thermal
HIL. `PWR-0018/DEC-0079` subsequently select the exact first cell target.

## Exact holder facts

The accepted prototype and production reference is `Keystone Electronics
1048P`:

- exact dual-18650, open, SMT holder;
- manufacturer-described as polarized to preserve continuity and circuit
  protection against improper installation;
- specifically intended for longer 18650 cells with built-in protection;
- `86.0 × 39.8 mm` plan envelope from the manufacturer holder drawing;
- four separately visible metal contact/tab positions in the dual-cell pad
  layout and product image; the PCB, not an internal holder link, creates the
  supervised 2S topology;
- high-temperature Nylon 46, UL 94 V-0 body and gold-flash stainless contacts.

The manufacturer drawing does not assign electronic pin numbers. The machine
source therefore uses functional physical names `SLOT0_POS`, `SLOT0_NEG`,
`SLOT1_POS` and `SLOT1_NEG`; it does not invent pad numbers. Before footprint
freeze, a received specimen must pass four-terminal continuity/isolation and
polarity-orientation tests against the drawing and molded marks. Any hidden
cross-link or orientation mismatch rejects the lot and reopens this decision.

## Cell compatibility and logistics

The base product supports only exact, qualified, protected button-top 18650
MPNs whose length, diameter, protection-current limit, charge current,
chemistry and authenticity path pass I8. A raw flat-top cell is deliberately
unsupported even if it can be forced physically into a generic 18650 volume.
Firmware admission can reject electrical abnormalities, but two terminals
cannot prove cell identity or turn an unknown cell into a qualified one.

Cells are a separately supplied regional kit by default. This keeps lithium
transport certification and regional carrier restrictions outside ordinary
PCBA/antenna factory kitting. The target product documentation still lists the
supported exact cell set; “cells not bundled” must not become “any cell works”.

## Four-contact 2S routing

The holder remains one physical part but exposes four independent circuit
endpoints:

1. slot-0 negative enters local pack ground;
2. slot-0 positive passes its own `0451005.MRL` and reaches the supervised 2S
   midpoint;
3. slot-1 negative reaches that same midpoint only through PCB copper;
4. slot-1 positive passes the other `0451005.MRL` and reaches stack positive.

This preserves separate fuse evidence, midpoint/full-stack ADC evidence and
MAX17320 cell taps. A reversed cell must remain open mechanically before any
of these nets is energized. The admission controller is a second safety layer,
not the mechanism that makes reverse insertion acceptable.

## Three physical NTC contacts

All three sensors are separate physical `B57332V5103F360` instances. The
accepted coupling geometry is:

- `PACK_NTC0`: a dedicated PCB/flex spring tongue through an open holder
  window, electrically insulated from and compliantly pressed to the middle
  third of cell 0's can;
- `PACK_NTC1`: the same independent geometry for cell 1;
- charger `TS`: exactly one populated sensor on one of two indexed tongue
  sites, installed on the thermally worst slot after placement analysis and
  confirmed by the charge/load thermal matrix.

The tongue/coverlay/foam stack is mechanical structure, not a fourth sensor.
It must tolerate ordinary cell removal without adhesive on the replaceable
cell. The insulation covers the NTC terminations as well as the ceramic body;
spring force cannot dent the can, unseat a cell or defeat the holder's
polarity feature.

MAX17320 therefore receives direct temperature evidence for both cells, while
BQ25798 retains an independent non-ignored hardware charge-temperature gate.
If different HIL scenarios make different slots thermally worst and neither
single indexed location bounds both, the one-sensor BQ path must be reopened;
software is not allowed to declare one location representative.

## Updated physical fit

The exact holder replaces the old `40 × 78 mm` volume placeholder in the
bounded rear-fit generator:

| Check | Result |
|---|---:|
| board | `75 × 150 mm` |
| exact holder projection | `39.8 × 86.0 mm` at `(17.6, 40.0)` |
| lower board margin | `24.0 mm` |
| U214-to-holder plan gap | `9.719 mm` |
| U214 rear protrusion | `15.11 mm` |
| holder + installed-cell reference envelope | `20.7 mm` |
| paper rear-depth reserve | `5.59 mm` |

The longer holder still fits and does not move or overlap the accepted U214
dock. The installed envelope improves the old bare-cell-only depth screen, but
wall, door, tolerance, hand access and exact-cell geometry remain mechanical
HIL. Updating this bounded fit artifact does not resume the integrated product
mockup before internals close.

## Cost and cost-down boundary

Authorized-distributor pricing visible on 2026-08-18 is about `$8.57` at 100
pieces (`$9.00` at 25). That is material, so it is recorded rather than hidden
inside an unspecified holder line. A later molded compartment with discrete
contacts is a valid I8 cost-down candidate only if it reproduces pre-contact
polarity blocking, four independent contacts, retention, sensor windows,
replacement life and all HIL results. A cheap non-polarized holder plus
software/electronic reverse detection is not an equivalent cost reduction.

## Sources

- [Keystone exact `1048P` product page](https://www.keyelco.com/product.cfm/product_id/13959)
- [Keystone M65 p27 holder drawing](https://www.digikey.com/htmldatasheets/production/1298968/0/0/1/18650-lithium-ion-battery-holders.pdf)
- [Mouser authorized stock and pricing](https://www.mouser.com/ProductDetail/Keystone-Electronics/1048P?qs=9%252Bwcgl%2FJqd1h8Vx3IFpTxA%3D%3D)
- [TDK exact NTC product page](https://product.tdk.com/en/search/sensor/ntc/chip-ntc-thermistor/info?part_no=B57332V5103F360)

## Review result

Exact holder identity, plan/depth envelope, four independent functional
contacts, protected-button-top compatibility boundary and all three NTC
coupling roles receive **«Проведено ревью»** at paper level. The exact cell is
now selected by `DEC-0079`; its certification/specimen fit, thermal-stack MPNs,
enclosure door, continuity/orientation, insertion cycling, sensor compression/
open/short/lift and thermal response remain HIL gates.
No KiCad start is authorized.
