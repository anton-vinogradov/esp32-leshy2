# SVC-0001 — three-domain development access

- Статус: **Проведено ревью topology и first-target candidates; CAD/AVL/HIL открыты**
- Дата: 2026-08-16
- Решение: [`DEC-0031`](../decisions/DEC-0031-permanent-three-domain-development-access.md)
- Строки BOM: `C-006`, частично `C-001…003/007`
- Пререквизиты: [`REC-0001`](REC-0001-compute-recovery-and-link-prerequisites.md), `FND-0037` closed

## Exact first-target component set

| Function | Exact first target | Qty | Evidence and boundary |
|---|---|---:|---|
| USB-C 2.0 receptacle | `GCT USB4105-GF-A` | 3 | manufacturer USB 2.0 16-contact/top-mount specification; common connector reduces unique parts; exact CAD/retention/enclosure proof open |
| debug header | `Samtec FTSH-105-01-L-DV-K-TR` | 3 | active 2×5, 1.27 mm SMT keyed-notch header; common pinout; mating cable/strain/clearance proof open |
| BOOT/RESET switch | `C&K KMR221GULCLFS` | 6 | SPST-NO, 2 N, 200k-cycle, 4.6×2.8 mm SMT top-actuated first target; ergonomics/recess/sealing proof open |
| USB D+/D− ESD | `TI TPD2EUSB30ADRTR` | 3 | active two-line 0.7 pF typical, 3.6 V VRWM, ±8 kV IEC-contact candidate; exact placement/AVL/assembly proof open |
| Type-C sink declaration | 5.1 kΩ 1% from CC1 and CC2 to GND | 6 | one pair per receptacle; exact resistor MPN joins the consolidated passive manifest |

Primary/current sources:

- [GCT USB4105 product specification](https://gct.co/files/specs/usb4105-spec.pdf)
- [Samtec FTSH-105-01-L-DV-K](https://www.samtec.com/products/ftsh-105-01-l-dv-k)
- [C&K KMR221GULCLFS](https://www.ckswitches.com/products/switches/product-details/Tactile/KMR2/KMR221GULCLFS/)
- [TI TPD2EUSB30A](https://www.ti.com/product/TPD2EUSB30A)

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

S3 GPIO43/44 runtime sharing is safe only because U214/GNSS accessory power is
off/high-Z during ROM service. C5 UART pins were previously counted as generic
free in `SYN-3A`; permanent diagnostics reclassifies GPIO11/12 as
service-reserved and leaves five generic C5 GPIO (`FND-0038`). RP SWD is
dedicated. These invariants become ERC/HIL checks rather than layout notes.

## USB topology

1. Each D+/D− pair routes directly between one MCU and one receptacle; no mux,
   shared stub or cross-domain switching exists.
2. `TPD2EUSB30ADRTR` sits at each connector with a short low-inductance ground
   path. Series elements remain at the MCU side: S3/C5 begin with manufacturer
   22/33 Ω tuning footprints; RP uses 27 Ω.
3. S3 VBUS enters only the later-qualified product power/protection path.
4. C5/RP VBUS stops at protected high-impedance presence/test circuitry and is
   not a source for `3V3_CORE` or an individual MCU.
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

The topology and candidates receive **«Проведено ревью»**. No component row
receives final Q until the exit gates pass.
