# REV-0005AW — I6 native S3/C5 RF propagation

- Status: **Проведено ревью subblock; I6 remains active**
- Decision: [`DEC-0092`](../decisions/DEC-0092-exact-s3-c5-native-rf-endpoints.md)
- Finding: [`FND-0097`](../findings/FND-0097-native-rf-evidence-stopped-before-the-real-feed.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| exact device registry | pass: exact dual-band coupler, board U.FL receptacle and 39-pF C0G DC block have manufacturer/contact/source/orderability records |
| actual exposed contacts | pass: module `ANT/ANT1/ANT2`, U.FL center/shell, all four manufacturer-named coupler lands and all LTC5532 contacts are represented |
| machine instances | pass: S3 and C5 use independent connector/coupler/termination/detector-support bodies |
| RF coverage | pass on paper: 2400…2496 and 4900…5950 MHz include every stated native module channel |
| mainline loss | pass as bounded input: no more than 0.2 dB at 2.4 GHz and 0.4 dB at 5 GHz before cable/PCB/SMA loss |
| actual-TX evidence | pass on paper: directional sample after the module receptacle, exact termination and complete detector support replace both abstract taps |
| pin/bus budget | pass unchanged: no GPIO or bus is consumed |
| C5 secondary RF contact | pass: real `ANT2` is acknowledged and explicitly default-disabled/no-connect |
| availability/cost | pass for selected MPNs: authorized stock checked; about USD 2.98 at qty 100 before cables/passives |
| target product diagrams | pass: English and Russian vertical diagrams show separate exact physical bodies and roles |
| firmware contract | pass: band coverage, feed loss, evidence qualification and TX-deny behavior propagate without promising unmeasured thresholds |
| physical boundary | pass: exact jumper length and RP-SMA MPN remain visibly blocked until placement rather than guessed |
| downstream boundary | pass: CC1101 and remaining I6 endpoints stay active; no early I6 closure |
| CAD/mockup | pass: no KiCad authorization or integrated-mockup restart is inferred |

## Self-review corrections

| Observed mismatch | Correction |
|---|---|
| detector MPN was visible but RF source was abstract | inserted real module connector, board mate, directional coupler and termination |
| detector support values existed only in prose | instantiated two resistors, input/output capacitors and bypass per detector |
| C5 module exposes an extra RF pad | recorded real `ANT2` and its default-disabled no-connect state |
| a convenient 100-mm jumper could have been frozen before placement | kept the exact length-coded cable assembly open until placement and loss measurement |

## Verification result

- both machine JSON files parse and generated artifacts reproduce;
- 55 hardware architecture tests pass, including exact-band/contact/route and
  no-old-abstract-tap regressions;
- target diagrams remain vertical and current;
- firmware documentation tests pass after propagation.

The S3/C5 native RF paper subblock therefore has **«Проведено ревью»**. I6
remains active; the CC1101 frontend is next.

