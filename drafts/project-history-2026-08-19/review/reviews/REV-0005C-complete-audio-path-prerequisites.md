# REV-0005C — complete audio-path prerequisites review

- Статус: **Проведено ревью фактов; последующий owner choice закрыт DEC-0054**
- Дата: 2026-08-17
- Artifact: [`AUDIO-0002`](../architecture/AUDIO-0002-complete-audio-path-comparison.md)
- Findings: [`FND-0066`](../findings/FND-0066-es8311-line-input-and-pam-differential-capability.md),
  [`FND-0067`](../findings/FND-0067-audio-source-select-and-reset-bypass.md)
- Proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)

## Проверено

- Legacy Si4732/SA518 mux, PAM8302A input circuit, electret/SA518 MIC_IN path
  and all three required selector functions were traced end to end.
- Direct ES8311 input loading is not a zero-loss ADC tap; passive and active
  capture branches are separated honestly.
- PAM8302A differential input removes the need for a central DAC
  differential-to-single-ended amplifier; TX still needs its own one-leg
  attenuation and selection.
- Current SA518 evidence gives about `700 mV/200 Ω` AFOUT and about `10 mV`
  typical modulation sensitivity, proving that codec TX needs attenuation.
- Current TAC5111IRGER status, exact 24 pins plus corner/thermal grounds,
  4×4-mm package, line/mic input modes, 5/10/40-kΩ input selections and current
  distributor price were checked. Its six digital bus contacts fit the existing
  S3 GPIO map, but current Espressif supported-device list has no TAC5111 driver.
- The existing RX-source control omission was corrected on P27; slow accounting
  now closes at `24/0/0`.
- External pulls on P11/P12 cannot guarantee bypass across S3-only reset while
  TCA6424 remains powered. One direct arm plus dual gate is a complete leading
  closure and consumes one, not both, free S3 GPIO.
- Common selectors, PTT independence, power-off isolation and measured
  schematic/HIL gates are included in every viable candidate rather than
  credited only to the recommendation.

## Саморевью рекомендации

E2-B is the best prototype baseline: it preserves the supported ES8311 driver,
does not load the ordinary bypass, and makes the passive E1-P version a later
measured cost-down rather than an optimistic first build. TAC5111 is a strong
technical reference but does not remove external fail-safe selectors, may still
need a high-impedance input network, costs materially more and adds a new
driver. Choosing it now would conflict with the zero-loss cost objective without
buying a required product capability.

## Несоответствия, найденные и исправленные в этом review

| Draft mismatch | Исправление |
|---|---|
| Preliminary `PAM8302AASCR` row misplaced contacts 2–4 | Rechecked current Diodes MSOP-8 top view and corrected the machine source/test to `1 SD, 2 NC, 3 IN+, 4 IN−, 5 VO+, 6 VDD, 7 GND, 8 VO−` |
| Preliminary TS5A63157 description called it a 1-Ω switch | Corrected to manufacturer value `12 Ω`; exact `TS5A63157DCKR` SC70-6 contact map remains valid and 12 Ω is negligible only subject to the high-impedance TX network calculation |
| Preliminary package/revision metadata mixed body and lead-span dimensions | Replaced it with current manufacturer document revisions and nominal body sizes for the exact DBV/DCK order codes |

The one-pin `AUDIO_ARM` gate is preferred over spending both free S3 GPIO on
selectors or resetting the entire slow plane. It also provides a direct
firmware escape from a stuck I2C/expander state while leaving GPIO43 available.

## Итог

The prerequisite and comparison artifact receives **«Проведено ревью»**. It
did not itself accept implementation. The owner later accepted `IMP-0046/A`
as `DEC-0054`; propagation is reviewed in `REV-0005D`, followed by the
still-open exact schematic calculations and HIL.
