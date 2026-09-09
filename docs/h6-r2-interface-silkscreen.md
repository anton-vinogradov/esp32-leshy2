# Interface silkscreen

[Home](../README.md) · [Component views](h6-r2-component-views.md) · [Русский](h6-r2-interface-silkscreen.ru.md)

H6.0.3-R1 · 2026-09-09. This is a label-completeness update, not a phase closure
or fabrication approval.

The update adds **29 real F/B silkscreen labels: 13 on UI and 16 on RF**.
Eight neighbouring RF resistors were relocated locally for clear debug labels.
Connectors, selected parts, nets, copper and the board outline are unchanged.
Existing button, indicator, antenna and USB identities remain intact. The old user-label
audit checked its selected labels; it did not prove that every interface had one.

## What the labels mean

| Area | User or assembly identification |
| --- | --- |
| UI optical edge | U24 `IR RX`: demodulated IR receiver; U23 `IR LRN`: carrier/learning receiver; D11 `IR TX`: IR emitter. These are distinct from the existing `IR` TX-status LED label. |
| Antennas and USB | Retain each SMA owner/band and each USB owner plus `DATA USB` or `POWER + USB`. Identical USB bodies do not merge their functions. |
| UI internal coax | J4 `S3 ANT`, J8 `C5 ANT`, J13 `nRF1 ANT`, J15 `nRF2 ANT`, J17 `nRF3 ANT`. These identify cable destinations on B, not connector ordering in a picture. |
| Debug headers | B-side owner labels identify S3, C5 and Hub; on RF, J2 `PACK`, J3 `RF` and J13 `SAFE` identify the pack, RF RP and safety service headers. A printed owner does not prove that reset, boot or recovery works electrically. |
| Display, storage and interboard | B-side J1 `DISPLAY`, J18 `M1 UI` and RF J12 `M1 RF`; retain outward `microSD`. The existing F-side `DISPLAY · FPC ↑` is an assembly mark intentionally covered by the installed display. |
| RF external/service access | `HEADSET`, `CAP`, `M5 UNIT`, `POWER`, `NFC`; TP1 has B-side `MAIN` / `PG` on two lines. `POWER` does not assign unverified RUN/KILL directions. `NFC` identifies the reservation; the pickup loop is not yet routed. |
| Microphone and speaker | Existing outward UI `MIC` belongs to RF-inner MK1, not a UI microphone footprint; a local B-side `MIC` is now also present on RF. RF LS1 has B-side `SPK +` and `SPK -`: **both are BTL amplifier outputs; SPK - is not ground**. The separate UI speaker-body drawing remains an assembly representation. |
| Cells and sensors | BT1 uses full names at both ends: `CELL0 -`, `CELL1 +`, `CELL0 +`, `CELL1 -`, identifying the reviewed checkerboard cell polarity. Existing `NTC0 PAD` / `NTC1 PAD` remain assembly marks, not proof of thermal contact. |
| Controls and indicators | Retain F1–F8, navigation, BACK/OPT, encoder/PTT, owner + RST/BOOT, and every TX/fault indicator label. |

The exact per-reference text and side requirements are in the independent
[coverage contract](../hardware/layout/h6-r2-interface-label-coverage.json).
It covers the physical interface inventory plus NFC and the service probe;
it does not demand a label on every resistor, IC pin or internal thermistor.

## Real ink versus drawing annotations

In the [component views](h6-r2-component-views.md), **blue is actual native
F/B silkscreen**. Grey Fab outlines, optical-direction arrows and renderer-added
references such as `U23` or `D11` are inspection graphics, not printed labels.
Internal assembly/service labels must be real B.SilkS text, readable when the
board is turned over. Having a visible reference in an SVG is insufficient.

The [coverage helper](../hardware/layout/h6_r2_interface_label_coverage.py)
checks the current ledger/catalog interface inventory independently of the
label generator, then checks owner/reference/text/side and, when supplied,
actual native footprint and visible PCB_TEXT records. Missing, extra, duplicate,
wrong-owner or wrong-side labels fail. A semantic-plan pass alone is not native
verification. Text positions and physical ink clearances have separate checks.

## Verified scope and limits

The accepted local captions are `PACK` at RF J2, `RF` at J3 and `SAFE` at J13.
They supersede the distant draft placements. The
[native integration receipt](../hardware/layout/h6-r2-interface-label-integration.json)
records the completed finite migration:

- Native coverage: **76/76 interfaces and 95/95 required labels**, with zero ink-geometry errors.
- Fresh DRC on both boards: **0 violations and 0 schematic-parity errors**.
- All **857 copper objects (92 UI + 765 RF)**, pad/net connectivity and unrelated footprints are preserved; only the eight declared resistors moved.

The [finite relocation review](../hardware/layout/h6-r2-interface-label-relocation-review.json)
records ordinary-resistor placement tradeoffs, including the 1 kΩ VTREF series
resistor. Pad-centre distances are distinct from actual routed lengths or performance.
The [live silkscreen audit](../hardware/layout/generated/H6-R2-user-silkscreen-audit.json)
and [current routing report](h6-r2-current-routing.md) own current results and
hashes; hashes are not duplicated here.

Even complete readable labels do not qualify solder access, the closed device,
electrical safety, RF/acoustic performance or production. Existing H6 review
gates remain open.
