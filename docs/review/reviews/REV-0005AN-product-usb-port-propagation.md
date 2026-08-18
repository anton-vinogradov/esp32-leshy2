# REV-0005AN — exact product USB-port propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0083`](../decisions/DEC-0083-exact-protected-product-usb-port.md)
- Architecture: [`USB-0001`](../architecture/USB-0001-exact-product-usb-c-and-protection.md)
- Finding: [`FND-0087`](../findings/FND-0087-product-usb-ended-on-abstract-port.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| exact-device registry | JAE receptacle, TI protector, Panasonic 22-Ohm series parts, 100-V VBIAS capacitor and 220-pF CC part have current primary/orderable evidence and real contacts |
| machine routes | raw VBUS, four grounds, shell, both CC, both duplicated USB2 pairs, both physical SBU NCs, protector supplies/fault/grounds/NCs and S3/TPS destinations are explicit |
| pin budget | S3 remains GPIO19 D-, GPIO20 D+; `FLT` is fixture-only; GPIO47 remains free |
| power/startup | raw VBUS/TPS SafeMode path is unchanged; protector VPWR comes from TPS LDO_3V3 and preserves dead-battery attach |
| signal integrity | corrected S3 capability to USB Full-Speed 12 Mbit/s; exact 22-Ohm series parts and two DNP shunt positions follow the initial Espressif circuit while RC/SI and enumeration remain HIL |
| CC behavior | exact shunts change 330→220 pF; paper subtotal becomes 369…471 pF before measured parasitics |
| fault authority | CC/data OVP is hardware-only; software can observe detach/PD status but cannot bypass protection |
| diagrams/product pages | both target diagrams now show separate exact receptacle, protector and support parts; finished-product text says protected USB2 without engineering IDs |
| firmware input | automatic protection, detach/re-enumeration handling, no Alt Mode/source role and fixture-only FLT are propagated |
| sourcing/cost | current stock and `$1.9…2.6` material screen recorded; electrical alternate and one-stop supply remain I8 |
| CAD boundary | I4 remains active; integrated mockup stays paused through I9 and KiCad remains unauthorized |

## Result

The first I4 product-USB paper endpoint and its downstream propagation receive
**«Проведено ревью»**. Physical placement and all port HIL evidence remain
explicit and no prototype result is implied.
