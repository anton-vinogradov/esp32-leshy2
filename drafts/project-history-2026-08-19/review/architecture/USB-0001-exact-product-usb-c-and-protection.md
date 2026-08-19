# USB-0001 — exact product USB-C receptacle and four-line protection

- Статус: **Проведено ревью бумажной принципиальной схемы**
- Дата: 2026-08-18
- Dependency step: [`INT-0001/I4`](INT-0001-internal-design-closure-sequence.md)
- Finding: [`FND-0087`](../findings/FND-0087-product-usb-ended-on-abstract-port.md)
- Decision: [`DEC-0083`](../decisions/DEC-0083-exact-protected-product-usb-port.md)
- Propagation review: [`REV-0005AN`](../reviews/REV-0005AN-product-usb-port-propagation.md)

## Boundary

This pass closes the first I4 paper endpoint: one externally accessible
sink-only product USB-C port carrying native S3 USB2 and the accepted
TPS25751D power-input path. It selects the exact receptacle, connector-side
CC/data protection, support passives, complete real-contact route and a test
boundary. It does not close placement, enclosure, USB2 signal-integrity or
destructive port HIL and does not authorize KiCad.

## Exact physical instances

| Role | Qty | Exact MPN | Reviewed use |
|---|---:|---|---|
| product receptacle | 1 | `JAE DX07S016JA1R1500` | 16-contact right-angle USB Type-C/USB2 receptacle; 10,000-cycle class, four through-hole shell locks |
| four-line port protector | 1 | `Texas Instruments TPD4S201RUKR` | connector-side CC1/CC2 and USB2 D+/D- 28-V short-to-VBUS plus IEC ESD protection |
| S3 USB data series resistors | 2 | `Panasonic ERJ-2RKF22R0X` | 22 Ohm ±1%, 0402; one each in D+ and D-, close to S3 |
| protector VBIAS | 1 | `TDK C1608X7S2A104K080AB` | 100 nF, 100 V, X7S, 0603 |
| protector VPWR | 1 | `TDK C1608X7R1C105K080AC` | 1 uF, 16 V, X7R, 0603 |
| protector FLT pull-up | 1 | `Yageo RC0402FR-0710KL` | 10 kOhm to TPS `LDO_3V3` |
| protected CC shunts | 2 | `Murata GRM1555C1H221JA01D` | 220 pF ±5%, 50 V, C0G, 0402; one per controller-side CC line |

The connector and protector are new exact BOM lines. VPWR and FLT reuse
existing exact lines; VBIAS, the smaller CC value and the 22-Ohm termination
add inexpensive passive lines. Two 0402 shunt-capacitor positions are reserved
at the S3 side and initially remain DNP, so they are neither populated parts
nor false exact-MPN commitments before measured tuning.

## Complete route

| Receptacle contacts | Protected destination | Rule |
|---|---|---|
| A4/A9/B4/B9 VBUS | existing `TVS2200DRVR`, TPS25751D `VBUS` and `VBUS_IN` | raw input only; accepted PDOs remain 5 V/3 A, 9 V/3 A and 15 V/2 A; no source/power-bank role |
| A1/A12/B1/B12 GND | local entry-zone power return | every physical ground contact is soldered; TVS/protector returns stay short |
| shell locks | entry-zone chassis/ESD structure | final chassis-to-power-ground network is a placement/HIL gate |
| A5 CC1 | TPD `C_CC1` → `CC1` → TPS CC1 | `RPD_G1` loops to connector-side `C_CC1` for dead-battery attach |
| B5 CC2 | TPD `C_CC2` → `CC2` → TPS CC2 | `RPD_G2` loops to connector-side `C_CC2` |
| A6+B6 D+ | TPD `C_SBU1` → `SBU1` → `ERJ-2RKF22R0X` → S3 GPIO20 | exact initial 22-Ohm series termination; one nearby 0402 shunt position remains DNP |
| A7+B7 D- | TPD `C_SBU2` → `SBU2` → `ERJ-2RKF22R0X` → S3 GPIO19 | native S3 USB Full-Speed/Serial-JTAG path remains dedicated; second shunt position remains DNP |
| A8/B8 SBU | no-connect | no DisplayPort, audio-adapter or other Type-C Alt Mode claim |

All TPD ground contacts and exposed pad terminate locally. Pins 16/17/19/20
remain datasheet NC. `VPWR` is fed from autonomous TPS `LDO_3V3` and bypassed
by 1 uF. `VBIAS` receives 100 nF/100 V. Open-drain `FLT` is pulled to the same
local rail and routed to `TP_USB_PROTECTOR_FAULT_N`; it is deliberately not
tied to the unpowered main-domain interrupt and consumes no scarce GPIO.

## CC capacitance correction

The previous 330-pF shunts were selected before a connector-side protection
device existed. The reviewed published-value screen per CC line is now:

| Contribution | Paper value |
|---|---:|
| exact external C0G, including ±5% | 209…231 pF |
| TPS25751 receiver input | 120 pF published value |
| TPD4S201 protected CC channel | 40…120 pF |
| subtotal before connector/route parasitics | **369…471 pF** |
| remaining distance to 600-pF receiver ceiling | **at least 129 pF** |

The 220-pF part remains comfortably above the 200-pF receiver minimum even at
the low published corner once TPS/protector capacitance is present. The board
must still measure the complete CC line because the table is not a tolerance
model for the TPS input, connector or layout.

## USB2 and fault behavior

ESP32-S3 GPIO19/20 provide native USB **Full-Speed, 12 Mbit/s**; they are not a
480-Mbit/s High-Speed PHY. Espressif recommends initial 22/33-Ohm series
resistors close to the chip/module and reserved shunt-capacitor footprints,
initially DNP. This design instantiates two exact 22-Ohm parts and reserves the
two tuning positions without pretending that unmeasured capacitors are BOM.

TPD4S201 specifies at least 600-MHz bandwidth for its USB2-capable protected
channels, 6-pF channel capacitance and 4-Ohm typical/6.8-Ohm maximum on
resistance. That is ample on paper for the S3 Full-Speed PHY, but protector,
termination, route and return geometry still require assembled enumeration,
RC/signal-integrity and fault HIL. A failure reopens resistor/capacitor values,
placement or the protector split; it does not authorize removing protection.

The protector opens CC/data paths on connector overvoltage and exposes `FLT`.
Firmware treats detach, PD-controller fault and failed re-enumeration as the
normal product signal; the fixture test point proves direct FLT timing and
recovery. There is no firmware bypass and no automatic repeated USB reset loop.

## Availability and cost screen

Both active parts were checked against manufacturer data and visible
authorized-distributor stock on 2026-08-18. `DX07S016JA1R1500` had broad stock
near `$1.23` at 100 pieces. `TPD4S201RUKR` was current and multi-source stocked,
roughly `$0.59…1.25` depending on quantity/reel, while catalog stock at the
preferred one-stop assembler was thinner. With passives, the first quantified
port material is approximately `$1.9…2.6` per board before landed/assembly
cost. Connector and protection were already mandatory unresolved I4 lines, so
this is a quantified implementation rather than a newly added product feature.

Factory-supplied versus consigned TPD4S201 and an electrical alternate remain
I8 sourcing work. Sparse one-stop stock cannot silently replace the protector.

Primary sources:

- [JAE DX07S016JA1R1500 product page](https://products.jae.com/jp/ja/connectors/category/io/dx07-receptacle/dx07s016ja1r1500/)
- [JAE DX07 16-position receptacle brochure](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8440/MB-0350E_DX07_16-POS_RECEPTACLE.pdf)
- [TI TPD4S201 datasheet](https://www.ti.com/lit/gpn/TPD4S201)
- [TI TPD4S201RUKR orderable page](https://www.ti.com/product/TPD4S201/part-details/TPD4S201RUKR)
- [TI TPS25751 datasheet](https://www.ti.com/lit/ds/symlink/tps25751.pdf)
- [Espressif ESP32-S3 hardware-design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/esp-hardware-design-guidelines-en-master-esp32s3.pdf)
- [Panasonic ERJ-2RKF22R0X orderable page](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-2RKF22R0X/1746157)

## Review result

Exact component choice, all exposed contacts, protected routes, reset/dead-
battery behavior, CC paper screen, cost and failure authority receive
**«Проведено ревью»** at paper-schematic level. Exact placement/return network,
enclosure cutout, total CC capacitance, USB Full-Speed RC/signal integrity, ESD,
short-to-VBUS and recovery HIL remain open. I4 continues with the next exact
display/UI/storage endpoint; integrated mockup and KiCad remain blocked.
