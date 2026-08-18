# SAFE-0002 — принятая AON STOP/evidence circuit boundary

- Статус: **Проведено ревью `I2`; nRF and native S3/C5 evidence amended/reviewed by `DEC-0091/0092`; other I6/HIL open**
- Дата фиксации: 2026-08-18
- Decision: [`DEC-0061`](../decisions/DEC-0061-aon-stop-and-per-path-tx-evidence.md)
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)
- Device source: [`devices.json`](../../../hardware/architecture/devices.json)
- Prerequisite review: [`SAFE-0001`](SAFE-0001-aon-stop-and-tx-evidence-options.md)
- Finding: [`FND-0071`](../findings/FND-0071-hard-stop-and-tx-evidence-coverage.md)

## Граница артефакта

Этот документ закрывает бумажный `I2`: exact first-target active devices,
непрограммируемую truth table, fan-out, default pulls, fault behavior и
контрольные точки. Он не подменяет schematic capture и не объявляет
измеренными RF/IR thresholds. Источник/hold-up `AON_SAFE_3V3` and the exact
main-release chain subsequently close at paper level in `PWR-0019/DEC-0080`;
branch load switches и thermal/loss budget относятся к `I3`. The three nRF
paths now close through `N24E-0001`; native S3/C5 feeds close through
`NAT-0001`; CC/voice RF taps, every measured threshold and the optical analog
front end remain in `I6`.

## Непрограммируемая STOP-цепь

| Instance | Exact MPN | Роль | Критичные exact contacts |
|---|---|---|---|
| `safe_supervisor` | `TPS3808G33DBVR` | AON brownout/POR | `1 RESET_N`, `3 MR_N`, `4 CT`, `5 SENSE`, `6 VDD` |
| `safe_conditioner` | `74LVC2G14GW,125` | Schmitt conditioning STOP/RE-ARM | `1A→1Y`, `2A→2Y` |
| `safe_por_or` | `74LVC1G32GV,125` | STOP-dominant clear combination | `1A,1B→1Y` |
| `safe_latch` | `SN74LVC1G74DCUR` | asynchronous STOP latch | `1 CLK`, `2 D`, `3 /Q`, `5 Q`, `6 /CLR`, `7 /PRE` |
| `safe_reset_buffer` | `SN74LVC3G34DCUR` | Ioff reset fan-out | `1A→1Y`, `2A→2Y`, `3A→3Y` |
| `safe_gate_a` | `SN74LVC08APWR` | 3×nRF CE + nRF rail | four independent `A·B→Y` channels |
| `safe_gate_b` | `SN74LVC08APWR` | CC/voice rails + IR + accessory | four independent `A·B→Y` channels |
| `safe_ptt_or` | `74LVC1G32GV,125` | active-low voice PTT force-RX | `PTT_REQ_N OR TX_KILL` |
| `stop_led` | `LTST-C190KFKT` | independent orange STOP indicator | `Q → 2.2 kΩ → A`; `K → GND` |

`AON_SAFE_3V3` supplies every device in this table. All selected LVC logic
outputs use partial-power-down `Ioff`; loss of their supply therefore does not
back-power application domains.

### Inputs and truth equation

- STOP is a normally-closed contact to safety ground. `STOP_LOOP_SENSE` has a
  `10 kΩ` pull-up to AON and `10 nF X7R` to ground. Healthy/closed is low;
  pressing STOP, disconnecting the contact or opening a wire is high.
- Conditioner channel 1 produces active-low `STOP_ASSERT_N` and drives `/PRE`.
- RE-ARM is a separate recessed normally-open contact to safety ground.
  `REARM_RAW` has a `47 kΩ` pull-up and `100 nF X7R`; conditioner channel 2
  produces a positive clock edge on a fresh press.
- D is fixed low through `10 kΩ`. `Q=TX_KILL`; `/Q=RUN_PERMIT`.
- Supervisor `CT=10 nF C0G`, giving approximately `57.6 ms` typical POR delay.
  `MR_N` is now driven directly by exact pulled-up `TPS629203.PG`;
  open-drain `POR_N` uses one exact `10 kΩ` AON pull-up and directly enables
  main against an exact 100-kOhm fail-low pull.
- The clear equation is `CLR_N = POR_N OR STOP_LOOP_SENSE`. Therefore an open
  STOP loop makes `/CLR` inactive before/as `/PRE` asserts and avoids the
  forbidden simultaneous asynchronous preset+clear state.

| State/event | `TX_KILL` | Result |
|---|---:|---|
| cold valid AON, STOP healthy | 0 after POR | new boot; every TX arm/lease remains cleared |
| STOP pressed/open wire | 1 asynchronously | three compute resets low; every TX gate safe |
| STOP released | 1 | latched; no boot or restored session |
| fresh RE-ARM after release | 0 | new TX-off boot |
| RE-ARM held during STOP | 1 | preset dominates; release does not create a clock edge |
| AON brownout/loss | safe by pulls | no output can become a run/enable command |

Power cycling remains the second physical re-arm route already accepted for
the product, but always starts a fresh TX-off session.

### Three-domain reset fan-out

All three `SN74LVC3G34DCUR` inputs receive `RUN_PERMIT`; outputs drive S3
`CHIP_PU`, C5 `CHIP_PU` and RP `RUN`. Every target has `47 Ω` series resistance
from the buffer and a local `1 kΩ` pull-down. Application-side pull-ups are
forbidden unless they are at least `10 kΩ`.

With the buffer unpowered and a worst allowed `10 kΩ` pull-up to `3.3 V`, the
target voltage is `3.3 × 1/(10+1) ≈ 0.30 V`. This is below the conservative
`0.8 V` low ceiling used for paper review; exact module specimen thresholds and
release waveforms remain fault-injection/HIL measurements.

## TX gate fan-out

Each active-high output has its own `10 kΩ` pull-down at the controlled
endpoint. `RUN_PERMIT` is the second AND input; one stale request cannot defeat
STOP. The active-low SA518 PTT output instead has a `10 kΩ` module-side pull-up.

| Request source | Exact gate channel | Safe output | Downstream exact-part gate |
|---|---|---|---|
| RP `GPIO1 NRF0_CE_REQ` | `safe_gate_a.1` | `NRF0_CE_SAFE` | exact switched-rail `74LVC126APW,118` then nRF0 CE |
| RP `GPIO4 NRF1_CE_REQ` | `safe_gate_a.2` | `NRF1_CE_SAFE` | exact switched-rail `74LVC126APW,118` then nRF1 CE |
| RP `GPIO7 NRF2_CE_REQ` | `safe_gate_a.3` | `NRF2_CE_SAFE` | exact switched-rail `74LVC126APW,118` then nRF2 CE |
| RP `GPIO15 NRF_GROUP_PWR_EN` | `safe_gate_a.4` | `NRF_GROUP_PWR_EN_SAFE` | exact `TPS22919DCKR`, Ioff buffers and detector-hold circuit reviewed in `DEC-0091` |
| RP `GPIO23 CC_PWR_EN` | `safe_gate_b.1` | `CC_PWR_EN_SAFE` | load switch/isolation in `I3/I6` |
| slow `P13 VOICE_DOMAIN_REQ` | `safe_gate_b.2` | `VOICE_DOMAIN_EN_SAFE` | 4-V rail stage in `I3/I5` |
| C5 `GPIO6 IR_TX_CARRIER` | `safe_gate_b.3` | `IR_TX_CARRIER_SAFE` | LED driver in `I6` |
| slow `P17 U214_5V_REQ` OR `P05 UNIT_5V_REQ` | exact request OR then `safe_gate_b.4` | `EXT_ANY_5V_EN_SAFE` | shared fixed-5-V buck; exact dual AND then independently enables each reverse-safe eFuse per `DEC-0098` |
| RP `GPIO18 VOICE_PTT_REQ_N` | `safe_ptt_or` | `VOICE_PTT_SAFE_N` | exact SA518 pin 14 |

S3/C5 native radios are stopped by their module resets. RP reset additionally
stops the owner of nRF/CC/voice/U214, while the external gates cover stale
outputs and rail states independently.

## Eight physical evidence channels

| Index | Path | Exact detector | Comparator/contact | Direct mirror |
|---:|---|---|---|---|
| 0 | S3 2.4 GHz | `CP0603Q5425ENTR` → `LTC5532ES6#TRMPBF` | `cmp_a IN1/OUT1` | slow `P23` |
| 1 | C5 2.4/5 GHz | `CP0603Q5425ENTR` → `LTC5532ES6#TRMPBF` | `cmp_a IN2/OUT2` | C5 `GPIO23` |
| 2 | nRF0 | `DC2337J5010AHF` → `AD8314ACPZ-RL7` | `cmp_a IN3/OUT3` | source mask |
| 3 | nRF1 | `DC2337J5010AHF` → `AD8314ACPZ-RL7` | `cmp_a IN4/OUT4` | source mask |
| 4 | nRF2 | `DC2337J5010AHF` → `AD8314ACPZ-RL7` | `cmp_b IN1/OUT1` | source mask |
| 5 | CC1101 | final-line resistive sample → `AD8314ACPZ-RL7` | `cmp_b IN2/OUT2` | source mask |
| 6 | SA518 voice | 5.1-kΩ/52.3-Ω sample → `AD8314ACPZ-RL7` | `cmp_b IN3/OUT3` | source mask |
| 7 | IR optical | `VEMD1060X01` | `cmp_b IN4/OUT4` | C5 `GPIO24` |

`evidence_cmp_a/b` are two exact `TLV1824PWR` quad open-drain comparators on
AON. Each output is `EV_N[i]`, active low, with a `10 kΩ` AON pull-up. RF
detector output goes to the inverting comparator input; the separately
calibrated threshold/hysteresis network goes to the non-inverting input.
The CC and voice paths are amended by `DEC-0093/DEC-0094`: each separate
`AD8314` is pre-armed from its STOP-qualified rail request and a
diode/10-kΩ/1-uF node retains `ENBL` for approximately 10 ms after application
rail fall. The S3/C5 paths are amended by
`NAT-0001/DEC-0092`: independent `CP0603Q5425ENTR` couplers sit after real
module-to-PCB U.FL links, their `50 OHM` lands receive 49.9-Ohm terminations,
and their samples reach `LTC5532` through exact 39-pF C0G DC blocks. Each
detector uses matched `10 kΩ 1%` feedback/ground resistors for `2×` gain,
grounded `VOS`, exact 33-pF output loading and 100-nF local bypass. C5 `ANT2`
remains default-disabled/no-connect; only `ANT1` feeds its evidence path.
The three nRF paths are amended by `N24E-0001/DEC-0091`: exact 10-dB
directional couplers feed AON `AD8314` measurement-mode `V_UP`; a common
diode/10-kOhm/1-uF node keeps ENBL asserted through nRF QOD fall and then
returns all three detectors to low-current shutdown. Channels 0/100/125 still
require measured thresholds.

`TCA9534APWR` is fixed at seven-bit address `0x38` on the local side of RP I²C0,
before `TCA4307`: `P0…P7 = EV_N[0…7]`. Its `INT_N` is a test point only. Source
attribution may fail with I²C, but the physical aggregate cannot.

Four exact `BAT54ALT1G` dual-common-anode arrays isolate pairs `0/1`, `2/3`,
`4/5`, `6/7`. Their common anodes join `RP_ANY_TX_N`, pulled up by `10 kΩ`.
The same node sinks current from `AON → 2.2 kΩ → LTST-C190KRKT`, so any asserted
comparator lights the red indicator and pulls RP `GPIO22` low without firmware.
The selected onsemi array replaces initially screened `BAT54A,215`: the latter
had zero DigiKey/Mouser stock in the dated check, while `BAT54ALT1G` was active
and stocked by both distributors.

U214 and later accessories keep RF/antenna hardware on the accessory. Without
their own qualified evidence output the state is explicitly
`unknown/unavailable`; proof-mandatory TX stays disabled or fixture-only.

## AON rail and exact power boundary

Detectors, comparators, source-mask expander and both critical LEDs stay on
`AON_SAFE_3V3`; STOP therefore does not erase its own evidence. `I3` must now
select the rail source/hold-up and prove its continuous current. The base
first-target load is approximately:

- two continuously enabled LTC5532: `2 × 0.50 mA = 1.00 mA`;
- three AD8314: about `3 × 20 uA = 0.06 mA` while the nRF domain is parked,
  rising from `3 × 4.5 mA = 13.5 mA` typical to the listed
  `3 × 5.7 mA = 17.1 mA` maximum during nRF operation/hold;
- two additional AD8314: about `2 × 20 uA = 0.04 mA` while CC/voice are parked,
  rising to `2 × 4.5 mA = 9.0 mA` typical during their individually exclusive
  active/hold windows;
- eight TLV1824 channels: about `0.04 mA` typical total;
- supervisor/logic/expander idle plus pull networks: budget `0.50 mA` until
  measured;
- indicator current only while active: about `0.5…0.7 mA` each.

Thus `I3` reserves **at least 5 mA continuous and 30 mA transient** for safety
electronics before tolerance, cold/temperature and hold-up margin. It may
increase this budget, never silently reduce it.

## Named test points

`TP_AON_SAFE_3V3`, `TP_STOP_LOOP_SENSE`, `TP_STOP_ASSERT_N`, `TP_REARM_RAW`,
`TP_REARM_CLK`, `TP_POR_N`, `TP_TX_KILL`, `TP_RUN_PERMIT`, `TP_S3_RUN`,
`TP_C5_RUN`, `TP_RP_RUN`, `TP_NRF0_CE_SAFE`, `TP_NRF1_CE_SAFE`,
`TP_NRF2_CE_SAFE`, `TP_NRF_RAIL_EN_SAFE`, `TP_CC_RAIL_EN_SAFE`,
`TP_VOICE_RAIL_EN_SAFE`, `TP_VOICE_PTT_SAFE_N`, `TP_IR_TX_SAFE`,
`TP_EXT_5V_EN_SAFE`, `TP_EV_N0…TP_EV_N7` and `TP_RP_ANY_TX_N` are mandatory
exposed copper pads in the prototype. They are test geometry, not front-panel
connectors and require no GPIO.

## Fault review and downstream pass conditions

| Fault | Paper result | Remaining physical proof |
|---|---|---|
| STOP pressed during every TX path | asynchronous kill/gates | latency and RF/optical decay at test points |
| one MCU hung or one request stuck | STOP remains independent | fault injection for each request/output |
| I²C or evidence expander stuck | aggregate LED/GPIO still direct | short/open bus injection |
| AON brownout/loss | Ioff + local pulls force reset/off | ramp, droop, back-power and release traces |
| one comparator asserted | source bit + aggregate assert | threshold, pulse width, LED/GPIO low voltage |
| STOP loop opened | fail-safe assertion | contact/cable disconnect |
| STOP sense shorted to ground | STOP can be masked | explicit HIL detection case; no dual-fault claim |
| remaining RF tap/front end absent/unqualified | evidence unknown | affected TX profile blocked until `I6/HIL` pass |

The remaining tests are named and owned; they do not reopen the accepted logic
topology unless measurements disprove its electrical assumptions.

## Availability snapshot for added closure parts

Checked 2026-08-18 because these exact order codes are newly selected:

- `SN74LVC3G34DCUR`: TI `ACTIVE`, partial-power-down `Ioff`; DigiKey and Mouser
  showed stock ([TI](https://www.ti.com/product/SN74LVC3G34),
  [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC3G34DCUR/484593));
- `BAT54ALT1G`: onsemi active common-anode dual; DigiKey and Mouser showed stock
  ([onsemi datasheet](https://www.onsemi.com/download/data-sheet/pdf/bat54alt1-d.pdf),
  [DigiKey](https://www.digikey.com/en/products/detail/onsemi/BAT54ALT1G/917808));
- `LTST-C190KRKT` and `LTST-C190KFKT`: active Lite-On 0603 indicators with
  broad distributor stock ([red datasheet](https://optoelectronics.liteon.com/upload/download/DS-22-99-0151/LTST-C190KRKT.PDF),
  [orange DigiKey](https://www.digikey.com/en/products/detail/liteon/LTST-C190KFKT/386812)).
- `CP0603Q5425ENTR`, `U.FL-R-SMT-1(10)` and `GRM1555C1H390JA01D`: exact
  S3/C5 coupler, PCB receptacle and RF input DC block were checked at selection
  and had authorized distributor stock; full evidence is in
  [`NAT-0001`](NAT-0001-exact-s3-c5-native-rf-evidence-endpoints.md).

All earlier option-A active devices retain the dated availability evidence in
[`SAFE-0001`](SAFE-0001-aon-stop-and-tx-evidence-options.md). Availability is
a sourcing snapshot, not a lifecycle guarantee or authorization to freeze BOM.
