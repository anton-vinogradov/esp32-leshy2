# REV-0005A — HMX035CTFT-001 electrical-fit and propagation review

> Subsequent `DEC-0054/REV-0005D` assigns S3 GPIO6 to `AUDIO_ARM`; the
> display-only `31/3/2` snapshot below is historical and current total is
> `32/3/1`.

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Artifact: [`DSP-0005`](../architecture/DSP-0005-hmx035ctft-electrical-fit.md)
- Findings: [`FND-0063`](../findings/FND-0063-hmx035ctft-mpn-was-disclosed.md),
  [`FND-0064`](../findings/FND-0064-stale-s3-budget-in-stage-ledger.md)

## Проверка

- Official QDtech schematic, not a reseller inference, exposes assembly marking
  `HMX035CTFT-001` and the reviewed 40-contact map.
- `devices.json` records every physical contact; lifecycle text explicitly
  separates disclosed marking from production orderability.
- `G2F-3I` instantiates the assembly and terminates QSPI, touch I2C/IRQ and
  resets on exact contacts.
- QSPI needs no separate DC. Existing S3 `GPIO39` is reused as touch IRQ; at
  this display-only pass `GPIO6/GPIO43` remain free and S3 budget is `31/3/2`.
- Existing slow-plane `P06/P07` terminate exact display/touch reset contacts;
  no hidden P27 allocation was introduced.
- TE remains unassigned until measured A/B benefit; it is not treated as an
  unconditional requirement for menu/dirty-region rendering.
- Power, QSPI straps and backlight endpoints are visible; exact supply,
  current sink, ESD/protection and connector remain explicit blockers.
- Connector `FH12-40S-0.5SH(55)` is labelled candidate only because contact
  side/FPC thickness/tail drawing are not proved.
- Misleading near-matches `TTH348BVT-01CG` (172×640) and
  `KD035QVFID225-C086A` (MIPI) are rejected, not promoted by diagonal/
  resolution alone.
- Generated ledger and principled pinout are current. A regression test fixes
  the assembly, critical physical contacts, GPIO39 IRQ reuse, reset routes,
  QSPI straps and unchanged free-pin set.
- Stale `stages.md` S3 budget is corrected from `29/3/4` to `31/3/2`.

## Итог

Current exact-display **paper electrical fit получает статус «Проведено
ревью»**. Это materially reduces `FND-0060`, but does not authorize production
BOM or KiCad. The next display-specific advance requires a real specimen/FPC
drawing plus shared-bus, backlight, optics and sourcing qualification.
