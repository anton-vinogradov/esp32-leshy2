# REV-0005AP — microSD endpoint propagation review

> S3 was `32/3/1` at this endpoint; `REV-0005AQ` later changes the whole-device
> result to `33/3/0` for encoder capture without changing microSD allocation.

- Status: **Проведено ревью**
- Decision: [`DEC-0085`](../decisions/DEC-0085-exact-isolated-microsd-electrical-endpoint.md)
- Finding: [`FND-0089`](../findings/FND-0089-microsd-endpoint-was-backpowered-and-unprotected.md)

## Propagation checked

| Consumer | Result |
|---|---|
| machine device registry | exact active socket, return buffer, ESD array and 22-uF capacitor expose every real contact; retained parts use already-verified contacts |
| G2F-3I instances/routes | power, Ioff isolation, CS-gated DAT0, mandatory pulls, damping, ESD, shield and detect are exact physical routes |
| allocation regression | S3 remains `32 used / 3 reserved / 1 free`; slow-I/O P20/P21 remain the existing power/detect allocation |
| product diagram | every storage physical component is a separate node with exact MPN and role; no mixed-device rectangle remains |
| display sharing | GPIO4 reaches card DAT0 only through the gated return buffer; reset-high CS defaults and SPI-mode-first sequencing are explicit |
| firmware contract | power-up, initialization, clean unmount, unexpected removal and recovery behavior are explicit |
| stage state | the third I4 paper endpoint receives «Проведено ревью»; remaining UI endpoints and physical/HIL gates stay active |

## Review boundary

Checked JSON, generated atlas and target start pages agree. The circuit contains
no abstract microSD power, isolation, pull, ESD or detect endpoint. This review
does not authorize KiCad, enclosure/socket placement, media procurement as a
production-qualified set, final RC values or claims that fault/throughput HIL
has passed.
