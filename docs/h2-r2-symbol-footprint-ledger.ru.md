# Точные symbols и footprints H2-R2

[English](h2-r2-symbol-footprint-ledger.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

**`H2-R2.1.2` зафиксировано 30 августа 2026 года.** Это точная граница
определений компонентов native-схемы R2. Она не создаёт schematic nets,
KiCad-проекты или PCB layout.

## Результат

| Элемент ledger | Зафиксированный результат |
|---|---|
| Точные component groups продукта | 242 |
| Группы компонентов на платах | 237; у каждой один symbol `Leshy2_R2` и одна точная footprint-identity |
| Явные non-PCBA groups | 5: display assembly, U214, комплект из двух cells, ручка encoder и пять съёмных RF-jumper |
| Логические контакты | 1 662, скопированы и hash-bound к текущему manufacturer contact evidence |
| Стандартные package identities KiCad | 202 |
| Существующие локальные manufacturer-derived definitions | 32 |
| Новые локальные геометрии, материализованные в contact-checkpoint | 3: `FH34SRJ-50S-0.5SH(50)`, `WBC1-1TLC` и `WBC16-1TLC` |
| Созданные native schematic symbols/files/nets | 0 / 0 / 0 |
| Незакрытые группы | 0 |

Каждая строка содержит точный MPN, schematic value, полный contact map, роли
контактов, affinity к native sheets R2, manufacturer evidence и номер JLCPCB,
если он принят. Package names старого R1 используются только как подсказки:
они принимаются лишь после сверки exact MPN и текущих contacts и никогда не
переносят старые designators, nets или sheet owners.

## Исправления, найденные ledger

Пять TE Connectivity `2118651-2` — это съёмные 30-мм кабели U.FL↔U.FL. Они
больше не изображаются как PCB-компоненты. Native-схема показывает разъёмы на
плате и модуле; у самого кабеля нет symbol или PCB-footprint.

Пять конфликтов исторических package-hints разрешены по текущей точной
manufacturer identity, а не унаследованы автоматически:

- Murata 22 мкФ остаётся конденсатором 0805, а не резистором;
- термистор TDK остаётся NTC в resistor-style корпусе 0603, а не конденсатором;
- Nexperia `74LVC1G32GV,125` использует свой TSOP5/SC-74A package;
- TI logic/comparator в DCK используют manufacturer-specific five-land mapping
  DCK там, где историческое evidence расходилось.

Принятый `AD8314ARMZ-REEL`, новые passives Pack/Safety и `TCA9803DGKR` также
получили точные текущие packages. Этот шаг не менял ни одного production MPN.

## Contact-checkpoint H2-R2.1.3

Новый 50-контактный footprint FH34 и оба six-pad Coilcraft transformer
материализованы по официальным чертежам. Сгенерированный аудит разрешает
все 1 605 контактов 237 board groups: 1 602 являются контактами footprints,
ещё три — явными RF-разъёмами на модулях. Все именованные площадки footprints учтены
как электрические или явно механические; фиктивные площадки carrier для разъёмов
на модулях не создаются. Остальные 57 контактов исходного ledger из 1 662 контактов
принадлежат пяти явным non-PCBA assemblies.

## Машинное evidence

- [Контракт exact ledger](../hardware/ecad/h2-r2-symbol-footprint-contract.json)
- [Сгенерированный ledger 242 групп](../hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json)
- [Контракт contact-to-pad](../hardware/ecad/h2-r2-contact-materialization-contract.json)
- [Сгенерированная материализация контактов](../hardware/ecad/generated/H2-R2-contact-materialization.json)
- [Контракт controlled symbols](../hardware/ecad/h2-r2-symbol-library-contract.json)
- [Сгенерированный manifest controlled symbols](../hardware/ecad/generated/H2-R2-controlled-symbol-library.json)
- [Проверенное распределение экземпляров](h2-r2-instance-ledger.ru.md)
- [Текущий native project inventory](h2-r2-native-inventory.ru.md)

## Текущая граница

Controlled library `Leshy2_R2` теперь содержит все 237 exact-MPN symbols и
1 618 уникальных electrical-pad pins и проходит parser KiCad 10. Все 1 187
устанавливаемых экземпляров распределены по текущим проектам, а их 4 323
контакта прошли [сверку native nets](h2-r2-net-ledger.ru.md).
[Проекты native KiCad](h2-r2-native-kicad.ru.md) также проходят ERC без замечаний.
Сверка sheets и HW↔FW прошла в [H2-R2.1.5](h2-acceptance.ru.md). Теперь H3
фиксирует эти входы; placement, routing, печать и заказ остаются заблокированы.
