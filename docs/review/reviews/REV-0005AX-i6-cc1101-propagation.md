# REV-0005AX — I6 CC1101 three-band propagation

- Статус: **Проведено ревью subblock; I6 remains active**
- Decision: [`DEC-0093`](../decisions/DEC-0093-exact-cc1101-three-band-endpoint.md)
- Finding: [`FND-0098`](../findings/FND-0098-cc1101-single-ended-band-switch-was-invalid.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| primary-source/spec check | pass: TI silicon bands/contacts, Infineon truth/contacts, TTM balun, AD8314, crystal and ESD data checked |
| current real-device comparison | pass with correction: M5 U219 proves dual-SP3T topology/passive coupon but is WIP; crossed control interpretation is not copied |
| actual contacts | pass: CC VQFN20, two TSSOP14 buffers, band VSSOP8, both TSNP8 switches, balun, crystal, ESD and detector pads are machine-routed |
| bus independence | pass unchanged: dedicated RP PIO0 SM3 plus dedicated DMA/IRQ remain intact |
| powered-off isolation | pass on paper: all six digital directions and both band bits use switched-rail Ioff buffers; `00` isolates both RF ends |
| band branches | pass as first coupon: exact 315/433/868–915 populated MPNs exist; conducted tuning remains blocking |
| actual-TX evidence | pass on paper: sample is after both switches/matching; AD8314 is AON-held; incoming RF cannot authorize |
| ESD | pass on paper: exact 0.2-pF, ±20-kV SESD part is at the external line |
| pin budget | historical I6 pass: P03/P04 consumed and P05 was free; DEC-0098 later consumes P05 for native-Unit power; MCU budgets remain unchanged |
| cost | pass: no dramatic expansion; two switches are about USD 0.43 total at qty 100, balun about USD 0.56, remaining support is low-cost; AD8314 reuses an existing SKU |
| diagrams | pass: both target pages and generated vertical atlas show exact MPN and role per physical body |
| firmware | pass after companion propagation: rail-off band code, lease identity, evidence semantics and fail-closed transition are explicit |
| CAD/mockup | pass boundary: no KiCad authorization and no integrated-mockup restart |

## Self-review corrections

| Observed mismatch | Correction |
|---|---|
| one switch left three filter stubs attached | two equal-control SP3T bodies bracket all branches |
| M5 WIP truth text could have been copied | Infineon truth table is authoritative; both switch bodies receive identical V1/V2 |
| old detector was abstract and weak at low CC output | 0.47-pF high-impedance sample plus existing AD8314 becomes the first full-range target |
| detector could be mistaken for authorization | contract states it only verifies a commanded TX or blocks/delays quiet; it never creates a lease |
| crystal 12-pF reference loads did not match chosen 10-pF CL | exact 15-pF pair accounts for TI's typical 2.5-pF parasitic term |

## Verification result

- both JSON sources parse and generated artifacts reproduce;
- 56 hardware architecture tests pass, including exact truth, contact, branch,
  no-direct-CC-peer, no-old-abstract-tap and target-diagram regressions;
- all new exact MPNs and one-body-per-box roles appear in both target diagrams.

The CC1101 paper subblock therefore has **«Проведено ревью»**. Conducted and
coexistence HIL remain open, and I6 proceeds to the next unfinished RF endpoint.
