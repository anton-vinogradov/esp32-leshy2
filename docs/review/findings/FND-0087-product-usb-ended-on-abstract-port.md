# FND-0087 — product USB ended on an abstract connector and unprotected data/CC lines

- Статус: **Исправлено exact endpoint and four-line protection profile**
- Дата: 2026-08-18
- Architecture: [`USB-0001`](../architecture/USB-0001-exact-product-usb-c-and-protection.md)
- Decision: [`DEC-0083`](../decisions/DEC-0083-exact-protected-product-usb-port.md)
- Review: [`REV-0005AN`](../reviews/REV-0005AN-product-usb-port-propagation.md)

## Finding

After I3 closed, the first I4 consumer still terminated raw VBUS, CC1/CC2 and
S3 USB2 at `abstract:product-usb-c-*` endpoints. The target product diagram
therefore showed `MPN TBD`, the machine route could not prove every real
receptacle contact, and neither USB2 nor CC had an exact connector-side
short-to-VBUS/ESD boundary.

The existing 330-pF CC shunts also could not simply survive insertion of a
protector. TPS25751 contributes a published 120-pF receiver input and
TPD4S201 contributes 40…120 pF per protected CC channel. With a 330-pF part,
the high paper corner reaches 570 pF before capacitor tolerance, connector,
route and layout parasitics, too close to the USB-PD 600-pF receiver ceiling.

## Correction

`USB-0001/DEC-0083` instantiate exact `DX07S016JA1R1500`, route every live
Type-C contact, add one `TPD4S201RUKR` across both CC and both USB2 lines and
replace the two CC shunts with exact 220-pF C0G parts. The new published-value
screen is 369…471 pF before route parasitics and leaves 129 pF to the upper
receiver limit. Exact total capacitance and USB Full-Speed RC/signal integrity
remain measured gates, not paper claims. The correction also adds exact
22-Ohm D+/D- series parts and two initially DNP tuning footprints at S3.

The correction uses no new MCU pin. Protector `FLT` receives an exact local
pull-up and fixture test point; normal software sees detach/PD state while a
prototype fixture captures the direct hardware fault.
