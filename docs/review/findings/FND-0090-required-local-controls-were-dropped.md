# FND-0090 — required local controls were dropped by the inherited projection

- Status: **исправлено на бумажном уровне; switch mechanics and HIL open**
- Scope: I4 local controls and principled pin fit
- Decision: [`DEC-0086`](../decisions/DEC-0086-complete-local-controls-and-direct-encoder.md)
- Architecture: [`UI-0001`](../architecture/UI-0001-complete-local-control-topology.md)

## Finding

The old physical mockup contains nine ordinary labelled buttons: D-pad
directions plus OK, BACK, OPT, F1 and F2. It also contains an encoder with
push, a dedicated hold-to-talk PTT and a separate STOP. The zero-based target
text later replaced that inventory with encoder/BACK/HOME/OPTIONS and claimed
the old nine-button matrix was unnecessary. That was not a cost optimization;
it silently removed accepted controls.

The next display projection consumed former encoder GPIO40/41 with PWM and
QSPI D2. A 3×3 matrix could still hold only nine presses and therefore could
not restore both the nine ordinary buttons and encoder push. Treating touch or
phone input as the replacement would violate the accepted autonomous-control
boundary. Putting PTT or STOP into that matrix would additionally violate their
timing and safety boundaries.

## Self-review correction

The corrected topology retains the full inventory and changes only transport:

- one dedicated `TCA9534APWR` provides four rows, three columns, one local
  reserve and a real open-drain wake interrupt; all rows are low in reset/idle;
- ten onsemi `1N4148WT` devices isolate the nine ordinary buttons and encoder
  push in a 4×3 matrix;
- encoder A/B move to real exposed S3 GPIO39/GPIO47 and hardware PCNT0;
- display TP_INT moves through a pin-compatible open-drain polarity-adapter
  footprint into existing shared `SYS_INT_N` on GPIO37;
- PTT remains direct RP GPIO21; STOP and RE-ARM remain separate AON hardware.

The initially considered decoder was rejected during self-review: with all
outputs high while disabled, the matrix had no electrical path capable of
waking firmware for the first key press. Adding a wake sink would create a
push-pull conflict during scan. The dedicated expander costs more but preserves
interrupt-driven input and releases TCA6424 P00…P05. S3 becomes
`33 used / 3 reserved / 0 free`; main slow I/O becomes `18/0/6`, and the UI
expander is `7/1/0`.

## Remaining boundary

Ordinary/PTT/STOP/RE-ARM exact switch MPNs, force, sealing and placement remain
mechanical gates. Touch polarity/controller identity and full matrix/encoder
concurrent-load behavior remain HIL. The selected first encoder is not a
production mechanical freeze, and this correction does not authorize KiCad.
