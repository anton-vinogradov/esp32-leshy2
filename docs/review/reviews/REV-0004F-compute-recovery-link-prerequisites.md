# REV-0004F — compute recovery and link prerequisites

- Статус: **Проведено ревью пререквизитов; IMP-0026 разрешён DEC-0031**
- Дата: 2026-08-16
- Артефакт: [`REC-0001`](../components/REC-0001-compute-recovery-and-link-prerequisites.md)
- Finding: [`FND-0037`](../findings/FND-0037-c5-usb-download-strap-misidentified.md)

## Review result

| Check | Result |
|---|---|
| recovery works without target application firmware | yes at contract level; erased/corrupt-image HIL remains open |
| recovery works without a functioning peer MCU | yes; no peer-controlled mux/expander permitted |
| manufacturer ROM straps match the exact targets | yes after correcting C5 BOOT from GPIO26 to GPIO28 |
| S3/C5 UART fallback retained | yes; service access required even though normal recovery prefers USB |
| RP2354 internal flash incorrectly removes USB_BOOT | no; USB_BOOT + RUN and SWD remain |
| fixture USB can backfeed one compute domain | prohibited; VBUS-to-board path absent and VREF is sense-only |
| active inter-domain isolation required by current power tree | no; all compute peers share `3V3_CORE` and are reset-only domains |
| future individual power gating silently allowed | no; it reopens C-007 and requires Ioff-qualified isolation |
| exact owner-facing access topology fixed | yes after this prerequisite review; owner accepted B in `DEC-0031`, propagation is reviewed by `REV-0004G` |
| C-006/C-007 receive final Q | no; schematic/ERC/layout/fixture/HIL and exact passive qualification remain |

## Corrected mismatch ledger

| Artifact mismatch | Correction | Status |
|---|---|---|
| `PIN-0002` claimed GPIO26-low selected C5 USB Joint Download Boot | physical BOOT moved to GPIO28-low with GPIO27-high; reset uses CHIP_PU; GPIO26 is not tied to BOOT | corrected; `FND-0037` closed |

The factual prerequisites and correction receive **«Проведено ревью»**.
The former owner choice is now closed by `DEC-0031`; component qualification
does not advance beyond the documented partial state until its implementation
passes the listed CAD/AVL/mechanical/HIL gates.
