# INT-0001 — dependency-ordered internal-design closure sequence

- Статус: **Проведено ревью порядка; I1…I5 paper reviewed, I6 active**
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
| `I3` | battery, charging, power path, rails, load switches, monitoring and thermal | `I1/I2`, `PWR-0001`, scenario ledger | **Проведено ревью paper electrical scope** by `DEC-0082/PWR-0021/REV-0005AM`; exact-lot, thermal, transition and destructive HIL plus I8 certification evidence remain explicit | exact circuits, source/fault truth, loss ledger and every physical residue classified without claiming HIL |
| `I4` | display, touch, UI electrical plane, microSD and product USB | `I1/I3` | **Проведено ревью paper electrical scope** by `DEC-0089/IOX-0001/REV-0005AT`; exact USB/display/microSD/controls/touch endpoints plus TCA6424A core, addresses, cross-domain isolation and shared-interface audit complete; physical/HIL gates named | exact electrical endpoints, protection, reset/default and shared-SPI contracts |
| `I5` | Si4732/audio capture/playback/TX/microphone/speaker and SA518 electrical boundary | `I2/I3/I4`, `DEC-0054` | **Проведено ревью paper electrical scope** by `DEC-0090/AUDIO-0003/REV-0005AU`; exact rails, interfaces, passives and acoustic endpoints instantiated; HIL named | calculated complete circuits and safe reset/powered-off behavior; HIL plan separated |
| `I6` | nRF/CC/C5/voice/IR RF assemblies, quiet-state isolation and feeds | `I2/I3/I5`, `DEC-0045…0050` | **active paper block**; three-nRF electrical subblock reviewed by `DEC-0091/REV-0005AV`; S3/C5/CC/voice/receiver/IR RF endpoints and consolidated coexistence remain open | exact assemblies and feed/protection circuits, power/coexistence budgets and qualification fixtures |
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

## Completed I3 boundary and current next gate

`I2` has **Проведено ревью** through `DEC-0061/SAFE-0002/REV-0005O`. The
machine source now contains the three-domain AON latch/reset/gate tree, seven
RF detectors, optical IR evidence, eight-bit local-I²C source mask, direct
hardware aggregate/indicators, default pulls, fault cases and test points.
Exact RF taps/thresholds remain `I6/HIL`, not hidden paper uncertainty.

`I3` started from this accepted AON load and all existing scenario/rail
demands, then selected the battery/charger/power-path topology,
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
`FND-0084/PWR-0019/DEC-0080` then remove the hidden programmable-sequencer
placeholder: exact AON PG, TPS3808 MR/SENSE/CT/POR and a 10-kOhm/100-kOhm pair
now form the complete hardware main-release path, with a conservative
system-first input/charge budget. `FND-0085/PWR-0020/DEC-0081/REV-0005AL`
then correct the remaining single-fault gap: exact `TPS25961DRVR` AON and two
separate `TPS25974LRPWR` main/voice stages split every raw buck output from its
load, move operational evidence to protected PG and review exact settings,
loss and fault direction. Remaining I3 dependencies are
certification/specimen fit and exact-cell droop thresholds, pulse/cooldown lot
and hot-copper HIL, destructive overvoltage/short containment,
source-transition HIL and consolidation of the complete measured thermal
budget.

`FND-0086/PWR-0021/DEC-0082/REV-0005AM` audit that residue against the
completion rule above. No generic paper design gap remains: certification is
an I8 procurement gate and every other item is a named lot/prototype/
controlled-destructive HIL with a pass and reopen condition. I3 therefore has
**«Проведено ревью»** for paper electrical scope without promoting any
measurement. I4 is the active dependent paper block; failed I3 HIL reopens I3
before changing a rail, mode or target guarantee.

I4 begins with `FND-0087/USB-0001/DEC-0083/REV-0005AN`. Exact
`DX07S016JA1R1500` and `TPD4S201RUKR` replace the abstract product-port
endpoint, protect CC1/CC2 and USB2 D+/D- without consuming GPIO, and correct
the CC shunts from 330 pF to 220 pF after a complete receiver-capacitance
screen. This endpoint has **«Проведено ревью»** at paper-schematic level;
placement, shield return, enclosure cutout, total CC, USB Full-Speed RC/SI,
ESD and short-to-VBUS HIL remain named.

`FND-0088/DSP-0006/DEC-0084/REV-0005AO` next replace the display's abstract
logic/backlight/mate endpoints with exact physical instances. The paper
endpoint is reviewed without changing GPIO budget. A real HMX tail must still
prove the first connector candidate, and shared-QSPI, touch, current, thermal
and injected-fault HIL remain evidence gates.

`FND-0089/STO-0001/DEC-0085/REV-0005AP` next replace the microSD abstractions
with exact switched power, Ioff card-side buffers, a CS-gated DAT0 return,
mandatory pulls, source damping, eight ESD channels and always-readable
detect. The paper endpoint is reviewed with no new GPIO. Socket access,
real-media/endurance, throughput/contention, hot-removal, electrical abuse and
filesystem-recovery HIL remain evidence gates. I4 now proceeds to the remaining
UI protection/default-state endpoints.

`FND-0090/UI-0001/DEC-0086/REV-0005AQ` restore D-pad/OK, BACK, OPT, F1, F2,
encoder push, direct PTT, hard STOP and RE-ARM without inheriting the obsolete
legacy GPIO placement. Dedicated TCA9534A P0…P6 gives the ordinary controls an
interrupt-driven 4×3 plane, P7 is reserved, TCA6424 P00…P05 return to the main
slow-I/O budget and encoder A/B use direct S3 PCNT0. The decoder alternative
was rejected because its disabled state could not wake the first key press.
`FND-0091` separately corrects the exact TCA9534A address table to RP-local
`0x38` and S3 UI candidate `0x3F`. Control inventory and principled pin fit have
**«Проведено ревью»**.

`FND-0092/UI-0002/DEC-0087/REV-0005AR` then close the dependent switch-current,
default-state and ESD boundary. Eleven exact `Y78B23214FP` low-current tactile
switches cover the nine discrete ordinary controls, direct PTT and recessed
RE-ARM; exact gold-clad `AEQ10410` preserves the normally-closed hard STOP
inside its documented 100-uA-at-3-V range. One `TPD8E003DQDR` and two separate
`TPD4E05U06DQAR` instances protect matrix, encoder/PTT and safety inputs without
mixing the safety ESD return. Exact cap/guard/harness/enclosure mechanics and
electrical/HIL injection remain open.

`FND-0093/DSP-0007/DEC-0088/REV-0005AS` close the former touch identity and
polarity uncertainty. Exact integrated `ST77922` owns both display and touch,
touch responds at `0x38`, and active-low TP_INT now has a 10-kOhm raw pull-up
plus fixed non-inverting `SN74LVC1G07DCKR` before shared GPIO37. The obsolete
inverter population option and stale direct-GPIO39 machine text are removed.
Identity/readback, IRQ pulse/clear, reset recovery, shared-source discovery and
physical HIL remain named.

`FND-0094/IOX-0001/DEC-0089/REV-0005AT` complete the consolidated dependency
and abstract-endpoint audit. The exact TCA6424A core now has address `0x22`,
complete VCCI/VCCP/decoupling/ground/reset/interrupt routes and fixture plus
full-main-power-cycle recovery. Two AON-powered open-drain buffers prevent
positive injection into P22/P23 while preserving STOP/evidence polarity. The
pack target is fixed at `0x2A`, microSD terminates at real GPIO4, the product
USB shield directly bonds to local power/ESD ground and the STOP LED resistor
is exact. No generic I4-owned paper endpoint remains; I4 therefore has
**«Проведено ревью»** at paper electrical scope. I5 then closes through
`FND-0095/AUDIO-0003/DEC-0090/REV-0005AU`: exact codec, receiver and voice
power/interface boundaries, analog paths, passives and physical acoustic
endpoints replace the remaining audio abstractions. Main slow I/O becomes
`21/0/3`; all controls remain intact. I5 has **«Проведено ревью»** and I6 is
now active. `FND-0096/N24E-0001/DEC-0091/REV-0005AV` then give its first
subblock **«Проведено ревью»**: three full-function nRF paths now have exact
Ioff isolation, local energy and 2400–2525-MHz forward-power evidence without
freezing the unproven Ebyte mate. S3/C5/CC/voice/receiver/IR RF endpoints and
the consolidated coexistence proof remain active. All prototype/physical/procurement evidence remains explicit,
and neither KiCad nor the paused integrated mockup is authorized.
