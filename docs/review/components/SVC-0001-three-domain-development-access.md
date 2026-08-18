# SVC-0001 — three-domain development access

- Статус: **historical topology; exact implementation superseded by `SVC-0002/DEC-0099`**
- Дата: 2026-08-16
- Решение: [`DEC-0031`](../decisions/DEC-0031-permanent-three-domain-development-access.md)
- Строки BOM: `C-006`, частично `C-001…003/007`
- Пререквизиты: [`REC-0001`](REC-0001-compute-recovery-and-link-prerequisites.md), `FND-0037` closed

> Permanent independent programming/recovery/diagnostics remains a product
> requirement. This file preserves the topology review. Exact parts, passive
> circuits, board-off isolation and corrected reset behavior are normative in
> [`SVC-0002`](../architecture/SVC-0002-exact-three-domain-service-recovery-boundary.md).

## Exact first-target component set

| Function | Exact first target | Qty | Evidence and boundary |
|---|---|---:|---|
| data-only USB-C 2.0 receptacle | `GCT USB4105-GF-A` | 2 | C5/RP only; S3 uses the already reviewed product connector |
| debug header | `Samtec FTSH-105-01-L-DV-K-P-TR` | 3 | active 2×5, 1.27 mm SMT, keyed and explicit pick-and-place pad |
| BOOT/RESET switch | `Alps Alpine SKQGADE010` | 6 | mass-produced automotive SPST-NO, 2.55 N, 100k cycles, documented low-level floor |
| USB D+/D− ESD | `TI TPD2EUSB30ADRTR` | 2 | one per data-only port; S3 product protection is separate |
| board-off USB data isolation | `onsemi FSUSB42MUX` | 2 | Ioff/power-off protected D+/D− disconnect; hard-selected HSD1 |
| DBG10 ESD | `TI TPD4E05U06DQAR` | 3 | one array per header for RESET/BOOT/DBG0/DBG1 |
| Type-C sink declaration | exact `RC0402FR-075K1L` | 4 | one 5.1-kΩ Rd per CC contact of the two data-only ports |

Primary/current sources:

- [GCT USB4105 product specification](https://gct.co/files/specs/usb4105-spec.pdf)
- [Samtec FTSH-105-01-L-DV-K](https://www.samtec.com/products/ftsh-105-01-l-dv-k)
- [Alps Alpine SKQGADE010](https://tech.alpsalpine.com/e/products/detail/SKQGADE010/)
- [TI TPD2EUSB30A](https://www.ti.com/product/TPD2EUSB30A)
- [onsemi FSUSB42](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf)

These are first qualification targets, not unchangeable monopolies. Any
alternate must preserve geometry, mating life, retention, electrical behavior,
debug access and HIL before it can enter the AVL.

## Common `DBG10` physical pinout

| Pin | Common meaning | Electrical rule |
|---:|---|---|
| 1 | `VTREF_SENSE` | target→fixture level reference through current-limiting sense path; fixture never powers target |
| 2 | GND | ground-first fixture wiring |
| 3 | `RESET_N` | fixture starts high-Z; active-low only |
| 4 | `BOOT_N` | fixture starts high-Z; active-low only |
| 5 | `DBG0` | target-specific UART TX or SWDIO |
| 6 | `DBG1` | target-specific UART RX or SWCLK |
| 7 | GND | adjacent return for debug signals |
| 8 | `ID0` | passive strapped identity; fixture input only |
| 9 | GND | return/guard |
| 10 | `ID1` | passive strapped identity; fixture input only |

The fixture reads `ID1:ID0` while pins 3…6 remain high-Z. Codes are `00=S3`,
`01=C5`, `10=RP`, `11=invalid/unattached`. ID straps use resistors so a
misconfigured fixture cannot hard-short VTREF to ground.

## Per-domain mapping

| Domain | RESET_N | BOOT_N | DBG0 | DBG1 | Dedicated USB |
|---|---|---|---|---|---|
| S3 | `EN` | `GPIO0` | UART0 TX / GPIO43 | UART0 RX / GPIO44 | product USB GPIO19/20, data + protected power input |
| C5 | `CHIP_PU` | `GPIO28` | UART0 TX / GPIO11 | UART0 RX / GPIO12 | service USB GPIO13/14, data-only; GPIO27 fixed high for Joint Download Boot 0 |
| RP2354A | `RUN` | `USB_BOOT`→QSPI_SS through 1 kΩ | `SWDIO` | `SWCLK` | service USB DP/DM, data-only |

S3 GPIO43/44 are dedicated UART0 service contacts in the current map. C5 UART
pins were previously counted as generic free in `SYN-3A`; permanent diagnostics reclassifies GPIO11/12 as
service-reserved and leaves five generic C5 GPIO (`FND-0038`). RP SWD is
dedicated. These invariants become ERC/HIL checks rather than layout notes.

## USB topology

1. Each D+/D− pair remains private to one MCU and one receptacle; there is no
   cross-domain selection. C5/RP each pass through a dedicated, fixed-selected
   `FSUSB42MUX` only to block board-off data backfeed.
2. `TPD2EUSB30ADRTR` sits at each C5/RP connector with a short return. Exact
   MCU-side series values are 22 Ω for C5 and 27 Ω for RP. S3 uses the separate
   protected product USB path.
3. S3 VBUS enters only the later-qualified product power/protection path.
4. C5/RP VBUS stops at one 1-MΩ bleeder and high-impedance test pad and is not
   a source for any product rail or MCU.
5. Three simultaneous host cables are a required HIL case: no host-to-host
   backfeed, false attach, ground fault, reset storm or TX re-arm.

## Buttons and safety

Each MCU has its own momentary `RESET` and `BOOT` button wired in parallel with
the corresponding DBG10 controls. Normal pulls define SPI/application boot;
buttons and fixture only pull low. The six switches are service controls, not
ordinary UI keys and not inputs to the I²C expander.

Any asserted RESET/BOOT clears or expires the affected domain's TX leases.
Recovery starts with hardware TX permissions off. Debugging an RF transmitter
does not bypass STOP, power/profile, authorization or conducted/shielded gates.

## Exit gates

- exact project-local symbols/footprints and provenance for all four component
  families;
- schematic/ERC proof of pulls, CC, USB series/ESD, VBUS isolation and no
  peer/fixture dependency;
- mechanical clearance, connector insertion/retention, button access/recess and
  three-cable strain review;
- two-authorised-source AVL/quote and PCBA capability for the 1 mm ESD package;
- erased/corrupt-image USB/UART/SWD recovery on all domains;
- misplug, wrong-ID, held-button, multi-host, ESD and RF/EMC HIL.

The historical topology received **«Проведено ревью»**. `SVC-0002/DEC-0099`
supersede its exact implementation and also receive **«Проведено ревью»** in
paper electrical scope. No physical component receives final Q until the exit
gates pass.
