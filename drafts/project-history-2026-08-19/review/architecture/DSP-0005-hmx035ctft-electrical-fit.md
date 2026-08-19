# DSP-0005 — HMX035CTFT-001 exact electrical-fit review

> Amended by `DEC-0086/UI-0001` and then `DEC-0088/DSP-0007`: TP_INT now
> reaches shared GPIO37 through a fixed active-low open-drain normalizer;
> GPIO39 is encoder phase A. Exact integrated controller is ST77922 at address
> 0x38; the former controller/polarity uncertainty is closed on paper.
> The dedicated UI expander also makes the later `24/0/0` slow-plane statement
> historical; current main slow accounting is `21/0/3` after I5.
> The panel contact map and QSPI/reset conclusions below remain valid.

- Статус: **Проведено ревью paper electrical fit; sourcing/mechanics/HIL открыты**
- Дата: 2026-08-17
- Class decision: [`DEC-0053`](../decisions/DEC-0053-new-35in-qspi-display-class.md)
- Machine source: [`devices.json`](../../../hardware/architecture/devices.json) /
  [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)
- Findings: [`FND-0063`](../findings/FND-0063-hmx035ctft-mpn-was-disclosed.md),
  [`FND-0064`](../findings/FND-0064-stale-s3-budget-in-stage-ledger.md)
- Review: [`REV-0005A`](../reviews/REV-0005A-hmx-display-electrical-fit.md)
- Exact endpoint amendment: [`DSP-0006`](DSP-0006-exact-display-rail-backlight-and-mate-profile.md) /
  [`DEC-0084`](../decisions/DEC-0084-exact-protected-display-electrical-endpoint.md)

> `DSP-0006/DEC-0084` later close the exact paper power, reset, backlight and
> first-connector circuit. Standalone panel procurement and physical mate HIL
> remain open; this original contact-fit review is otherwise unchanged.
> `DSP-0008/BOM-0010/REV-0005BI` later prove complete-board donor/specimen
> availability and record the standalone RFQ/no-drop-in boundary; they do not
> claim raw-panel production orderability.

## Результат

Официальная схема QDtech `ES3C35P` раскрывает exact display/touch assembly
`HMX035CTFT-001` и все 40 контактов. Его QSPI+I2C path полностью ложится на
текущую карту без нового GPIO:

- `TP_INT` joins shared S3 `GPIO37/SYS_INT_N` through exact 10-kOhm raw pull-up
  and fixed `SN74LVC1G07DCKR`; active level is low;
- S3 `GPIO6` остаётся free;
- S3 `GPIO43` остаётся free и может получить `TE` только после HIL A/B;
- display reset и touch reset уже были на `TCA6424ARGJR P06/P07`;
- display itself preserves S3 `31/3/2` and the then-current slow `23/1/0`;
  later `AUDIO-0002/FND-0067` used P27 for RX-audio selection, making the
  pre-`DEC-0086` slow accounting `24/0/0` without changing display fit.

Это проводит ревью **paper contact fit**, но не принимает assembly в production
BOM. `DSP-0006/DEC-0084` now add exact connector candidate and backlight/power
circuit; standalone ordering/drawing/lifecycle, final mate, optics and specimen
measurements remain open.

## Exact assembly and controller identifiers

- Display/touch assembly marking: `HMX035CTFT-001` in the official QDtech
  schematic; the marking is not proof that QDtech manufactures the assembly.
- Primary complete HIL board identifiers: Elecrow `DLE06235B`, QDtech
  `ES3C35P`.
- Exact integrated display/touch TDDI: Sitronix `ST77922`.
- Firmware component reference: `espressif/esp_lcd_st77922`.
- Separate touch-controller MPN: not applicable; ST77922 itself contains the
  capacitive-touch controller.
- Exact touch bus: I2C 7-bit address `0x38`, maximum 400 kHz.

## Exact 40-contact register

### Touch and supplies: contacts 1–8

- `1 TP_I2C_SCL` → S3 `GPIO2/SYS_I2C_SCL`.
- `2 TP_I2C_SDA` → S3 `GPIO1/SYS_I2C_SDA`.
- `3 TP_INT` → 10-kOhm raw pull-up → fixed non-inverting open-drain
  `SN74LVC1G07DCKR` → shared S3 `GPIO37/SYS_INT_N`.
- `4 TP_RESXP` → normalized `TP_RESET` → slow I/O `P07/TOUCH_RST_N`.
- `5 GND` → qualified display ground.
- `6 VDDI` → qualified 3.3 V display rail.
- `7 VDD` → qualified 3.3 V display rail.
- `8 TE` → unconnected in current map; optional HIL probe to free `GPIO43`.

### QSPI/control: contacts 9–18

- `9 CS` → S3 `GPIO38/LCD_CS_N`.
- `10 RS` → QSPI `D1` → S3 `GPIO4/DISPLAY_SD_SPI_D1`.
- `11 WR` → QSPI clock → S3 `GPIO35/DISPLAY_SD_SPI_SCK`.
- `12 RD` → unused in reviewed QDtech QSPI reference.
- `13 SDA` → QSPI `D0` → S3 `GPIO36/DISPLAY_SD_SPI_D0`.
- `14 NC` → no connection.
- `15 RESET` → slow I/O `P06/LCD_RST_N`.
- `16 GND` → qualified display ground.
- `17 DB0` → QSPI `D2` → S3 `GPIO41/LCD_QSPI_D2`.
- `18 DB1` → QSPI `D3` → S3 `GPIO42/LCD_QSPI_D3`.

### Parallel-data straps and NC: contacts 19–32

- `19 DB2`, `20 DB3`, `21 DB4`, `22 DB5`, `23 DB6`, `24 DB7` → GND,
  matching the official QSPI reference.
- `25…32` → NC.

### Backlight and interface straps: contacts 33–40

- `33 LEDA` → qualified backlight supply.
- `34 LEDK`, `35 LEDK`, `36 LEDK` → one qualified dimmable current sink.
- `37 GND` → qualified display ground.
- `38 IM0` → GND.
- `39 IM1` → 3.3 V.
- `40 IM2` → GND.

## Shared display/microSD consequence

The screen uses QSPI `D0…D3`; microSD uses the same SPI2 clock/D0/D1 with a
separate CS. The exact machine contract therefore requires:

- display and SD specimens high-Z whenever their CS is inactive;
- explicit per-device bus mode/clock switching;
- QSPI only while SD CS is high;
- non-preemptible display occupancy `<=1 ms`;
- no radio FIFO or S3↔RP/C5 IPC deadline on this controller.

The exact contacts fit, but only an oscilloscope/contention test can close this
shared-bus gate.

## Backlight reference — evidence, not production freeze

QDtech's reference board uses:

- MOSFET `BSS138` (`Q4`);
- series resistor `R33 = 10 Ω` in the LEDK path;
- `R31 = 0 Ω` from `LCD_BL` to the gate;
- gate pulldown `R32 = 10 kΩ`;
- LEDA tied to 3.3 V.

This is useful HIL evidence, but it does not prove regulated current, target
brightness, thermal margin or low-EMI dimming. Production backlight source/
sink therefore remains an exact-part electrical gate.

## Touch reference

The official board places `10 kΩ` pull-ups `R29/R30` on touch SDA/SCL and
`C50 = 100 nF` (`104`) decoupling. `DEC-0084` deliberately does not copy those
pull-ups: the complete Leshy2 SYS_I2C already has one exact 2.2-kOhm pair.
The exact assembly specification publishes address `0x38` and active-low
TP_INT; `DEC-0088` adds a distinct exact 10-kOhm pull-up on the raw interrupt,
not another I2C pull-up. Rise time and touch pulse/clear behaviour remain HIL.

## Connector candidate — electrically instantiated, mechanical acceptance open

Hirose `FH12-40S-0.5SH(55)`, CL `CL0586-0527-7-55`, is an active 40-position,
0.5-mm-pitch, 2.0-mm-height bottom-contact ZIF candidate. It matches the coarse
Waveshare/QDtech connector class. `DEC-0084` instantiates it as the exact first
paper connector candidate, but it is **not yet the final Leshy2 mate or frozen
footprint**.

Before acceptance, a real `HMX035CTFT-001` sample or manufacturer drawing must
prove FPC thickness, exposed-contact side, tail geometry, insertion direction,
stiffener and keepout. A generic «40 pin 0.5 mm» match is insufficient.

## Secondary HIL markings

The official Waveshare `ESP32-S3-Touch-LCD-3.5B` schematic exposes assembly
markings `HXR35014C30` and `HXR35014C30_TOUCH`, controller `AXS15231B`, and a
generic `40 pin / 0.5 mm / back-flip / 2.0H` connector description. These are
secondary-HIL identifiers, not interchangeable target parts.

## Rejected near-matches

- Tailor Pixels `TTH348BVT-01CG`: `3.48 inch` but `172×640`, not target
  `320×480`; rejected before shortlist.
- Shenzhen KD Startek `KD035QVFID225-C086A`: `3.5 inch 320×480`, but MIPI
  interface rather than direct QSPI; rejected.
- OPL product `226`: advertised `3.5 inch 320×480 AXS15231B QSPI`, but exact
  manufacturer MPN/drawing/lifecycle is absent; inquiry lead only.

## HIL/qualification gates

1. Obtain one exact `DLE06235B/ES3C35P` board and preferably one raw
   `HMX035CTFT-001`; photograph markings and FPC tail.
2. Measure FPC pitch/thickness/contact side and qualify the exact connector.
3. Verify rail sequencing, reset timing, exact `0x38` identity/readback and
   active-low IRQ idle/pulse/hold/clear behaviour.
4. Validate vendor init, rotation, partial windows, sleep/wake and long-run
   image integrity.
5. Prove both display and microSD CS-high high-Z, no back-power/contention,
   `<=1 ms` display slices, menu first-visible `<=100 ms`, SD `>=4.0 MB/s`,
   1.5 MB/s recording and 250-ms card-stall behaviour.
6. Measure backlight current, brightness, thermals and PWM/EMI coupling.
7. Compare TE disconnected versus S3 `GPIO43`; assign the pin only if measured
   tearing/latency improvement justifies losing a free GPIO.
8. Qualify production orderability, lifecycle, second source, optics and cover
   lens before BOM/KiCad freeze.

## Primary sources

- [QDtech ES3C35P official schematic](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf)
- [Elecrow/QDtech DLE06235B/ES3C35P specification](https://www.elecrow.com/download/product/DLE06235B/3.5inch_IPS_ESP32-S3_Specification.pdf)
- [Hirose FH12-40S-0.5SH(55)](https://www.hirose.com/en/product/p/CL0586-0527-7-55)
- [Waveshare 3.5B official schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-3.5B/ESP32-S3-Touch-LCD-3.5B-Schematic.pdf)
- [KD Startek KD035QVFID225-C086A](https://en.tft-tft.com/product/detail?id=1188)
- [OPL product 226](https://www.opldisplaytec.com/product/226)
