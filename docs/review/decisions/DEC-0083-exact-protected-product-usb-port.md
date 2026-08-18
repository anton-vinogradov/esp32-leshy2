# DEC-0083 — exact protected product USB port

- Статус: **Принято; paper endpoint проведено ревью**
- Дата: 2026-08-18
- Architecture: [`USB-0001`](../architecture/USB-0001-exact-product-usb-c-and-protection.md)
- Finding: [`FND-0087`](../findings/FND-0087-product-usb-ended-on-abstract-port.md)
- Propagation: [`REV-0005AN`](../reviews/REV-0005AN-product-usb-port-propagation.md)

## Decision

1. Exact product receptacle is `JAE DX07S016JA1R1500`; every live Type-C
   contact and four shell locks are represented in the machine source.
2. One `TPD4S201RUKR` protects CC1, CC2, D+ and D- against connector-side
   short-to-VBUS and IEC ESD before TPS25751D and S3.
3. The protector SBU1/SBU2 channels carry only USB2 D+/D-. Physical Type-C
   SBU contacts remain unconnected; Alt Mode is not a product capability.
4. CC1/CC2 shunts change from 330 pF to exact 220-pF C0G parts. The complete
   line must pass measured USB-PD capacitance/attach behavior before freeze.
5. `FLT` receives an LDO_3V3 pull-up and fixture test point without consuming
   GPIO47 or joining a main-domain net while unpowered.
6. The exact ESP32-S3 limit is USB Full-Speed at 12 Mbit/s. Two exact
   `ERJ-2RKF22R0X` 22-Ohm series resistors implement the initial Espressif
   recommendation; two 0402 shunt positions remain DNP pending measured tuning.
   Failed RC/SI HIL reopens the values, placement or protector architecture,
   but never silently removes protection.
7. Placement, shield-return/chassis network, enclosure cutout, ESD,
   short-to-VBUS and USB Full-Speed RC/SI HIL remain open. No KiCad
   authorization follows.

## Consequence

The first I4 endpoint no longer contains an abstract product connector or
unprotected external CC/data line. It uses no additional MCU pin and adds no
new product mode. Current material is approximately `$1.9…2.6` per board for
the formerly unresolved mandatory connector/protection implementation;
alternate/one-stop sourcing remains I8.
