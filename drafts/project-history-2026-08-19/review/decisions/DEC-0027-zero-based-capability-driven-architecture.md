# DEC-0027 — zero-based capability-driven architecture

- Статус: **Принято владельцем**
- Дата: 2026-08-16
- Основание: прямое уточнение владельца после прерывания legacy-derived synthesis

## Решение

Системная архитектура Leshy2 разрабатывается с нуля от замороженных продуктовых хотелок, обработанных capability contracts, simultaneous scenarios, safety/legal boundaries и zero-loss cost rule.

Прежние MCU owners, buses, transports, GPIO, module placement, PCB routing и классы layouts не являются входами. Они только справочные идеи, риски и отрицательные результаты.

## Канонические входы

1. `INV-0004` и owner invariants `W-OWN-*`;
2. reviewed `REQ-*` после очистки от implementation leakage;
3. явно принятые `DEC-*`, включая C5 IR, S3 native BLE, external GNSS/LoRa, ES8311, STOP и signed updates;
4. primary-source component ceilings, полученные заново при оценке candidates;
5. измерения и comparable quotes, когда до них доходит стадия.

## Порядок synthesis

1. выделить hardware-neutral capability atoms и их evidence/safety boundaries;
2. построить simultaneous/failure scenarios;
3. вывести compute, real-time, bus, memory, storage, analog, RF, power, recovery и physical-control demand без pin numbers;
4. только затем синтезировать несколько полных hardware architectures, включая все owners/controllers/bridges;
5. для каждой architecture с нуля решить exact modules, controllers, transport, GPIO/pins, memory, storage, power, antennas, STOP, recovery и cost;
6. отбросить hard-fail variants, сравнить только equivalent passing variants;
7. принимать всю архитектуру одним атомарным package по `DEC-0026`.

## Особо nRF24

Три nRF24 не привязаны заранее к S3, C5, третьему controller или одному physical owner. Фиксированы только три simultaneous full-function paths и их timing/calibration/safety/evidence contract. Placement решает полный package.

## Следствия

- `DEC-0022/0023/0026` сохраняются; меняется способ исполнения этапа 3;
- прежние stage-3 layouts, scorecards, budgets и owner comparisons архивируются;
- target README обоих репозиториев не получает архитектуру до атомарного owner acceptance;
- любое совпадение нового решения со старым само по себе не является доказательством.
