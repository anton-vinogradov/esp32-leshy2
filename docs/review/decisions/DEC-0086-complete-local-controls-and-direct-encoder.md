# DEC-0086 — complete local controls and direct encoder capture

- Status: **accepted; Проведено ревью for inventory and principled pin fit**
- Finding: [`FND-0090`](../findings/FND-0090-required-local-controls-were-dropped.md)
- Architecture: [`UI-0001`](../architecture/UI-0001-complete-local-control-topology.md)
- Propagation review: [`REV-0005AQ`](../reviews/REV-0005AQ-local-controls-propagation.md)

## Decision

1. Retain D-pad directions plus OK, BACK, OPT, F1 and F2, the rotary encoder
   with push, dedicated PTT, independent hard STOP and recessed RE-ARM.
2. Put only the nine ordinary buttons and encoder push in a diode-isolated 4×3
   matrix on one dedicated exact `TCA9534APWR`: P0…P3 rows, P4…P6 columns and
   P7 local reserve. Use ten exact onsemi `1N4148WT` diodes. Hold all rows low
   in reset/idle so the first press produces a hardware interrupt; perform a
   bounded one-low/three-high row scan and restore idle afterwards.
3. Use exposed S3 GPIO39/GPIO47 and PCNT0 for encoder A/B. The matrix carries
   only encoder push and cannot delay or lose quadrature edges.
4. Use active `Alps Alpine EC11E18244AU` as the first encoder target; keep its
   final rear placement, feel and installed-U214 fit open.
5. Move panel TP_INT to existing `SYS_INT_N` through one SC70-5 footprint.
   Populate `SN74LVC1G07DCKR` for active-low or pin-compatible
   `SN74LVC1G06DCKR` for active-high only after specimen HIL proves polarity.
6. Keep PTT direct on RP GPIO21. Keep STOP and RE-ARM on their independent AON
   circuits; neither may be multiplexed into the UI matrix.

## Consequences

- S3 closes to `33 used / 3 reserved / 0 free`; main slow I/O becomes `18/0/6`
  and the dedicated UI expander is `7/1/0`.
- One already-used-family I²C expander is added, with an approximately
  USD 0.95…1.15 paper BOM delta including the touch adapter and support parts.
  This is accepted under the delegated no-material-cost-inflation rule because
  it restores interrupt-driven operation and six main slow-I/O contacts.
- Touch remains interrupt-driven and the full autonomous physical control set
  remains available without phone or touchscreen.
- Exact switch mechanics, address-collision scan, scan current, touch polarity,
  encoder placement and all UI HIL remain blockers. This decision does not
  authorize KiCad or enclosure freeze.
- `FND-0091` corrects the exact TCA9534A address table: all-high UI straps are
  candidate `0x3F`; the control topology and pin result are unchanged.
