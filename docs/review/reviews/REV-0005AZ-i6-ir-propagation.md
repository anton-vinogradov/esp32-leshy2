# REV-0005AZ — I6 IR propagation

- Статус: **Проведено ревью paper subblock; HIL open**
- Decision: [`DEC-0095`](../decisions/DEC-0095-exact-ir-endpoint.md)
- Finding: [`FND-0100`](../findings/FND-0100-ir-endpoint-was-abstract-and-not-production-shaped.md)
- Architecture: [`IRF-0001`](../architecture/IRF-0001-exact-dual-receiver-transmit-and-optical-evidence-endpoint.md)

## Проверка распространения

| Consumer | Result |
|---|---|
| machine devices | exact TSOP95238TT, TSMP95000TT, VSMY14940 and support contacts added; VEMD1060X01/TLV9061 promoted to the exact optical path |
| machine candidate | all RX power/filter/isolation, TX/current/default and optical-TIA routes replace IR abstractions |
| pin map | C5 GPIO0/1/4/6/24 unchanged; no invented or unexposed device contact |
| quiet state | QOD receive discharge, Ioff returns, host idle pulls and dark MOSFET default are explicit |
| principled diagram | both landing-page diagrams are vertical and show one physical device with exact MPN and role per box |
| requirements/old decisions | robust envelope, measured-carrier provenance and conditional safety limits remain distinct; old first candidates are marked superseded |
| firmware input | exact phase, provenance, evidence and shutdown contract exported without presenting HIL as complete |

## Result

The IR paper subblock receives **«Проведено ревью»**. This closes the last
separate I6 endpoint, not I6 as a whole: optical, thermal, electrical,
conducted/OTA and whole-device coexistence/no-stall HIL remain mandatory.
No KiCad or integrated-mockup authorization follows from this review.
