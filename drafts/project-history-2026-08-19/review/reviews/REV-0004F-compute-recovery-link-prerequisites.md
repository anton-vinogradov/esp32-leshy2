# REV-0004F — compute recovery and link prerequisites

- Статус: **Проведено ревью manufacturer prerequisites; exact topology superseded**
- Дата: 2026-08-16
- Артефакт: [`REC-0001`](../components/REC-0001-compute-recovery-and-link-prerequisites.md)
- Finding: [`FND-0037`](../findings/FND-0037-c5-usb-download-strap-misidentified.md)

## Review result

| Check | Result |
|---|---|
| recovery works without target application firmware | yes at contract level; erased/corrupt-image HIL remains open |
| recovery works without a functioning peer MCU | yes; no peer-controlled mux/expander permitted |
| manufacturer ROM straps match the exact targets | yes after correcting C5 BOOT from GPIO26 to GPIO28 |
| S3/C5 UART fallback retained in current maps | C5 — where explicitly allocated; S3 — no, GPIO43/44 conflict with current U214 use, while native USB+EN/BOOT remains the baseline |
| RP2354 internal flash incorrectly removes USB_BOOT | no; USB_BOOT + RUN and SWD remain |
| fixture USB can backfeed one compute domain | prohibited; VBUS-to-board path absent and VREF is sense-only |
| active inter-domain isolation required by current power tree | no; all compute peers share `3V3_CORE` and are reset-only domains |
| future individual power gating silently allowed | no; it reopens C-007 and requires Ioff-qualified isolation |
| exact owner-facing access topology fixed | no; owner requirement retained by `DEC-0031`, exact implementation superseded by `DEC-0032/REV-0004H` |
| C-006/C-007 receive final Q | no; schematic/ERC/layout/fixture/HIL and exact passive qualification remain |

## Corrected mismatch ledger

| Artifact mismatch | Correction | Status |
|---|---|---|
| `PIN-0002` claimed GPIO26-low selected C5 USB Joint Download Boot | physical BOOT moved to GPIO28-low with GPIO27-high; reset uses CHIP_PU; GPIO26 is not tied to BOOT | corrected; `FND-0037` closed |
| superseded service study was read as proof of S3 UART0 in active G2F maps | active service contract now claims native USB+EN/BOOT only; UART0 requires a represented route/isolation proof | corrected in `FND-0052`; topology remains open |

The factual prerequisites and correction receive **«Проведено ревью»**.
The former exact owner choice was superseded by `DEC-0032`; only the independent
programming/recovery/diagnostics requirement and reviewed manufacturer
primitives remain active. Component qualification does not advance beyond the
documented partial state until a future complete topology passes the listed
CAD/AVL/mechanical/HIL gates.
