# DEC-0091 — exact three-nRF electrical endpoint

- Status: **accepted under delegated non-dramatic cost/no function-loss rule; Проведено ревью subblock**
- Finding: [`FND-0096`](../findings/FND-0096-nrf-quiet-state-and-tx-evidence-were-not-physical.md)
- Architecture: [`N24E-0001`](../architecture/N24E-0001-exact-three-nrf-electrical-endpoint.md)
- Propagation: [`REV-0005AV`](../reviews/REV-0005AV-i6-three-nrf-propagation.md)

## Decision

1. Keep three independent, full-function `E01-ML01IPX` references on RP2354.
   The common power domain does not permit time-sharing or peer standby.
2. Insert one `74LVC126APW,118` and one `74LVC2G126DC,125` per radio, both
   powered by `3V3_NRF_GROUP`, with all six outputs source-terminated and both
   sides held in deterministic inactive states.
3. Complete the common `TPS22919DCKR` branch with exact input bypass, ON
   fail-low, QOD and independent module-local 10-uF/100-nF energy.
4. Use one `DC2337J5010AHF` plus `AD8314ACPZ-RL7` forward-power evidence path
   per radio. Terminate the isolated coupler port at 49.9 Ohm, match the
   detector with 52.3 Ohm and hold its enable through rail fall.
5. Reject `HHM2510B1` for this endpoint because 2500 MHz is not the end of the
   nRF channel set. Qualification covers 2400–2525 MHz and explicitly samples
   channels 0/100/125.
6. Keep the Ebyte receptacle mate and exact pigtail/SMA assembly open until a
   received specimen proves them. Do not call the receptacle U.FL by inference.
7. Mark only the nRF electrical paper subblock reviewed. I6 stays active for
   S3/C5/CC1101/SA518/Si4732/IR RF endpoints and consolidated coexistence.

## Consequences

- The existing quiet-state claim now has a physical circuit behind it.
- Full nRF mixes and GPIO allocation do not change.
- Six small logic ICs and three couplers add roughly USD 4.2 at quantity 100
  before ordinary passives; AD8314 replaces, rather than supplements, the
  three provisional detector bodies. This is bounded safety closure, not a
  new feature tier.
- Detector power does not add a permanent 13.5-mA idle load because ENBL falls
  after the evidence-hold interval.
- No KiCad authorization, atomic architecture freeze or mockup restart follows.
