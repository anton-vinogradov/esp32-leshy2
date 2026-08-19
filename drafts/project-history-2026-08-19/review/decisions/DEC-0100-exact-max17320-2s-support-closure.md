# DEC-0100 — exact MAX17320 2S support closure

Статус: **принято; проведено ревью в paper electrical scope**.

## Решение

1. Реализовать exact 2S Figure-24 topology MAX17320G20+T: два балансировочных
   резистора CELL1/BATTS, short CELL1/CELL2/CELL3 и два sense capacitors.
2. Принять `ERJ-P08F49R9V` как first target балансировочного резистора: 49,9 Ω,
   1%, 1206, 0,66 Вт; thermal HIL остаётся обязательным.
3. Принять `GRM188R71E474KA12D` как общий first target 0,47-мкФ/25-В X7R для
   CP, AOLDO, REG3 и REG2, каждую позицию устанавливать отдельно.
4. Машинно инстанцировать все IN/PCKP/CHG/DIS, ALRT, private I²C, MSPM0
   VDD/NRST и shunt force/Kelvin support parts.
5. Не соединять push-pull MAX17320 PFAIL напрямую с admission-domain input.
   Использовать половину отдельного `2N7002DW-7-F` как level translator.
6. Не выдавать standard PA23 за open-drain. Использовать вторую половину того
   же dual MOSFET как passive-drain request к общему `SYS_INT_N`.
7. Сохранить принятую 2S функциональность, GPIO budget, hard STOP и три
   независимых service/recovery domains без изменений.

## Следствия

- Узкий I3 paper-support residue, обнаруженный I8, закрыт и повторно
  просмотрен; I1…I7 снова имеют **«Проведено ревью»** в paper scope.
- BOM возрастает на 25 placements и две новые MPN-линии, до 816/187; это
  физически необходимые детали, а не новая функция.
- Прямой PFAIL мог превысить питание входа MSPM0, а прямой PA23 не обеспечивал
  wired-low поведение. Оба несоответствия устранены без нового IC family.
- KiCad по-прежнему не разрешён: I8 qualification и I9 whole-design review
  остаются впереди, physical/HIL gates перечислены в `PWR-0022`.

