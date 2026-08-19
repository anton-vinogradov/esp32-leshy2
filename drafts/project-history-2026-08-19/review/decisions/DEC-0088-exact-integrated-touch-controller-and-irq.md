# DEC-0088 — exact integrated touch controller and IRQ

- Status: **accepted under delegated no-material-function/cost rule; Проведено ревью paper electrical endpoint**
- Finding: [`FND-0093`](../findings/FND-0093-touch-controller-identity-and-polarity-were-left-open.md)
- Architecture: [`DSP-0007`](../architecture/DSP-0007-exact-integrated-st77922-touch-endpoint.md)
- Propagation review: [`REV-0005AS`](../reviews/REV-0005AS-exact-touch-propagation.md)

## Decision

1. Treat exact `Sitronix ST77922` as the integrated display/touch TDDI inside
   exact current paper assembly `HMX035CTFT-001`; do not invent a separate
   capacitive-touch controller.
2. Freeze the touch bus contract at SYS_I2C 7-bit address `0x38` and no faster
   than 400 kHz.
3. Freeze `TP_INT` as active low from the exact assembly specification. Add
   exact `Yageo RC0402FR-0710KL` 10-kOhm raw pull-up, populate only fixed
   non-inverting `SN74LVC1G07DCKR`, and remove the `SN74LVC1G06DCKR`
   alternative.
4. Keep shared S3 GPIO37 `SYS_INT_N`; GPIO39 remains dedicated encoder phase
   A. Touch stays interrupt-driven and source discovery is mandatory after a
   shared-line assertion.
5. Preserve the exact reset-low defaults and published minimum timings: 10-us
   reset pulse, 100-ms touch-ready wait, and 120-ms display Sleep-Out wait.

## Consequences

- No GPIO, MCU, expander, interface or user-visible function changes.
- One negligible-cost resistor closes the raw-input default. Removing the
  inverter alternative simplifies BOM and prevents an assembly choice from
  silently reversing runtime semantics.
- ST77922 is not another open/closed firmware policy boundary: it is
  vendor-configured fixed-function COG silicon inside the replaceable display
  assembly.
- Specimen identity/readback, interrupt timing/clear behavior, reset recovery,
  coordinate mapping, shared-source identification and physical/ESD HIL remain
  explicit. The decision does not authorize KiCad.
