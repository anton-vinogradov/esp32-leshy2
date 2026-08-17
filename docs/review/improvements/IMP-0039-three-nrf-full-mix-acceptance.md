# IMP-0039 — three-nRF full-mix RF acceptance

- Статус: **Принят вариант A решением `DEC-0047`**
- Дата: 2026-08-17
- Requirement: [`REQ-N24-0001`](../requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)
- Finding: [`FND-0054`](../findings/FND-0054-three-nrf-mix-needs-rf-acceptance.md)
- Group decision: [`DEC-0045`](../decisions/DEC-0045-one-active-signal-group.md)

## Контекст

Цифровая карта `G2F-3I` уже даёт каждому nRF отдельные SPI wires, PIO state
machine, DMA pair, CE, CSN и IRQ. Поэтому три state machine действительно могут
одновременно находиться в любых `PRX`/`PTX` ролях без ожидания общей шины.

Но local 0 dBm TX внутри корпуса попадает в соседний receiver намного сильнее
weak remote packet. По типовым selectivity данным nRF24L01+:

- same-channel требует wanted signal сильнее local leakage примерно на 7…12 dB;
- первые соседние каналы также дают слишком малое подавление для weak RX;
- только далеко разнесённые каналы дают порядка 48…60 dB typical rejection,
  причём эти цифры специфицированы не у sensitivity floor и требуют проверки
  exact module/antenna/enclosure.

Даже оптимистичные 150 mm и свободное пространство дают около 23.7 dB path
loss на 2.44 GHz. При 0 dBm local TX это порядок −24 dBm на соседнем входе до
дополнительной развязки. Поэтому same-channel weak RX во время local TX не
может стать универсальной гарантией обычным фильтром: фильтр одновременно
ослабит и wanted signal.

## Вариант A — полный mix с квалифицированным RF envelope (рекомендуется)

Все сочетания `3×PRX`, `1T+2R`, `2T+1R`, `3T` реализуются без скрытых gaps.
Для mixed TX/RX manifest задаёт доказанные ограничения channel separation,
data rate, TX power, antenna pose и минимальный wanted/RPD test level. UI/log
показывает профиль. Same/near-channel weak-signal сохранение полной
чувствительности помечается `unsupported physics`, но сами роли PTX/PRX и
пакетный обмен не урезаются. Exact acceptance floor определяется OTA/conducted
HIL на целевой геометрии.

Цена: отдельные антенны/зонирование, shield/feed filtering, измерительные точки,
packet rail и bulk, рассчитанные на реальный одновременный `3T` peak/average,
и HIL; возможно групповое снижение мощности/расширение channel separation.
Плюс: остаётся реальный полезный одновременный mix внутри base device без
ложного обещания same-frequency full duplex.

## Вариант B — arbitrary channel + weak-signal RX как жёсткая гарантия

Требовать сохранения близкой к изолированной sensitivity даже когда соседний
nRF передаёт на том же/соседнем канале. Обычные три nRF24 внутри handheld это
не обеспечивают. Понадобятся физически вынесенные/проводные RF heads,
экранированная комната либо специализированное self-interference-cancellation
оборудование; размер, стоимость и product archetype меняются, а same-channel
packet collision всё равно нельзя отменить.

Цена: максимальная, base-device архитектура не сходится на текущем корпусе и
BOM; результат остаётся сильно зависимым от конкретной установки.

## Вариант C — незаметно time-slice RX вокруг TX

Радио логически остаются назначенными PRX/PTX, но RX получает gaps во время
локальных TX bursts. Это дешевле, однако противоречит прямому требованию
одновременности «без тормозов» и потому не рекомендуется.

## Рекомендация

Принять A: hardware/runtime обязаны реализовать любой одновременный mix, а
качество RX во время local TX является versioned измеренным RF envelope.
Вариант B оставить отдельным Laboratory remote/conducted fixture, не base BOM.

## Решение владельца

[`DEC-0047`](../decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md)
принимает вариант A. Заказанный второй device используется как внешний
observer/peer по [`N24H-0001`](../architecture/N24H-0001-two-device-full-mix-fixture.md).
Он измеряет и воспроизводит профиль, но не становится обязательной частью base
product и не превращает один nRF24 в same-frequency full duplex.

## Первичный источник

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
