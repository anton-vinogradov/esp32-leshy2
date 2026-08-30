# Native ECAD-инвентарь H2-R2

[English](h2-r2-native-inventory.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

**`H2-R2.1.1` зафиксировано 2026-08-30.** Это чистая входная граница новой
production-схемы R2. Здесь описан готовый продукт, а не история прошлых решений.

## Результат

| Инвентарь | Результат ревью |
|---|---|
| Native-проекты | `LESHY2-UI-R2`, `LESHY2-RF-R2`, пассивный `L2-DISP-ADP-001-B` |
| Функциональные sheets | 23 уникальных sheets с одним владельцем каждой ответственности |
| Вычислительные домены | 6: S3, C5, передний Hub RP, задний RF RP, Pack и Safety |
| Точные группы компонентов | 213 MPN-групп, 1 106 позиций на готовое устройство |
| Внешний антенный комплект | 8 точных групп, 12 отдельно идентифицированных антенн/pod |
| Открытые prerequisite до ECAD | 0 |
| Созданные native symbols/nets | 0 / 0 |

Передний проект владеет S3, C5, Hub RP, display/touch, microSD, органами
управления и всеми тремя полными nRF24-островами. Задний проект владеет RF RP,
питанием, Pack/Safety, CC1101, VHF/UHF voice, broadcast/Airband, audio и
host-интерфейсами U214/U219/M5. M1 существует только как две именованные
стороны точного 80-контактного контракта.

Исторической кастомной платы `LESHY2-LORA-CAP-01` в native R2 нет. Устройство
поддерживает серийные Caps U214/U219 через заднюю розетку, но не производит
отдельную LoRa-Cap PCB.

## Точный delta после H1 cost inventory

В принятом H1 было 210 групп и 1 099 позиций. Проверенная Pack/Safety-граница
добавляет один `TCA9803DGKR/C2687966`, два rail-local 1 мкФ `C52923`, два
100 нФ `C1525` и две дополнительные MAIN-подтяжки `C25879`. Итог — 213 точных
групп и 1 106 позиций. Display, опциональный U214, съёмные аккумуляторы и ручка
энкодера сохраняют явные non-PCBA/final-assembly dispositions.

## Машинные evidence

- [Source/sheet contract](../hardware/ecad/h2-r2-native-inventory-contract.json)
- [Сгенерированный component inventory](../hardware/ecad/generated/H2-R2-native-inventory.json)
- [Электрические prerequisites](h2-r2-electrical-prerequisites.ru.md)
- [Проверенный физический результат H1](h1-r2-acceptance.ru.md)

Каждый source связан hash. Исторический stock не выдаётся за текущий: каждый
выбранный MPN повторно проверяется на поверхности JLCPCB Standard PCBA при
architecture freeze и непосредственно перед заказом ровно одного экземпляра.

## Текущая граница

Текущая точка — **`H2-R2.1.2`**: сформировать точный ledger symbols/contacts/
values/footprints для этих 213 групп и шести domain maps. KiCad-проекты,
schematic nets, PCB placement, routing, печать и заказ остаются заблокированы.
