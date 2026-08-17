# MFG-0001 — one-stop PCBA and loose-antenna kitting feasibility

- Статус: **Проведено ревью фактов; supplier policy остаётся открытой**
- Дата проверки: 2026-08-17
- Antenna decision: [`DEC-0055`](../decisions/DEC-0055-profiled-external-antenna-kit.md)
- Proposal: [`IMP-0047`](../improvements/IMP-0047-one-stop-pcba-antenna-kitting-policy.md)

## Ответ

Заказать изготовление/сборку платы и loose antennas одной поставкой возможно,
но это не обычный bare-PCB order. Нужен turnkey PCBA с kitting/box-build либо
отдельный custom RFQ, где antennas являются строками комплекта без PCB
designators.

## Проверенные варианты

| Фабрика/сервис | Что прямо документировано | Вывод для Leshy2 |
|---|---|---|
| Seeed Fusion Kitting | parts из Seeed либо «anywhere else», customized PCB/PCBA в том же personalized kit, packaging/printing, от 5 sets | прямое соответствие прототипной партии |
| Elecrow | PCB fab/assembly, turnkey/combo sourcing, sub-assembly & kitting, labels/packaging | сильный RFQ candidate; exact antenna scope подтвердить quotation |
| JLCPCB | public/global/pre-order/consigned parts для PCBA orders | PCBA sourcing подходит; loose antenna kit не заявлен как стандартная операция, требуется письменное custom confirmation |
| PCBWay | turnkey/kitted/combo sourcing для PCBA, но закупленные parts используются только для assembly в PCBA orders | loose antennas нельзя предполагать частью стандартного portal order; нужен OEM/custom RFQ |

## Что должно входить в RFQ

- quantity PCBA и quantity complete kits;
- каждая loose antenna как `KIT-*` BOM line без reference designator;
- exact MPN, manufacturer, quantity per kit, approved purchase link и правило
  `no substitution without written approval`;
- раздельная маркировка port/profile, особенно SMA против RP-SMA;
- отдельные строки для pigtails, harnesses, collars/caps и крепежа;
- индивидуальные пакеты, lot/quantity traceability и incoming visual/connector
  inspection;
- отдельно оговорённые functional/RF tests: обычный kitting сам по себе не
  доказывает VNA, sensitivity, EIRP или coexistence.

## Источники

- [Seeed Fusion Custom Electronic Kitting](https://www.seeedstudio.com/kitting-service.html)
- [Elecrow turnkey manufacturing and kitting](https://www.elecrow.com/)
- [JLCPCB PCBA Parts Sourcing Instruction](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction)
- [PCBWay Electronic Components Sourcing](https://www.pcbway.com/pcb_prototype/Electronic_Components.html)

