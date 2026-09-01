# Controlled display assembly — ER-TFT035IPS-6 + ER-TPC035-6

Status: **selected production route; purchase and fabrication are not
authorized.** This is the deterministic factory-assembly boundary for the sole
prototype. The former `HMX035CTFT-001` donor and `L2-DISP-ADP-001-B` adapter
are rejected historical routes.

## Exact identities

- panel: EastRising `ER-TFT035IPS-6` with `ER-TPC035-6` capacitive touch,
  configured option `5344`, `ILI9488` plus `FT6236`;
- PCB connector: Hirose `FH34SRJ-50S-0.5SH(50)`, JLCPCB `C3169104`, 50
  positions at 0.50-mm pitch, dual-contact, for the exact 0.30-mm stiffener;
- retention: one traceable stocked 50.00 × 50.00-mm double-coated
  acrylic-foam PSA rectangle applied to the component-free UI-PCB outer face;
  the exact production MPN and thickness remain an H5 release gate;
- electrical interface: direct 8-bit i8080 at the exact 20-MHz first-prototype
  limit, with the serial recovery option retained on opened-device jumpers.

## Frozen board geometry

- panel body datum: exact `56.54 × 84.96 mm` outline with `FPC-UP` orientation;
- contact-tongue slot: rounded NPTH `27.00 × 1.20 mm`, board position
  `[24.00, 23.00] mm`;
- inner-face ZIF: envelope `27.00 × 3.80 × 1.00 mm`, board position
  `[24.00, 25.00] mm`;
- PSA datum: one `50.00 × 50.00 mm` outline at `[12.50, 44.46] mm`;
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
- the assembler verifies `1 → 1` and `50 → 50` before closing the latch.

## Deterministic factory sequence

1. Inspect exact panel option, tail, contact side and pin marks against the
   EastRising controlled drawing; reject any substitution.
2. Populate and inspect `C3169104`; keep the ZIF latch open.
3. Clean the released PCB PSA area with the specified process, apply the one
   stock rectangle inside its silkscreen datum and keep its upper liner fitted.
4. Perform the dry fit and record the route length, relaxed reserve and
   `1 → 1` / `50 → 50` orientation.
5. Close the ZIF latch only after the tongue is fully seated and relaxed.
6. Remove the PSA upper liner, align the panel to the `DISPLAY/FPC-UP` datum,
   apply the released pressure/time process and preserve the released dwell.
7. Inspect panel planarity, adhesive coverage, uncompressed FPC pocket and the
   absence of latch or routed-edge load. No power-on factory test is required.

## Open release gates

- measure the current-lot folded FPC maximum stack and bend path;
- select one exact stocked industrial PSA MPN at least `0.20 mm` thicker than
  that measured stack, with a traceable source;
- freeze cleaning, pressure, dwell, storage and rework instructions;
- obtain written quantity-one factory acceptance for customer-supplied panel,
  dry fit, ZIF insertion, PSA application and final device assembly.

The owner performs the first USB power-on and verifies image, backlight and
touch during H7/H8. Batteries are not supplied or installed by the factory.

## Primary sources

- [EastRising product/configuration page](https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen)
- [EastRising ER-TFT035IPS-6 controlled datasheet](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf)
- [Hirose exact FH34SRJ-50S product page](https://www.hirose.com/en/product/p/CL0580-1266-2-50)
- [JLCPCB exact C3169104 route](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104)
