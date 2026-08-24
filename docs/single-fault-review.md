# Single-fault review

`H3.6.2` is reviewed: 30 scenarios and 25 machine checks pass. The exact marker is `H3.6.3`.

Every fault records detection, the primary shutdown path, an independent or fail-safe path, the safe result and recovery. Automatic restart is forbidden.

| Domain | Single fault | Result |
|---|---|---|
| physical command | RUN moved to KILL or RUN conductor opens | all TX gates become safe; C5/RP reset; no automatic restart |
| physical command | RUN_LOOP_RAW is shorted in the permissive state | the single masking short cannot defeat KILL |
| fault plane | FAULT_ASSERT_N pull-up opens | safe latched shutdown |
| fault plane | FAULT_ASSERT_N is stuck low | safe no-start |
| fault plane | FAULT_ASSERT_N is stuck at the permissive level before RUN | safe no-admission with S3 held in fault/reset mode |
| application | S3 application or system heartbeat stops | bounded hard shutdown and retained reason |
| safety controller | safety-controller firmware hangs | bounded hard shutdown |
| AON supply | AON voltage browns out or disappears | immediate safe state; final journal write may be unavailable |
| primary latch | RUN_PERMIT latch/output is stuck permissive | hazardous endpoints lose command or power |
| processor reset | one primary C5 or RP reset driver is stuck released | processor held reset by the independent sink |
| processor reset | one direct FAULT_ASSERT_N reset sink is stuck released | processor and transmitters remain contained |
| nRF24 power | primary nRF rail gate is stuck high | all three nRF24 rails/CE paths are contained without losing full-mix capability |
| nRF24 power | nRF backup gate is stuck high | nRF group remains off for the single backup-gate fault |
| nRF24 power | nRF load switch is shorted on | a switch short alone cannot command TX; actual TX is caught by physical evidence |
| CC1101 power | primary CC rail gate is stuck high | CC rail and command path become safe |
| CC1101 power | CC backup gate or load switch is stuck permissive | the fault alone cannot create an authorized command |
| voice power | voice buck enable is stuck permissive | protected voice rail and PTT become safe |
| voice power | voice eFuse fault clamp is stuck released | voice transmitter loses rail or PTT |
| voice PTT | module-side PTT is stuck active | uncommanded voice TX is energy-bounded |
| external power | common external 5-V converter gate is stuck on | U214 and Unit branches both turn off independently of the common buck |
| external branch | one branch gate/eFuse is stuck permissive | the single failed branch cannot retain base-supplied power after common shutdown |
| IR transmitter | IR carrier safety gate is stuck permissive | IR emitter loses both command and supply |
| IR transmitter | IR TPS22919 load switch is shorted on | a rail short alone cannot produce optical TX |
| TX supervision | actual RF/IR TX occurs without a valid lease | all transmitter gates are shut and the source identity is journaled |
| TX evidence | one comparator/output is stuck active-low | safe nuisance shutdown |
| TX evidence | one comparator/output is stuck inactive or unreadable | safe no-admission for the affected transmitter |
| thermal sensing | one NTC is open or shorted | all hazardous power/TX is shut down |
| thermal sensing | one NTC is plausibly stuck in-range | the sensor fault alone cannot create heat; the affected high-power profile is blocked |
| power protection | one eFuse/load path fails open | safe loss of function |
| fault record | power disappears during journal commit | no fabricated cause is shown |

## Corrections

- `H3.6.2-F01` — separate direct FAULT_ASSERT_N reset sinks, nRF/CC backup gates, voice eFuse clamp, expansion-branch qualification and the shared reset-off IR rail were fitted
- `H3.6.2-F02` — unused TCA9535 P11 and its existing resistor position became a 100-kOhm series-isolated startup proof input
- `H3.6.2-F03` — the second SPDT throw now reaches FAULT_ASSERT_N through the already fitted spare SN74LVC3G07 channel as well as requesting pack shutdown

## Result boundary

Not claimed: two simultaneous independent faults or a first latent safety fault followed by a second hazard; common physical damage that shorts both independent shutdown routes or bypasses a protected rail directly; guaranteed final diagnostic write after complete AON loss; production-safe timing, RF silence or temperature without H6 layout and H8 measured fault injection.

[Machine evidence](../hardware/verification/generated/H3-VRF62-fault-tree.json).
