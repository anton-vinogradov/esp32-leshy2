# DEC-0041 — logical/electrical feasibility before physical layout

- Статус: **Принято по прямому указанию владельца; проведено ревью процесса**
- Дата: 2026-08-17
- Основание: сначала согласовать владельцев, контроллеры, шины и реально
  доступные выводы; затем адаптировать полезный legacy-макет
- Исправляет направление: [`LAY-0001`](../product-design/LAY-0001-form-factor-candidates.md)
- Метод: [`FLOW-0001/G2F`](../architecture/FLOW-0001-product-to-cad-gates.md)

## Решение

Между закрытым capability gate `G2` и новым физическим макетом вводится
обязательный feasibility checkpoint `G2F`. Он не создаёт KiCad и не замораживает
финальную архитектуру, но до дальнейшего industrial/physical design обязан дать:

1. нейтральный реестр всех семантических сигналов и аппаратных ресурсов из
   принятого wishlist, без наследования прежних владельцев;
2. цепочку происхождения каждого считаемого вывода: `SoC → package → exact
   module/device MPN/revision → реально доступный pad/header/connector`;
3. минимум две полные owner/bus/controller/GPIO карты с одинаковым scope;
4. отдельные ledgers used/free/strap/recovery, controller instances, memory,
   traffic, power и service/update burden;
5. self-review каждой карты и явное устранение коллизий;
6. согласованный владельцем **рабочий электрический baseline** для физической
   компоновки.

Рабочий baseline не равен `G7` atomic architecture. Если реальная упаковка,
антенны, питание, стоимость, обслуживание или эргономика покажут конфликт,
`G2F…G6` повторяются. Нельзя чинить конфликт скрытым удалением функции или
считать предварительный GPIO номер обязательным для платы.

## Правило реального устройства

Вывод считается доступным только когда закрыты все применимые слои:

| Слой | Обязательное доказательство |
|---|---|
| silicon | peripheral/GPIO capability в актуальной документации производителя |
| package | функция физически bonded в точном корпусе/варианте |
| module/device | pin не занят внутренней flash/PSRAM/RF/glue и выведен точным MPN/revision |
| carrier/connector | если используется готовая плата, Unit, Cap или модуль — сигнал присутствует на её реальном pad/header/connector |
| board implementation | land pattern, netlist, reset pulls, level/power domain и доступ для измерения соответствуют выбранной детали |
| specimen | на прототипе exact marking/revision, continuity, boot report и диагностический self-test подтверждают принятую конфигурацию |

Если слой неприменим (например, bare QFN непосредственно на нашей PCB), это
записывается явно; его нельзя молча заменить проверкой похожей dev-board.
Marketing GPIO count, generic family datasheet, символ библиотеки и pinout
похожего модуля сами по себе доказательством не являются.

## Отношение к старому макету

Legacy `75×150 mm` two-board clamshell и его генератор принимаются как **первая
рабочая физическая гипотеза**, потому что уже содержат полезные fold/edge/
mezzanine/clearance checks. Его старые MCU owners, onboard LoRa, antenna count,
generic module rectangles и pin assumptions не являются входами `G2F`.

Три новых эскиза `P1/P2/P3` из `LAY-0001` сохраняются как преждевременный
справочный эксперимент. Они не требуют выбора владельца и не заменяют
адаптацию старого воспроизводимого макета после electrical feasibility review.

## Граница CAD

- block diagram, exact candidate pin tables и машинно-проверяемый pin ledger
  разрешены до KiCad;
- component symbols, schematic, PCB placement/routing и production BOM всё ещё
  запрещены как normative output до соответствующих downstream gates;
- footprint или реальная module geometry допускаются только как проверка
  feasibility и маркируются candidate/reference.

