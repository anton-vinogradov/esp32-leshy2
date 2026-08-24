# Сводный результат digital interfaces

`H3.4` проведён ревью: проходят все три leaf-пакета, `162` их checks и `27` сквозных сводных checks. Незакрытых аналитических findings нет. Точный текущий маркер — `H3.5.1`.

## Закрытый аналитический envelope

| Граница | Проверенный результат |
|---|---|
| Levels и quiet state | Проходят 130 controller allocations, 13 interface groups, 13 reset/off contracts и все шесть no-back-power invariants |
| Display и storage | Direct QSPI 40 МГц, work quanta <=1 мс, full-frame payload 15,36 мс; квалифицированная SD сохраняет >=4 МБ/с, а 512 КиБ покрывают 349,525 мс |
| Audio | Full-duplex stereo 48 кГц, BCLK 3,072 МГц и DMA-ring 21,333 мс на отдельном controller |
| Compatibility radios | Три одновременно полнофункциональных nRF24 и CC1101 имеют независимый SPI/DMA service; worst serialized drain трёх nRF равен 79,2 мкс при guard 457,5 мкс |
| IPC | S3-RP и S3-C5 допускают >=1,5 МБ/с; S3-RP сохраняет 675 кБ/с сверх теоретического payload трёх nRF плюс CC |
| M1 и расширения | Проходят M1 на 80 контактов/51 net, защищённые ветки U214/native Unit, U214 SPI 10 МГц/I2C 150 пФ и data-only service USB |

Правило one-active-signal-group остаётся продуктовым. Оно не сериализует три nRF24: это намеренно одновременная группа с независимыми engines, полным RX/TX/mixed-role режимом и ограниченным временем обслуживания FIFO.

## Сохранённая физическая граница

Все `19` остаточных пунктов остаются явными измерениями H5/H8: far-end levels/eyes, reset/brownout captures, экземпляры SD, DMA и IPC traces, timing радио-FIFO, стыковка и loading M1/U214, неправильное использование расширений и service USB с несколькими hosts. H3.4 не переименовывает их в пройденную симуляцию.

В evidence сохранено одно исправление саморевью: пересчёт пФ в нс для U214 I2C исправлен до принятия; 150 пФ теперь дают 279,609 нс при лимите 300 нс.

Машинное evidence: [`H3-VRF44-digital-consolidation.json`](../hardware/verification/generated/H3-VRF44-digital-consolidation.json).
