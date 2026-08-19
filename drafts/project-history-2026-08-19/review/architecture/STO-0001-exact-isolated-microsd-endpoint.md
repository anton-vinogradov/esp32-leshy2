# STO-0001 — exact isolated microSD endpoint

- Status: **Проведено ревью paper electrical endpoint; physical/media/HIL open**
- Finding: [`FND-0089`](../findings/FND-0089-microsd-endpoint-was-backpowered-and-unprotected.md)
- Decision: [`DEC-0085`](../decisions/DEC-0085-exact-isolated-microsd-electrical-endpoint.md)
- Machine source: `hardware/architecture/devices.json` and
  `hardware/architecture/candidates/G2F-3I.json`

## Reviewed boundary

The endpoint is removable SPI-mode microSD on the only scheduled S3 SPI2 pair
with the QSPI display. It must be electrically absent while unused, must not
back-power either domain, and must not make radio service wait: radio owners and
inter-domain links remain physically independent.

The exact socket is active Hirose `DM3AT-SF-PEJM5`: push-push, top-board mount,
13.85 × 15.95 × 1.68 mm, 0.5-A contact rating, eight card contacts, shield and
a normally-open insertion switch that closes when a card is present. Current
manufacturer catalog and authorized-distributor stock were rechecked on
2026-08-18.

## Exact physical parts

| Function | Exact MPN | Reviewed role |
|---|---|---|
| socket | `Hirose DM3AT-SF-PEJM5` | eight card contacts, shield and normally-open detect pair |
| power switch | `TI TPS22919DCKR` | controlled rise, short/thermal protection and QOD discharge |
| host-to-card isolation | `SN74LVC3G34DCUR` | three Ioff buffers for SCK, CMD/MOSI and card CS |
| card-to-host isolation | `TI SN74LVC1G125DCKR` | Ioff DAT0/MISO return with active-low output enable from `SD_CS_N` |
| socket ESD | 2 × `TI TPD4E05U06DQAR` | eight 0.5-pF channels, ±12-kV IEC contact protection |
| switched-card bulk | `Murata GRM21BR60J226ME39L` | 22 uF, 6.3 V, X5R, 0805 |
| input bypass | `TDK C1608X7R1C105K080AC` | 1 uF on protected main side of the load switch |
| local/buffer/filter bypass | 4 × `TDK C1005X7R1H104K050BB` | card rail, two logic packages and card-detect filter |
| reset/card pulls | 12 × `Yageo RC0402FR-0710KL` | power-off, bus-idle, display/card CS and CMD/DAT0…DAT3 defaults |
| source damping | 4 × `Panasonic ERJ-2RKF22R0X` | 22 Ohm at card-side buffer outputs and MISO return output |
| detect input protection | `Yageo RC0603FR-071KL` | 1-kOhm series resistor before slow-I/O P21 |

The incremental material cost excluding the already-selected socket is
approximately USD 0.75…1.00 at quantity 100. The two ESD arrays dominate; the
correction consumes no GPIO and is accepted as a non-dramatic cost improvement.

## Power and isolation topology

Protected `3V3_MAIN` feeds the existing `TPS22919DCKR` through the exact 1-uF
input capacitor. TCA6424 P20 controls `ON`; a separate 10-kOhm pull-down keeps
the rail off while the expander is reset or absent. `VOUT` creates
`SD_CARD_3V3`, supplies the socket and both buffers, and has 22-uF plus 100-nF
local energy. `QOD` connects directly to `VOUT`; firmware waits the discharge
interval established by HIL because no separate card-rail ADC is allocated.

The host can drive the three buffer inputs while their supply is off because
the selected LVC devices support partial-power-down Ioff behavior. Their
card-side outputs do not feed an unpowered socket. DAT0 reaches the host only
through `SN74LVC1G125DCKR`; its `OE_N` is the same host-side `SD_CS_N`, making
the return high-impedance during every display QSPI D1 interval. When card
power is absent, Ioff preserves that high-impedance state independently of CS.

## Pulls, damping and ESD

Espressif requires 10-kOhm pull-ups on CMD and all DAT0…DAT3 conductors even
when unused data lines operate in SPI/1-bit mode. Five independent exact pulls
therefore come from `SD_CARD_3V3`. On the always-powered host side, separate
10-kOhm positions hold SCK low and MOSI/D1, card CS and display CS high while
controllers reset. These are physical defaults, not firmware assumptions.

Four exact 22-Ohm source resistors sit after the active drivers: SCK, CMD and CS
after `SN74LVC3G34DCUR`, and MISO after `SN74LVC1G125DCKR`. Their value is a
first paper fit; shared-bus oscilloscope measurements remain the authority for
final population. Previously reserved shunt positions remain DNP.

Two `TPD4E05U06DQAR` arrays clamp CLK, CMD, DAT0, DAT1, DAT2, DAT3/CS, VDD and
card-detect. Both ground pads on each package receive short independent-via
returns; the socket shield uses its own multi-via return. VSS is a direct local
ground contact and is not routed through a signal suppressor.

## Card detect

The socket's `DETECT_B` contact is ground. `DETECT_A` is the protected raw
node; it reaches slow-I/O P21 through the 1-kOhm resistor and has a 10-kOhm
pull-up to always-present `3V3_MAIN` plus 100-nF local filtering. The host can
therefore debounce and report insertion/removal while the card rail is off.
The electrical RC does not replace software debounce or push-push mechanical
qualification.

## Runtime sequence

1. With the card rail off, stop new SPI2 work, drive `LCD_CS_N` and `SD_CS_N`
   high, SCK low and MOSI/D1 high.
2. Accept only a stable detected insertion, enable P20, wait for the controlled
   rail rise and verify a bounded ready timeout.
3. With every other SPI CS high, issue the required low-speed startup clocks
   and place the card into SPI mode **before** any display traffic resumes.
4. Run bounded card transactions; display non-preemptible occupancy remains at
   most the separately accepted 1-ms quantum.
5. For clean removal, reject new writers, sync and drain all writes, unmount,
   raise CS, disable P20 and wait the HIL-qualified QOD discharge interval
   before reporting safe removal.
6. For unexpected removal, stop the session immediately, report possible loss
   of the unwritten tail, preserve the last committed metadata and require a
   checked recovery/remount. No UI may claim that incomplete data is intact.

## Remaining HIL

- socket placement, card-finger access, push-push retention and enclosure dust
  boundary;
- exact media-set compatibility, endurance, startup current and brownout;
- shared QSPI/SPI clocks, high-Z behavior, insertion contention and final RC;
- at least 4.0 MB/s storage and 1.5 MB/s recording with measured 250-ms stalls;
- ESD, short, QOD discharge and repeated hot-insert/removal fault tests;
- filesystem corruption window, committed-record recovery and user-visible UX.

These gates block physical/footprint freeze and target-architecture completion,
but not the reviewed paper endpoint.

## Primary sources

- [Hirose DM3AT-SF-PEJM5 exact product page](https://www.hirose.com/en/product/p/CL0609-0031-0-00)
- [Espressif ESP32-S3 SD pull-up requirements](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/sd_pullup_requirements.html)
- [Espressif shared SPI bus and SD-card initialization](https://docs.espressif.com/projects/esp-idf/en/v5.0.2/esp32s3/api-reference/peripherals/sdspi_share.html)
- [TI TPD4E05U06 datasheet](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf)
- [TI SN74LVC1G125 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf)
- [TI SN74LVC3G34 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc3g34.pdf)
- [TI TPS22919 datasheet](https://www.ti.com/lit/ds/symlink/tps22919.pdf)
