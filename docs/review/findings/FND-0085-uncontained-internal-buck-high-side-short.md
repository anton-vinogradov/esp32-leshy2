# FND-0085 — internal buck high-side shorts were not independently contained

- Статус: **Исправлено независимыми post-buck protection boundaries**
- Дата: 2026-08-18
- Correction: [`PWR-0020`](../architecture/PWR-0020-independent-post-buck-containment.md)
- Decision: [`DEC-0081`](../decisions/DEC-0081-independent-internal-rail-containment.md)
- Review: [`REV-0005AL`](../reviews/REV-0005AL-internal-rail-containment-propagation.md)

## Finding

The accepted AON, main and voice rails had converter overload protection and
downstream branch switches, but no independent series element between each
buck output and its load. A shorted buck high-side switch could therefore
connect `BQ25798 SYS` to a low-voltage load rail while the failed converter's
own controller was unable to turn that switch off.

That is a materially different fault from an ordinary output overload. An
upstream fuse/current limit bounds current but not rail voltage, and a
downstream branch switch does not protect the always-connected compute or
safety loads. In particular, the AON domain contains 3.3-V devices whose
tightest recorded absolute-maximum supply is 4.0 V, while the main domain has
3.6-V-class loads. The pre-existing AON supervisor observed the same
uncontained output and therefore was not an independent disconnect.

## Correction

Every internal converter output is split into raw and protected nets:

- `AON_RAW_3V3 → TPS25961DRVR → AON_SAFE_3V3`;
- `MAIN_RAW_3V3 → TPS25974LRPWR #MAIN → 3V3_MAIN`;
- `VVOICE_RAW_4V → TPS25974LRPWR #VOICE → protected VVOICE_4V`.

The AON supervisor, POR pulls and safety loads move to the protected AON side.
Main/voice operational fault evidence comes only from protected-side eFuse PG;
raw converter PG remains a fixture-only diagnostic point. Exact OVLO, current,
slew, timer and PGTH passives are machine-instantiated, and firmware has no
control that can bridge or disable these boundaries.

The correction adds no GPIO and no product mode. Paper calculations and the
single-fault direction receive review; trip waveforms, component temperature,
load-step margin and destructive-fault containment remain prototype HIL.

