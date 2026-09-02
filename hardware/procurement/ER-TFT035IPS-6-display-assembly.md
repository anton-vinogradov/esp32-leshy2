# Controlled display assembly — ER-TFT035IPS-6 + ER-TPC035-6

Status: **selected production route; purchase and fabrication are not
authorized.** This is the deterministic owner-assembly boundary for the sole
prototype. The former `HMX035CTFT-001` donor and `L2-DISP-ADP-001-B` adapter
are rejected historical routes.

## Exact identities

- panel: EastRising `ER-TFT035IPS-6` with `ER-TPC035-6` capacitive touch,
  configured option `5344`, `ILI9488` plus `FT6236`;
- PCB connector: Hirose `FH34SRJ-50S-0.5SH(50)`, JLCPCB `C3169104`, 50
  positions at 0.50-mm pitch, dual-contact, for the exact 0.30-mm stiffener;
- retention qualification line: 3M (TC) `4910SQ-2(5)`, DigiKey
  `1067-4910SQ-2(5)-ND`, one ready-made `50.80 × 50.80 × 1.016 mm`
  VHB 4910 square applied to the component-free UI-PCB outer face; it is an
  exact stocked candidate, but release still depends on the current-lot
  folded-FPC height and owner dry fit before bonding;
- electrical interface: direct 8-bit i8080 at the exact 20-MHz first-prototype
  limit, with the serial recovery option retained on opened-device jumpers.

## Frozen board geometry

- panel body datum: exact `56.54 × 84.96 mm` outline with `FPC-UP` orientation;
- contact-tongue slot: rounded NPTH `27.00 × 1.20 mm`, board position
  `[24.00, 23.00] mm`;
- inner-face ZIF: envelope `27.00 × 3.80 × 1.00 mm`, board position
  `[24.00, 25.00] mm`;
- PSA datum: one `50.80 × 50.80 mm` outline at `[12.10, 44.46] mm`;
- the upper FPC pocket remains free of adhesive, parts, vias, test points,
  silkscreen and copper-height steps.

The complete mechanical source and machine checks live in
[`display-mount.json`](../product-design/display-mount.json). The public
assembly drawing is
[`display-mount.svg`](../../docs/images/display-mount.svg).

## Mandatory received-panel dry fit

Keep the PSA upper liner installed. Rotate the panel into the released
`FPC-UP` orientation, make exactly one 180-degree fold and no twist, pass only
the narrow contact tongue through the rounded slot and insert it fully into the
open ZIF.

The minimum source tail is `29.66 mm` after the drawing tolerance. Measure the
actual neutral-axis route from the panel exit to the connector contact stop:
it must be at most `24.66 mm`, leaving at least `5.00 mm` of relaxed reserve.
The tail must show a free bow and must not pull the latch, touch a routed edge
or be compressed by the PSA/panel stack.

Pin orientation is not inferred from the dual-contact connector:

- after the released in-plane panel rotation and the single fold, tail pin 1
  is at board/world X-min and tail pin 50 at X-max;
- the connector footprint must put pin 1 at world X-min and pin 50 at X-max;
- the owner verifies `1 → 1` and `50 → 50` before closing the latch.

## Deterministic owner sequence

1. Inspect exact panel option, tail, contact side and pin marks against the
   EastRising controlled drawing; reject any substitution.
2. Populate and inspect `C3169104`; keep the ZIF latch open.
3. Clean the released PCB PSA area with the process below, apply the one exact
   stock square inside its silkscreen datum and keep its upper liner fitted.
4. Perform the dry fit and record the route length, relaxed reserve and
   `1 → 1` / `50 → 50` orientation.
5. Close the ZIF latch only after the tongue is fully seated and relaxed.
6. Remove the PSA upper liner, align the panel to the `DISPLAY/FPC-UP` datum,
   apply the released pressure/time process and preserve the released dwell.
7. Inspect panel planarity, adhesive coverage, uncompressed FPC pocket and the
   absence of latch or routed-edge load, then perform owner USB bring-up.

## Exact stock-pad evidence

Checked `2026-09-01`:

| field | controlled value |
|---|---|
| manufacturer / MPN | 3M (TC) `4910SQ-2(5)` |
| distributor line | DigiKey `1067-4910SQ-2(5)-ND` |
| physical form | ready-made `50.80 × 50.80 × 1.016 mm` square; no trimming or converter order |
| live distributor state | active; 16 line items in stock; displayed quantity-one price `$22.12` |
| material | clear double-coated acrylic foam, 3M VHB 4910 family |
| nominal tolerance | `1.016 mm`; official 4910 family thickness tolerance `±10%` |
| fail-closed minimum | `0.914 mm`; therefore folded-FPC maximum `≤0.714 mm` for the mandatory `0.20 mm` clearance |
| JLCPCB Standard surface | no exact `4910SQ-2(5)` or 3M 4910 public result; handle as a customer-supplied `J4-F` consumable, not an invented JLC/LCSC part |

Untraceable marketplace `50 × 50 mm` 3M-labelled pads are rejected: they do
not carry this exact controlled line. The official 50-mm `4910F50` roll
(`3M ID 7000072293`) is real but is also rejected for the one prototype because
it costs hundreds of euros and still requires cutting.

## Released 4910 application process

This process follows the official 3M 4910 data sheet and VHB surface-preparation
guidance. It does not override an EastRising panel pressure limit; the owner
must use a flat support/roller arrangement that cannot point-load the glass.

1. Condition the PCB, panel and pad at `21…38 °C`.
2. Clean both bond faces with fresh lint-free wipes and `70% IPA / 30% water`:
   one wet wipe followed immediately by one dry wipe. Let both surfaces become
   visibly dry. Do not add primer, abrasion or an unqualified solvent.
3. Place the pad on the PCB inside the PSA datum. With the upper liner still
   fitted, apply at least `100 kPa` uniformly over the complete pad using a
   supported roller or platen; no point load may reach the panel or FPC.
4. After the dry fit, ZIF insertion and orientation record, peel the upper
   liner, place the panel once and apply at least `100 kPa` through a flat
   fixture supported directly beneath the bonded PCB region. The fixture may
   not bend the PCB, press the adhesive-free FPC zone or concentrate load on
   the active glass. If this fixture is unavailable, stop rather than hand-
   pressing the display.
5. Keep the assembly flat and unloaded at room temperature. Allow at least
   `24 h` before packing and `72 h` before owner handling; 3M states that the
   bond reaches approximately 90% at 24 h and 100% at 72 h.

For the `2580.64 mm²` square, `100 kPa` corresponds to about `258 N` total.
That is why a distributed, backed fixture is mandatory rather than finger
pressure on the display.

## Open release gates

- measure the current-lot folded FPC maximum stack and bend path;
- prove folded-FPC maximum `≤0.714 mm` and actual dry-fit clearance `≥0.20 mm`
  with the received `4910SQ-2(5)`; otherwise select a thicker traceable stock
  rectangle and repeat this review;
- prove the dry-fit image/backlight/touch path before removing the upper liner;
- complete the exact M2.5 nonconductive fastener and 11.00-mm compression-stop
  kit used after the display, cables and knob are installed.

The owner performs USB power-on and verifies image, backlight and touch during
H7/H8 before the irreversible PSA bond where practical, then repeats it after
bonding and enclosure assembly. Batteries are separately sourced and installed.

## Primary sources

- [EastRising product/configuration page](https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen)
- [EastRising ER-TFT035IPS-6 controlled datasheet](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf)
- [Hirose exact FH34SRJ-50S product page](https://www.hirose.com/en/product/p/CL0580-1266-2-50)
- [JLCPCB exact C3169104 route](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104)
- [DigiKey exact 4910SQ-2(5) stock line](https://www.digikey.com/en/products/detail/3m-tc/4910SQ-2-5/3339259)
- [3M VHB 4910 technical data sheet](https://multimedia.3m.com/mws/media/2366536O/3M-VHB-Tape-Specialty-Tape-4910.pdf)
- [3M VHB surface preparation](https://www.3m.com/3M/en_US/bonding-and-assembly-us/resources/full-story/?storyid=b3996cbd-9954-455f-8e72-88e452ca38c0)
