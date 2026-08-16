# REV-0002AS — повторное ревью этапа 2 после competitor delta

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Этап: 2 — возможности и исключения
- Reopen finding: [`FND-0040`](../findings/FND-0040-current-competitor-benchmark-missing.md)

## Проверка delta

| Delta | Current disposition |
|---|---|
| `W-EXTRA-11` iButton | accepted external `DEC-0033/REQ-IBTN-0001` |
| M5 infrastructure | M5-first/two-tier `DEC-0034/REQ-EXT-0001` |
| `W-EXTRA-12` FIDO | removed from target `DEC-0039` |
| `W-EXTRA-13` haptic | rejected `DEC-0036` |
| `W-EXTRA-14` IMU | accepted external measurement metadata `DEC-0037` |
| `W-EXTRA-15` keyboard | integrated rejected, phone-assisted text `DEC-0038` |
| `W-EXTRA-16` generic USB host | rejected `DEC-0039` |
| `W-EXTRA-17` 6 GHz/Wi-Fi 6E | rejected `DEC-0040` |
| field mechanics/UI constraints | retained as G3 input, not electronics |

## Gate checks

- [x] all legacy 125 leaves remain traceable;
- [x] every current-competitor delta has owner/reviewed disposition;
- [x] radio/key mission correction propagated;
- [x] exclusions impose zero hidden architecture score/resource;
- [x] no compute owner, chip, bus, pin, PCB or enclosure selected in G2;
- [x] G3 receives controls, display, battery, antenna, expansion, service,
  environment, repairability and cost envelopes as physical-design work.

## Решение

Repeated G2 receives **«Проведено ревью»**. `FND-0040` is closed. G3 target
product design is now the active blocking gate; G4–G9 cannot consume archived
layouts or exact pin maps as accepted inputs before G3 review.
