# REV-0005AV — I6 three-nRF electrical propagation

- Status: **Проведено ревью subblock; I6 remains active**
- Decision: [`DEC-0091`](../decisions/DEC-0091-exact-three-nrf-electrical-endpoint.md)
- Finding: [`FND-0096`](../findings/FND-0096-nrf-quiet-state-and-tx-evidence-were-not-physical.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| exact device registry | pass: two Nexperia Ioff families, TTM coupler, AD8314 and both RF termination values have exact MPN/contact/source/orderability records |
| actual exposed contacts | pass: TSSOP14, VSSOP8, six-land coupler and LFCSP8/EPAD maps follow manufacturer package tables, not generic symbols |
| machine instances | pass: every buffer, coupler, detector, resistor and capacitor is a separate body; three radios are not collapsed |
| pin map | pass: RP GPIO allocation is unchanged; direct RP↔module peers are removed and replaced by directional isolators |
| quiet state | pass on paper: both directions specify Ioff at VCC=0; exact pulls, switch fail-low and QOD are represented |
| full-function behavior | pass: dedicated PIO/DMA/CE/CSN/IRQ and all `3R/1T2R/2T1R/3T` mixes remain mandatory |
| RF band | pass on paper: coupler 2000–4000 MHz and detector response to 2700 MHz include channel 125 at 2525 MHz |
| forward evidence | pass on paper: one directional 10-dB sample and detector per radio; reverse port is terminated; detector survives rail fall |
| lifecycle | pass as explicit risk: nRF24 NRND and exact Ebyte mate are not hidden; lot/alternate/specimen gates block freeze |
| target product pages | pass: both vertical diagrams show exact buffer/coupler/detector MPNs and roles in separate boxes without review-ledger IDs |
| firmware | pass: 100-ms POR, identity checks, enable/off sequence, evidence semantics and channel-edge HIL are propagated |
| downstream boundary | pass: other I6 RF endpoints and consolidated coexistence remain active; no early I6 closure |
| CAD/mockup | pass: no KiCad authorization or integrated-mockup restart is inferred |

## Self-review corrections

| Observed mismatch | Correction |
|---|---|
| quiet-state prose exceeded the circuit | added exact bidirectional powered-off isolation and forbidden direct RP/module routes by test |
| provisional detector saw an abstract, non-directional tap | inserted exact full-band directional coupler, termination, match and AON detector |
| first coupler candidate stopped at 2500 MHz | rejected it and selected a current part specified across 2500–3300 MHz |
| detector could disappear at the instant of rail-off | added diode/RC ENBL hold through QOD discharge |
| `IPX` was easy to misread as U.FL | kept exact mate and pigtail as a received-specimen gate |

## Verification result

- both machine JSON files parse and generated artifacts reproduce;
- 54 hardware architecture tests pass, including the new no-direct-peer,
  full-band-coupler and evidence-hold regression;
- target landing pages remain vertical and current;
- firmware documentation tests pass after propagation.

The three-nRF electrical subblock therefore has **«Проведено ревью»**. I6 is
still active and next owns the native S3/C5 plus CC1101 RF endpoints.
