# FND-0040 — current competitor benchmark was missing from the frozen wishlist

- Статус: **Открыто; G2 требует повторного ревью**
- Дата: 2026-08-16
- Обнаружено при входе в corrected `FLOW-0001/G3`
- Аудит: [`AUD-0004`](../audits/AUD-0004-current-competitor-capability-gap.md)

## Несоответствие

`INV-0002/0004` доказали полноту относительно legacy-списка и найденных тогда
extras, но не содержали отдельного актуального benchmark конкурентов. Это
недостаточно после явного требования владельца строить продукт из обработанных
возможностей конкурентов, 5 GHz и остального; кроме того, `FLOW-0001/G2`
нормативно называет competitors входом capability model.

Следовательно, прежний статус 125/125 остаётся корректным только для прежнего
source universe. Он не доказывает, что не пропущена новая пользовательская
хотелка перед physical design.

## Найденные delta-кандидаты

Актуальные официальные материалы выявили отдельные вопросы по:

- iButton/1-Wire read/emulate/write profile;
- U2F/FIDO-style USB security-key profile;
- haptic feedback и IMU;
- физической клавиатуре против touch/compact-control surface;
- dual-role/high-speed accessory host;
- 6 GHz/Wi-Fi 6E относительно уже принятого 5 GHz;
- field mounting, lanyard, glove/sunlight use and serviceable module mechanics.

Progress 2026-08-16: `W-EXTRA-11` closed through external passive iButton
profile `DEC-0033/REQ-IBTN-0001`; M5 infrastructure through `DEC-0034`; and
`W-EXTRA-12` was initially accepted through open personal FIDO
`DEC-0035/REQ-FIDO-0001`, then removed by the mission correction `DEC-0039`.
`AUD-0007/DEC-0036` reviewed and rejected product haptic.
`AUD-0008/DEC-0037/REQ-IMU-0001` accept optional external measurement pose;
`AUD-0009/DEC-0038` reject an integrated keyboard and accept bounded
phone-assisted text. `AUD-0010/DEC-0039` reject generic High-Speed USB host
while retaining RF-derived transport. `AUD-0012/REV-0002AQ` review the final
6 GHz facts; only owner placement `IMP-0034` remains unresolved.

Часть — новые capabilities, часть — входы `G3`, а часть уже покрыта
`W-EXTRA-*` и не должна учитываться дважды.

## Правильное закрытие

1. Проверить representative current products только по первичным/официальным
   sources и честно отделить shipping products от development prototypes.
2. Сопоставить каждую feature с reviewed wishlist: covered, existing deferred,
   G3 design input либо real gap.
3. Каждый real gap решить владельцем отдельно; ничего не добавлять молча.
4. Обновить `INV-0002/0004` и затронутые requirements.
5. Выпустить отдельный propagation review и лишь затем вернуть G2 статус
   **«Проведено ревью»**.

До закрытия G2 physical-design research допустим, но target `G3` не может быть
принят или стать входом архитектуры.
