# REV-0005AY — I6 SA518 RF propagation

- Статус: **Проведено ревью subblock; I6 remains active**
- Decision: [`DEC-0094`](../decisions/DEC-0094-exact-sa518-broadband-rf-endpoint.md)
- Finding: [`FND-0099`](../findings/FND-0099-sa518-rf-feed-and-evidence-were-not-electrically-closed.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| primary-source/spec check | pass: SA518 bands/output/contact 7, AD8314 input/range, PESD24VY1BSF voltage/capacitance/package and exact resistor order code checked |
| actual contacts | pass: SA518 ANT, PESD K1/K2, AD8314 LFCSP8 including EPAD and every support body are machine-routed |
| mainline | pass on paper: direct controlled 50 Ω; no band switch, coupler or external matching body adds latency/loss |
| protection | pass on paper: 24-V stand-off clears 31-dBm normal and first-order 2:1-VSWR voltage; lower-voltage CC TVS is rejected |
| actual-TX evidence | pass on paper: exact ~40-dB resistive sample reaches −14…−9 dBm, detector survives rail fall by bounded hold and never authorizes |
| detector SKU | pass: voice migrates from legacy LTC5507 to separate AD8314, reusing support SKUs |
| filter decision | pass as reopenable no-loss choice: no filter bank or P05 consumption before conducted failure evidence |
| pin/resource budget | historical I6 pass: MCU allocations unchanged and P05 was free; DEC-0098 later consumes P05 for native-Unit power; SG-VOICE remains independent half-duplex |
| diagrams | pass: both target pages and generated vertical atlas show exact MPN and role per physical body |
| firmware | pass after companion propagation: lease, antenna/profile, evidence, timeout and filter-reopen semantics explicit |
| CAD/mockup | pass boundary: no KiCad authorization and no integrated-mockup restart |

## Self-review corrections

| Observed mismatch | Correction |
|---|---|
| abstract ANT→SMA path | physical ANT contact 7 now terminates in one controlled-50-Ω line and explicit SMA boundary |
| 7-V low-power ESD reuse would clip a 1-W path | exact 24-V low-C bidirectional antenna TVS selected |
| 0.1-pF tap first idea was tolerance/parasitic-sensitive against AD8314 internal 2 pF | datasheet series-attenuation topology with exact 5.1-kΩ + 52.3-Ω bodies selected |
| old detector did not prove final-line RF | sample now originates on the complete protected external line and uses bounded AON hold |
| preemptive dual-band filter bank would spend P05 and add loss | filter bank becomes a measured-failure reopen gate |

## Verification result

- both JSON sources parse and generated artifacts reproduce;
- 57 hardware architecture tests pass, including exact protection voltage,
  contacts, route, no-old-abstract-tap, P05 and target-diagram regressions;
- root target pages contain the exact voice RF MPNs and no review-ledger IDs.

The SA518 RF paper subblock therefore has **«Проведено ревью»**. Conducted,
legal and coexistence HIL remain open, and I6 proceeds to the IR endpoint.
