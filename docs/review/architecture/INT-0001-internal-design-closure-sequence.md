# INT-0001 — dependency-ordered internal-design closure sequence

- Статус: **Проведено ревью порядка; внутренние блоки открыты**
- Дата: 2026-08-17
- Decision: [`DEC-0058`](../decisions/DEC-0058-internals-before-integrated-mockup.md)
- Working map: [`PIN-0003`](PIN-0003-g2f-3i-principled-pinout.md)
- Umbrella finding: [`FND-0060`](../findings/FND-0060-abstract-electrical-endpoints-block-final-pinout.md)

## Completion boundary

Каждый блок получает собственное **«Проведено ревью»** только когда его
пререквизиты проверены, internal decisions приняты, exact first-target devices
и circuit boundaries согласованы, pin/power/cost consequences распространены,
а HIL-only остаток отделён от paper uncertainty. Integrated mockup
возобновляется только после совместного self-review всех блоков.

Exact MPN availability повторно проверяется при выборе конкретной BOM-строки,
а не на каждом проходе архитектуры. До этого `MPN TBD` предпочтительнее
непроверенного случайного order code.

## Dependency chain

| Step | Internal block | Reviewed inputs | Current state | Paper/electrical exit |
|---|---|---|---|---|
| `I0` | semantic owners, buses, controllers, exposed pads and budgets | wishlist, `DEM-0001`, `SRC-0002` | `G2F-3I/PIN-0003` reviewed working map; not atomic | all later changes regenerate one machine source without collision or hidden pin |
| `I1` | compute, clocks, reset, signed update, recovery/diagnostics and S3↔C5↔RP links | `I0`, `DEC-0012/0031`, `REC-0001` | active; `FND-0070/IMP-0049` expose the 4-bit-SDIO service collision | every domain independently recoverable and diagnosable; exact transport/service topology selected and budgeted |
| `I2` | AON safety, hard STOP, re-arm, TX gates and actual-TX evidence | `I1`, `DEC-0024`, group arbiter | architecture invariant accepted; exact latch/gates/detectors absent | non-programmable truth table, exact parts/rails/faults and test points reviewed |
| `I3` | battery, charging, power path, rails, load switches, monitoring and thermal | `I1/I2`, `PWR-0001`, scenario ledger | capacity envelope reviewed; exact circuits absent | complete rail tree and sequencing with exact first targets, loss/thermal/fault budget |
| `I4` | display, touch, UI electrical plane, microSD and product USB | `I1/I3` | digital contacts largely exact; backlight/protection/UI endpoints open | exact electrical endpoints, protection, reset/default and shared-SPI contracts |
| `I5` | Si4732/audio capture/playback/TX/microphone/speaker | `I2/I3/I4`, `DEC-0054` | active IC topology selected; passives, rails and HIL open | calculated complete circuits and safe reset/powered-off behavior; HIL plan separated |
| `I6` | nRF/CC/C5/voice/IR RF assemblies, quiet-state isolation and feeds | `I2/I3`, `DEC-0045…0050` | owners/ports accepted; production modules/frontends/gates/evidence open | exact assemblies and feed/protection circuits, power/coexistence budgets and qualification fixtures |
| `I7` | M5 Unit/Cap, U214, external 5 V, USB/debug and expansion protection | `I1/I2/I3` | logical profiles reviewed; exact protection/detection and some connector mechanics open | profile-safe electrical interface, backfeed/hot-plug/unknown-device behavior and service access |
| `I8` | consolidated BOM evidence, lifecycle, availability, cost and alternates | `I1…I7` | scattered candidates; no coherent target BOM | every base function maps to exact first target plus equivalence/alternate and sourcing gate |
| `I9` | whole internal self-review and atomic paper projection | `I0…I8` | not started | no incompatible fragments, hidden `abstract:*`, unbudgeted rail/pin or unresolved owner decision |

## Reopen rules

- A failed prerequisite reopens its consumer steps; it is not patched locally.
- A part envelope may reject an internal candidate, but does not authorize a
  holistic enclosure layout before `I9`.
- A HIL-only item remains named with fixture and pass condition; it does not
  keep an otherwise complete paper block vaguely «open».
- Any change that removes a capability, service path or safety guarantee returns
  to the owner as an explicit proposal before it changes the machine map.

## Current next gate

`I1` is active. Official current documentation confirms the retained primitive
paths, but the current 4-bit S3↔C5 SDIO allocation conflicts with the former
full USB/UART service topology. `FND-0070/IMP-0049` compare the complete
no-silent-loss alternatives before any pin-map mutation.
