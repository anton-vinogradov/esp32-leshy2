# INT-0001 — dependency-ordered internal-design closure sequence

- Статус: **Проведено ревью порядка; внутренние блоки открыты**
- Дата: 2026-08-18
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
| `I1` | compute, clocks, reset, signed update, recovery/diagnostics and S3↔C5↔RP links | `I0`, `DEC-0012/0031`, `REC-0001` | **Проведено ревью** by `DEC-0059/REV-0005L`: 1-bit SDIO, full USB/UART service, exact topology budgeted; HIL named | every domain independently recoverable and diagnosable; exact transport/service topology selected and budgeted |
| `I2` | AON safety, hard STOP, re-arm, TX gates and actual-TX evidence | `I1`, `DEC-0024`, group arbiter | **Проведено ревью** by `DEC-0061/SAFE-0002/REV-0005O`: three-domain latch/gates, eight evidence channels, source mask, hardware aggregate and test points machine-projected; I3/I6/HIL proofs named | non-programmable truth table, exact parts/rails/faults and test points reviewed |
| `I3` | battery, charging, power path, rails, load switches, monitoring and thermal | `I1/I2`, `PWR-0001`, scenario ledger | **active; supervised 2S, exact manager/frontend, BQ25798 and TPS25751/EEPROM passive profiles, rail tree, eFuse, converter passives and bounded diagnostic frontends reviewed** through `DEC-0076/PWR-0015`; mechanics, thresholds, hot calculation and HIL open | freeze remaining passives and complete loss/thermal/fault/source-transition budget |
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

`I2` has **Проведено ревью** through `DEC-0061/SAFE-0002/REV-0005O`. The
machine source now contains the three-domain AON latch/reset/gate tree, seven
RF detectors, optical IR evidence, eight-bit local-I²C source mask, direct
hardware aggregate/indicators, default pulls, fault cases and test points.
Exact RF taps/thresholds remain `I6/HIL`, not hidden paper uncertainty.

`I3` is now active. It must start from this accepted AON load and all existing
scenario/rail demands, then select the battery/charger/power-path topology,
every quiet-state load switch, sequencing, monitoring, reverse-current policy
and a calculated loss/thermal/fault budget before `I4` begins.

`PWR-0002/FND-0073/REV-0005P` complete that prerequisite pass and reject the
old implementation as a target. `IMP-0052/B` is accepted as `DEC-0062`: the
two 18650 slots are individually replaceable, but reverse insertion, mismatch,
removal and contact bounce must fail closed before charge/discharge admission.
`DEC-0064` later reopened their electrical series/controlled-1S choice;
`PWR-0006/FND-0076/REV-0005S` review equal-energy/current facts, cross-charge,
rail classes and cost. The owner selected supervised 2S in
`DEC-0065/REV-0005T`; option A manager is accepted by
`DEC-0066/REV-0005V`. `IMP-0053/B` is
accepted as `DEC-0063`; `PWR-0004/REV-0005R` review the exact sink-only 30-W
TPS25751DREFR/BQ25798RQMR/CAT24C512WI-GT3/TVS2200DRVR frontend, preserve direct
S3 USB2 and leave GPIO47 free. `PWR-0007/FND-0077/REV-0005W` exposed the
linear-prequal gate; `DEC-0067/REV-0005X` accept no in-device recovery and the
exact active FET/fuse/NTC/shunt/hold/supply-isolation packages. I3 now
continues through `PWR-0008/DEC-0068/REV-0005Y`, which review the exact
independent fixed rail tree and quiet-state switches; `DEC-0069/REV-0005Z`
then make the externally accessible eFuse latch-off, and
`PWR-0009/DEC-0070/REV-0005AA` qualify optional-rail PG with two exact
`MMBT3904-7-F` stages instead of treating normal off as a fault.
`PWR-0013/FND-0078` correct PA24 to PA25/PA26 and freeze the exact
load/divider components. `PWR-0014/DEC-0075/REV-0005AF` then review the exact
BQ25798 750-kHz/2.2-uH energy banks, TS/ILIM, reset defaults and all special
pins. `FND-0079` corrects the product USB-C/USB2 endpoint back to dependent
step I4. `FND-0080/PWR-0015/DEC-0076/REV-0005AG` correct raw VBUS to both
TPS pin groups and close SafeMode straps, all controller/EEPROM passives,
unused contacts and both complete bus pull networks. `PWR-0016/DEC-0077`
close the exact polarized holder/NTC paper coupling;
`PWR-0017/FND-0082/DEC-0078` then correct the TPUL package and close the
hardware repetition bound. `PWR-0018/FND-0083/DEC-0079` select two exact
`XTAR 18650 4000mAh` protected cells and freeze the 2-A charge ceiling.
Remaining I3 dependencies are certification/specimen fit and exact-cell droop
thresholds, pulse/cooldown lot and hot-copper HIL, followed by the complete
hot loss/thermal/fault tree.
