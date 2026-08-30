# Распределение экземпляров native H2-R2

[English](h2-r2-instance-ledger.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

**Instance-checkpoint `H2-R2.1.3` пройден 30 августа 2026 года.** Он фиксирует,
какой точный устанавливаемый компонент относится к какому текущему проекту и
листу R2. Этот результат не создаёт и не разрешает schematic nets, размещение
PCB или печать.

## Результат

| Элемент | Проверенный результат |
|---|---:|
| Устанавливаемые экземпляры на платах | 1 096 |
| Точные группы компонентов плат | 208 |
| Native-проекты | 3 |
| Граф проектов | 23 листа; корневые листы только иерархические и намеренно не содержат деталей |
| Независимые домены RP2354B | 2: передний Hub RP и задний RF RP |
| Созданные native nets | 0 |
| Ошибки распределения или повторные project-local names | 0 |

Старый single-RP ledger использован только как подсказка имени и прежнего листа
после сверки текущих MPN, количества, footprint, контактов и affinity листов R2.
Он не передал ни одного reference designator, net или правила владения.
Устаревшие R1-only detector, identity, local-regulator и timing bodies не
перенесены. Текущие AD8314, 50-контактный дисплей, независимые service paths
двух RP и граница TCA9803 Pack/Safety присутствуют.

## Машинное evidence

- [Контракт распределения](../hardware/ecad/h2-r2-instance-ledger-contract.json)
- [Сгенерированный ledger 1 096 экземпляров](../hardware/ecad/generated/H2-R2-native-instance-ledger.json)
- [Генератор](../hardware/ecad/h2_r2_instance_ledger.py)

Следующая [сверка native nets](h2-r2-net-ledger.ru.md) теперь также пройдена.
Текущая точка остаётся **`H2-R2.1.3`**: материализовать проверенные definitions,
references и nets в трёх native-проектах KiCad. Placement, routing, печать и
заказ остаются заблокированы.
