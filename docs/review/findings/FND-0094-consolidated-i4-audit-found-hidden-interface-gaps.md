# FND-0094 — consolidated I4 audit found hidden interface gaps

- Status: **исправлено; Проведено ревью paper electrical boundary**
- Scope: consolidated `I4` display/touch/UI/microSD/product-USB interface block
- Architecture: [`IOX-0001`](../architecture/IOX-0001-consolidated-i4-electrical-closure.md)

## Finding

The individually reviewed I4 endpoints were functionally complete, but their
joint dependency audit found several implementation-significant details still
represented only by prose or `abstract:*` endpoints:

1. `TCA6424ARGJR` had real package contacts in the registry but no fixed
   VCCI/VCCP, bypass, ADDR, RESET, INT, ground or exposed-pad circuit.
2. AON STOP-latch and RF-evidence outputs reached P22/P23 directly. The
   TCA6424A source does not establish a positive partial-power tolerance for
   those P ports, so an AON-high signal could not be assumed safe while
   `3V3_MAIN`/VCCP was off.
3. The pack-admission target occupied SYS_I2C without a fixed address, leaving
   the assembled collision proof incomplete.
4. The microSD DAT0 return ended at a textual GPIO placeholder even though
   real S3 GPIO4 was already allocated.
5. The product USB shield ended at an unproved chassis network, and the
   internal display-FPC ESD boundary was not classified.
6. The physical STOP indicator still used an abstract 2.2-kOhm resistor.
7. Status text incorrectly said that the 24-line main slow plane had no
   reserve, although its machine budget was already `18 used / 6 free`.

None of these findings justified removing a control, radio, interface or
safety feature. They were integration defects in the paper design.

## Correction summary

| Gap | Correction | Functional result |
|---|---|---|
| TCA6424A core | both supplies on protected `3V3_MAIN`; two exact 100-nF bypass capacitors, one exact 1-uF bulk capacitor, ADDR low=`0x22`, grounded GND/EPAD, 10-kOhm RESET_N pull-up/test point and shared open-drain INT | same 24 slow contacts, now electrically instantiable |
| AON → P22/P23 | two separate AON-powered `SN74LVC1G07DCKR` open-drain buffers plus main-domain 10-kOhm pull-ups | STOP and active-low S3 evidence polarity preserved; no positive AON injection into an off VCCP domain |
| pack target | fixed firmware-defined SYS_I2C address `0x2A` | no hardware/cost change; collision proof becomes explicit |
| microSD return | exact `sd_miso_series.END_2 → s3.GPIO4` route | no pin or timing change |
| product USB shell | direct short multi-via bond to local power/ESD ground | removes an invented unresolved chassis domain; layout/HIL still required |
| display FPC | internal, service-only, no live insertion; reopen if mechanics expose it | no extra base-BOM ESD array without a real external boundary |
| STOP LED | exact `RC0402FR-072K2L` | same independent physical indication |
| reserve text | main slow plane `18/0/6`; UI P7 is a protected fixture/growth pad | full D-pad, PTT, STOP, F1 and F2 remain explicitly present |

## Remaining evidence, not paper uncertainty

HIL must still prove the TCA6424A identity/defaults/400-kHz timing, same-rail
startup, full power-cycle recovery below 0.2 V, shared interrupt behavior and
P22/P23 polarity/no-back-power states. Product USB return geometry, display
FPC accessibility, shared display/storage signal integrity and the complete
assembled I2C address scan remain prototype/layout evidence. Audio, receiver,
voice and external-accessory endpoint circuits remain owned by I5/I6/I7.

No KiCad authorization or product-mechanical freeze follows from this review.

## Primary source

- [TI TCA6424A primary datasheet](https://www.ti.com/lit/ds/symlink/tca6424a.pdf)
- [TI TCA6424ARGJR exact part page](https://www.ti.com/product/TCA6424A/part-details/TCA6424ARGJR)
