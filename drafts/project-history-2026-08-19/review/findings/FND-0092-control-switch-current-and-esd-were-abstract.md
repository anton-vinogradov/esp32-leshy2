# FND-0092 — control switch current and ESD were still abstract

- Status: **исправлено; Проведено ревью paper electrical boundary**
- Scope: ordinary controls, PTT, hard STOP and RE-ARM
- Architecture: [`UI-0002`](../architecture/UI-0002-exact-switch-and-control-protection.md)

## Finding

`UI-0001` restored the complete control inventory and pin fit, but every
discrete button remained an abstract contact. That hid three materially
different requirements:

1. the 10-kOhm ordinary-matrix and PTT paths switch only about 0.3 mA;
2. the 47-kOhm RE-ARM path switches only about 70 uA;
3. the normally-closed STOP path is safety relevant and must remain reliable
   at 3.3 V while a broken conductor asserts STOP.

A standard tactile switch with a 1-mA minimum load was therefore not a valid
drop-in choice. `D2F-01` was also screened and rejected for STOP: its primary
datasheet gives a minimum applicable load of 1 mA at 5 V, while the accepted
3.3-V/10-kOhm loop supplies only about 0.33 mA. Raising the AON voltage or
pretending the contact floor did not exist would have reopened the reviewed
safety rail for no product benefit.

The former abstraction also omitted an explicit ESD return for user-operated
controls. That was inconsistent with the already protected USB, display and
microSD endpoints.

## Correction

- Nine discrete ordinary controls, direct PTT and recessed RE-ARM now use
  exact order code `C&K Y78B23214FP` (`KMR232G ULC LFS`). Its ULC specification
  permits 1 uA at 1.8 V; all three accepted current levels exceed that floor.
- Hard STOP now uses exact `Panasonic AEQ10410`, a gold-clad SPDT low-level
  switch qualified from 100 uA at 3 V. COM+NC preserves open-wire assertion;
  the existing 10-kOhm AON pull-up meets its floor without a rail change.
- `TPD8E003DQDR` protects all eight UI-expander contacts. Separate
  `TPD4E05U06DQAR` instances protect encoder/PTT and STOP/RE-ARM; the safety
  instance returns only to safety ground.
- Exact pull-up, filter and series parts replace the former abstract PTT,
  STOP and RE-ARM networks in the machine route table.

Cap/plunger coupling, guarding, sealing, AEQ10410 chassis mounting and short
harness strain relief remain physical HIL. The correction does not authorize
KiCad or freeze the enclosure.

## Primary sources

- [C&K KMR2 datasheet](https://www.ckswitches.com/media/1479/kmr2.pdf)
- [Panasonic AEQ10410 product specification](https://industry.panasonic.com/global/en/products/control/switch/micro-non-seal/number/aeq10410)
- [TI TPD8E003 datasheet](https://www.ti.com/lit/ds/symlink/tpd8e003.pdf)
- [TI TPD4E05U06 datasheet](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf)
