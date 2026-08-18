# UI-0001 — complete local-control topology

- Status: **Проведено ревью for control inventory and principled pin fit**
- Finding: [`FND-0090`](../findings/FND-0090-required-local-controls-were-dropped.md)
- Decision: [`DEC-0086`](../decisions/DEC-0086-complete-local-controls-and-direct-encoder.md)
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)

## Required physical inventory

| Class | Physical controls | Transport |
|---|---|---|
| ordinary navigation/action | D-pad UP/DOWN/LEFT/RIGHT + OK, BACK, OPT, F1, F2 | diode-isolated 4×3 matrix |
| rotary | encoder A/B + push | A/B direct PCNT0; push in matrix |
| foreground voice | hold-to-talk PTT | direct RP GPIO21 |
| safety | normally-closed STOP | independent AON latch input |
| safety recovery | recessed normally-open RE-ARM | independent AON conditioned input |

Touch and paired-phone text entry are additional paths. Neither path removes a
physical control or becomes the only way to cancel, navigate or select.

## Matrix and exact paper parts

Dedicated `TCA9534APWR` uses P0…P3 as rows and P4…P6 as columns. P7 is routed
to a local growth pad and reserved. A0/A1/A2 are strapped high for candidate
7-bit address `0x3F`; the complete assembled-bus address scan remains HIL.
The device powers up with every P-port as an input. Exact
`RC0603FR-071KL` 1-kOhm pull-downs therefore hold all rows low from reset, and
firmware keeps all rows low in idle. Any press then pulls one independently
10-kOhm-high column low and asserts the open-drain interrupt without polling.
Initialization writes the P0…P3 output latches low before changing those four
ports from reset inputs to outputs, so their reset-default high latch value is
never exposed as an all-high idle state.

| Row | Column 0 | Column 1 | Column 2 |
|---|---|---|---|
| 0 | D-pad UP | D-pad DOWN | D-pad LEFT |
| 1 | D-pad RIGHT | OK | BACK |
| 2 | OPT | F1 | F2 |
| 3 | encoder push | empty | empty |

Each populated position has its own onsemi `1N4148WT`, quantity ten. After an
interrupt, firmware drives the selected row low and the other three high,
samples all columns, advances through all four rows, then restores every row
low. At 3.3 V each high row is externally limited by 1 kOhm to at most 3.3 mA,
and the three simultaneously high rows to at most 9.9 mA. This is below the TI
limits of 10 mA per high P-port and 80 mA total sourced P-port current. Actual
VOH, diode/VIL margin and transient behavior remain electrical/HIL gates.
Firmware applies qualified debounce/multi-key semantics.
PTT, STOP and RE-ARM never enter this scan.

## Encoder fast path

The first mechanical target is active `Alps Alpine EC11E18244AU`: 36 detents,
18 pulses and integrated push. Its real A/C/B/D/E contacts are registered in
the machine source. A→S3 GPIO39 and B→S3 GPIO47 use hardware PCNT0 with exact
`RC0402FR-073K32L` 3.32-kOhm pull-ups (approximately 1 mA closed-contact current
at 3.3 V); common C is ground and the D/E push contact occupies matrix row 3,
column 0.

PCNT capture is necessary but not sufficient proof of correct feel. Firmware
must reject invalid Gray transitions and publish only qualified full-detent
events. The chip glitch filter alone is not claimed to absorb the encoder's
mechanical chatter. Fast rotation, temperature, EMI and simultaneous display,
storage and active-signal-group load must prove that no detent is lost or
invented.

## Touch IRQ relocation

Panel `TP_INT` is not documented deeply enough to assume polarity or output
type. One SC70-5 footprint therefore accepts:

- `SN74LVC1G07DCKR` as first target for active-low/non-inverting input;
- pin-compatible `SN74LVC1G06DCKR` for active-high/inverting input.

Both produce an open-drain contribution to the existing pulled-up `SYS_INT_N`
on S3 GPIO37. After any wake firmware reads every enabled source: TCA6424,
the dedicated TCA9534A, touch, TPS25751 and pack admission. The actual
HMX035CTFT-001 specimen must
identify controller, idle level, polarity, pulse persistence and recovery
before one population option is frozen. Polling-only touch is not accepted.

## Pin and cost result

- S3: `33 used / 3 reserved / 0 free`;
- C5: unchanged `14/6/1`;
- RP: unchanged `48/0/0` including direct PTT GPIO21;
- main slow I/O: `18 used / 0 reserved / 6 free`;
- dedicated UI matrix I/O: `7 used / 1 reserved / 0 free`;
- paper BOM delta excluding switch mechanics: approximately USD 0.95…1.15 at
  quantity 1000 for TCA9534APWR, touch adapter, one extra matrix diode and
  support passives; no additional MCU and the new expander MPN is already used
  elsewhere in the product BOM.

## Remaining gates

- exact ordinary, PTT, STOP and RE-ARM switch MPN/force/sealing/caps;
- encoder position with the rear U214 installed and shaft/cap access;
- complete physical SYS-I2C address scan and TCA9534A interrupt HIL;
- matrix ghosting, debounce, multiple presses, bounded scan current, wake and
  100-ms response HIL;
- encoder chatter/speed/EMI/concurrent-load HIL;
- touch IRQ polarity, shortest assertion and shared-source identification HIL.

This artifact closes inventory and principled pin fit only. It does not freeze
the enclosure, switch footprints, production BOM or KiCad.
