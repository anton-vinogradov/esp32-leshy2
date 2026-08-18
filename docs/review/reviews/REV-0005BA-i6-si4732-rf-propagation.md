# REV-0005BA — I6 Si4732 RF propagation

- Статус: **Проведено ревью paper subblock; RF/mechanical HIL open**
- Decision: [`DEC-0096`](../decisions/DEC-0096-exact-si4732-dual-input-rf-endpoint.md)
- Finding: [`FND-0101`](../findings/FND-0101-si4732-rf-inputs-remained-abstract.md)
- Pin correction review: [`REV-0005BB`](REV-0005BB-si4732-soic16-pin-map-correction.md)
- Architecture: [`RXF-0001`](../architecture/RXF-0001-exact-si4732-dual-input-receive-frontend.md)

## Проверка распространения

| Consumer | Result |
|---|---|
| exact device registry | pass after `REV-0005BB`: the full Si4732 SOIC-16 map is corrected and regression-locked; target `Si4732-A10-GSR`/JLCPCB `C2155558` is an in-stock assembly line rather than the out-of-stock tube SKU; three new exact passive MPN/contact records include manufacturer facts and current authorized-stock evidence; two independent existing SESD bodies are reused |
| machine candidate | pass: nine exact routes replace both hidden frontend abstractions and retain separate FMI/AMI/RFGND contacts 6/8/7 |
| pin/power budget | pass: S3 `33/3/0`, C5 `14/6/1`, RP `48/0/0`, main slow I/O `23/0/1`, UI I/O `7/1/0`; no new rail or TX path |
| antenna identity | pass: FM/SW and non-50-Ohm AM/LW remain distinct labelled standard-SMA boundaries; connector MPN is still a mechanics input |
| quiet state | pass on paper: receiver rail/digital interfaces still discharge/isolate; passive ESD/coupling cannot back-power or authorize TX |
| principled diagram | pass: generated and both landing-page vertical diagrams show each physical part with exact MPN and role; the two ESD bodies are not merged |
| historical correction | pass: IR remains reviewed, but its stale “last separate endpoint” wording now points to this correction |
| firmware input | pass after paired-repository propagation: exact port/profile identity, qualification and failure semantics are exported without claiming HIL |

## Result

The Si4732 dual-input paper subblock receives **«Проведено ревью»**. Every
separate base RF/IR electrical endpoint is now represented, so I6 may proceed
to the consolidated power, quiet-state, conducted/OTA/optical, coexistence,
thermal, fault and no-stall proof. This review does not authorize KiCad or the
paused integrated mockup.
