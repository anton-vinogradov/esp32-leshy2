# PWR-0021 — I3 consolidated paper closure

- Статус: **Проведено ревью paper electrical closure; all physical evidence remains explicit**
- Дата: 2026-08-18
- Dependency step: [`INT-0001/I3`](INT-0001-internal-design-closure-sequence.md)
- Finding: [`FND-0086`](../findings/FND-0086-i3-paper-and-hil-closure-were-conflated.md)
- Decision: [`DEC-0082`](../decisions/DEC-0082-i3-paper-closure.md)
- Propagation review: [`REV-0005AM`](../reviews/REV-0005AM-i3-paper-closure-propagation.md)

## Review question

Does I3 still contain an unresolved paper architecture choice, hidden physical
part, unbudgeted load or unassigned fault, or are its remaining uncertainties
all evidence that requires a real lot/board/fixture?

## Prerequisite closure

| I3 obligation | Reviewed artifact/result | Residue class |
|---|---|---|
| source role and load scenarios | `PWR-0002/0004`: sink-only 5/9/15-V input, 12-W continuous/15-W transient product envelope | negotiated-source and full-load HIL |
| replaceable 2S topology | `PWR-0005…0007`: MAX17320/MSPM0 fail-closed admission, no in-device deep recovery, exact switching/fuse/shunt/NTC path | cell/holder lot, source-handover and injected-fault HIL |
| charger and PD support | `PWR-0014/0015`: every BQ25798/TPS25751/CAT24 contact, passive, reset and recovery path exact | layout, bus, blank-image, attach/remove, thermal and EMI HIL |
| holder/cell/diagnostic | `PWR-0016…0018`: exact 1048P, three NTC contacts, bounded dual-channel diagnostic and exact XTAR first target | certification procurement plus received-lot fit/droop/thermal HIL |
| rail tree and quiet states | `PWR-0008…0012`: exact fixed converters, energy/feedback/control parts, branch switches, accessory latch-off | capacitance, load-step, discharge, ripple/EMI and hot HIL |
| source sequence | `PWR-0019`: protected source→AON→PG/SENSE/CT/POR→main and conservative system-first charge rule | transition/DPM/brownout HIL |
| internal single-fault containment | `PWR-0020`: exact AON/main/voice post-buck cutoffs, protected PG, thresholds and recovery authority | trip-energy, destructive-short and hot HIL |

No unresolved owner choice appears in this table. Every physical active/passive
part required to express the I3 paper circuits is present in the machine map.
Abstract endpoints remaining in the generated ledger are named system nets,
fixture evidence or consumers owned by I2/I4…I7, not a hidden I3 sequencer or
protection device.

## Consolidated power and heat ledger

The purpose of this table is to ensure no heat source disappears between
component reviews. Values are paper screens already derived from exact parts;
they are not enclosure-temperature claims.

| Boundary | Accepted paper screen | What is deliberately not claimed |
|---|---|---|
| product load | 12 W continuous; 15 W bounded transient | simultaneous maximum of mutually exclusive signal groups |
| low-stack battery current | 15 W / (6.0 V × 0.90) = 2.78 A transient; path floor 3 A continuous/4 A pulse | 90% as a guaranteed efficiency or cell-temperature result |
| two slot fuses + shunt + pack FET | 35.5 mOhm and about 0.275 W at 2.78 A before contacts/copper | hot resistance, holder/contact/copper loss |
| diagnostic load | 7.82 W instantaneous at the paper high corner; at most 0.98 W total average under the hardware-only 50/350-ms abuse bound; normal firmware waits at least 10 s | local copper/enclosure temperature or exact lot pulse curve |
| main magnetic + post-buck eFuse | about 0.238 W inductor copper at 2.5 A plus about 0.063 W typical protected-boundary burden | converter switching loss and hot-Ron temperature |
| voice magnetic + post-buck eFuse | about 0.059 W inductor copper at 1.25 A plus about 0.018 W typical protected-boundary burden | RF/audio duty-cycle temperature |
| external magnetic + eFuse + bleeder | about 0.094 W inductor copper, 0.044 W typical eFuse conduction at 1.25 A and 0.025 W bleeder | connector/accessory/copper hot spot |
| AON cutoff | about 9.1-mV/0.18-mW conservative series proxy at 20 mA plus about 0.43 mW typical quiescent burden | cold-start hold-up and enclosure temperature |
| TPS/BQ and buck conversion | source admission reserves 15% of negotiated input before charging; system load always wins | treating the 15% reserve as a measured heat number or guaranteed efficiency |

The conversion stages dominate the remaining unknown because manufacturer
efficiency curves and thermal boards do not provide a guaranteed Leshy2 hot
limit. Inventing one summed junction temperature would be less rigorous than
the accepted 15% admission reserve plus measured per-scenario thermal map.
Paper closure therefore requires that every source is named and bounded by a
test, not that a nonexistent PCB measurement be fabricated.

## Fault/recovery ledger

| Fault class | Non-programmable result | Runtime authority |
|---|---|---|
| invalid/reversed/mismatched/deep cell | pack remains outside BAT/SYS; no linear recovery | report/refuse; no override |
| invalid/corrupt PD image or unsupported source | SafeMode; protected path and charge remain off | signed inactive-region recovery or fixture pads |
| weak source/DPM/thermal evidence | charge falls first, then optional loads; supplement only with admitted pack | may reduce further, never increase above evidence |
| AON raw OVLO | TPS25961 disconnects while OVLO persists; PG/SENSE keep POR asserted | observe only; no bypass |
| AON short/thermal | bounded TPS25961 hardware auto-retry; no sustained PG/SENSE/CT means no main | cannot accelerate retry or grant a session |
| main post-buck fault | TPS25974 latch-off; protected PG/fault aggregate drops | revoke leases; full source cycle required |
| voice post-buck fault | TPS25974 latch-off and STOP-dominant reset/PD/PTT remain safe | revoke voice session; validated domain power cycle only |
| accessory fault/backfeed | reverse-blocking TPS259470 latch-off, signals isolate first | explicit new session only; no retry loop |
| branch fault/off | independent reset-off switch/QOD; only active group remains powered | park pins before off; measured quiet threshold before reuse |
| hard STOP/evidence fault | I2 latch and physical gates dominate every software target | logging is best effort; re-arm remains physical |

## Remaining evidence register

| Gate | Owner/phase | Pass evidence | Reopen trigger |
|---|---|---|---|
| exact XTAR assembly documents | procurement/I8 | assembly/revision-matching UN38.3 transport evidence and regional compliance records | unavailable/mismatched documents select a new exact cell and reopen charge/fit/cost |
| received cell/1048P/NTC lot | prototype/I3 HIL | insertion, polarity block, four-contact isolation, NTC coupling, bounce and replacement-cycle traces | fit/contact/thermal failure reopens holder/cell profile |
| diagnostic qualification | prototype/I3 HIL | calibrated 25…50-ms pulse, 350…860-ms hardware lockout and droop distributions over SoC/temp/aging | nuisance reject, unsafe acceptance or hot copper |
| source transitions | prototype/I3 HIL | USB 5/9/15-V attach/remove, battery-only, USB-only, supplement, weak-source DPM and cell removal without unsafe rail pulse/backfeed | reset/chatter/backfeed or charge before valid evidence |
| rail electrical | prototype/I3 HIL | cold/hot startup, continuous/transient load, discharge, ripple/EMI, no nuisance trip and protected PG timing | accepted scenario exceeds voltage/current/quiet envelope |
| destructive containment | controlled fixture/I3 HIL | short and raw-overvoltage injections keep protected peak/energy inside consumer limits and fail safely | cutoff/copper/load damage or uncontrolled retry |
| thermal map | prototype/I3 HIL | worst legal scenario and fault repetition over qualified ambient keep cells, silicon, magnetics, resistors, contacts and enclosure below their limits with margin | derating or mode restriction would change target function |

These gates remain mandatory even though the paper block closes. Results are
recorded against the exact board revision, cell lot, firmware build and test
fixture; one passing room-temperature sample cannot satisfy the table.

## Review result

I3 has no remaining paper architecture choice, hidden component, unbudgeted
rail or unassigned fault. Its exact circuits, source truth, paper loss ledger,
runtime authority and reopen conditions receive **«Проведено ревью»** for
paper electrical scope. All physical/lot evidence above remains open and
visible. I4 paper work may begin; integrated mockup, BOM freeze and KiCad do
not.

