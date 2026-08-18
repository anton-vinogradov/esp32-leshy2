# FND-0101 — Si4732 RF inputs remained abstract

- Статус: **Исправлено на бумажном уровне; RF/mechanical HIL open**
- Scope: I6 broadcast-receiver RF endpoint
- Исправление: [`RXF-0001`](../architecture/RXF-0001-exact-si4732-dual-input-receive-frontend.md), [`DEC-0096`](../decisions/DEC-0096-exact-si4732-dual-input-rf-endpoint.md)

## Несоответствие

The exact `Si4732-A10-GSR` power, clock, control, interrupt and audio circuits
were reviewed in I5, and the antenna policy correctly reserved separate
`RX-FM/SW` and `RX-AM/LW` ports. The machine map nevertheless connected FMI
and AMI directly to two abstract frontend labels. It had no physical matching,
coupling or per-boundary ESD instances and no machine-enforced non-50-Ohm
AM/LW accessory contract.

Therefore the earlier claim that IR closed the last separate I6 endpoint was
incorrect. A named SMA path is not a complete electrical RF endpoint, and a
common connector shell does not make the AMI loop interface a generic 50-Ohm
coax port.

## Correction

- physical FMI/AMI/RFGND contacts 6/8/7 are corrected from the exact SOIC-16;
  the separate catalog pin-map error is recorded in [`FND-0102`](FND-0102-si4732-soic16-contact-map-was-shifted.md);
- FM/SW receives exact 56-nH high-Q matching, exact 1-nF C0G coupling and a
  separately placed exact 0.2-pF-typical ESD shunt;
- AM/LW receives exact 0.47-uF coupling and its own identical ESD body;
- the short ferrite-loop or qualified transformer pod and cable-capacitance
  limit are explicit; arbitrary long coax is forbidden;
- current availability was checked for every newly selected MPN;
- no pin, rail, transmit function or product-cost class changes.

The exact data short assigns FM/SW to FMI and AM/LW to AMI. The current
application note covers the Si47xx family rather than proving this exact A10
implementation; its 56-nH/1-nF network is an FM reference and its SW-on-AMI
section is explicitly Si4734/35-only. Therefore all four bands, pod parasitics,
sensitivity, blocking, ESD and coexistence remain measured gates.

## Sources

- [Skyworks Si4732-A10 data short](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [Skyworks AN383 antenna guidance](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN383.pdf)
- [Skyworks AN332 programming guide](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN332.pdf)
