# DEC-0087 — exact control switch and protection endpoint

- Status: **accepted under delegated no-material-function/cost rule; Проведено ревью paper electrical endpoint**
- Finding: [`FND-0092`](../findings/FND-0092-control-switch-current-and-esd-were-abstract.md)
- Architecture: [`UI-0002`](../architecture/UI-0002-exact-switch-and-control-protection.md)
- Propagation review: [`REV-0005AR`](../reviews/REV-0005AR-exact-control-switch-protection-propagation.md)

## Decision

1. Retain the complete local-control set accepted by `DEC-0086` without
   merging or removing D-pad, F1, F2, PTT, STOP or RE-ARM.
2. Use exact `C&K Y78B23214FP` for the nine discrete ordinary buttons, direct
   PTT and recessed RE-ARM. Its ULC range is mandatory; a pin-compatible
   standard-current tactile part is not an automatic substitute.
3. Use exact `Panasonic AEQ10410` for hard STOP. COM+NC is the only functional
   throw; NO is left open. Keep the accepted 10-kOhm/10-nF AON circuit because
   its 0.33-mA nominal contact current satisfies the switch's 100-uA-at-3-V
   low-level range.
4. Protect P0…P7 with one exact `TPD8E003DQDR`; protect encoder/PTT with one
   existing-family `TPD4E05U06DQAR`; protect STOP/RE-ARM with a separate
   `TPD4E05U06DQAR` returned only to safety ground.
5. Instantiate exact PTT 10-kOhm/100-nF/1-kOhm, STOP 10-kOhm/10-nF and RE-ARM
   47-kOhm/100-nF components in the machine map.

## Consequences

- MCU, expander and control-function budgets do not change.
- The earlier `D2F-01` direction is rejected because the actual 3.3-V loop was
  below its documented 1-mA-at-5-V minimum applicable load.
- AEQ10410 adds a safety-specific part rather than forcing a 5-V AON rail; its
  checked quantity-1000 price is about USD 2.60. This is accepted as a bounded
  reliability correction, not a feature addition.
- Exact cap/guard/harness/enclosure mechanics and ESD/bounce/fault HIL remain
  open. The decision does not authorize KiCad or restart the whole mockup.
