# FND-0054 — three-nRF digital concurrency does not prove mixed-RF sensitivity

- Статус: **Подтверждено; ожидает `IMP-0039`**
- Дата: 2026-08-17
- Requirement: [`REQ-N24-0001`](../requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)
- Architecture: [`RFQ-0002`](../architecture/RFQ-0002-g2f-3i-rf-concurrency-boundary.md)
- Proposal: [`IMP-0039`](../improvements/IMP-0039-three-nrf-full-mix-acceptance.md)

## Находка

Предыдущий черновик ошибочно разбил nRF на `SG-N24-HUNT` и `SG-N24-TX` и
переводил два radio в standby при TX третьего. Это противоречит принятому
product demand: все три nRF должны одновременно оставаться полнофункциональными
и независимо исполнять любые `PRX`/`PTX` роли.

Исправленная digital карта это выдерживает: у каждого radio свои data bus,
CSN, CE, IRQ, PIO state machine и DMA pair. Но она не доказывает, что weak RX
сохранит isolated sensitivity рядом с local 2.4 GHz TX. На том же канале
возникают одновременно receiver blocking и обычная packet collision; далеко
разнесённые каналы улучшают selectivity, но требуют exact module/antenna/
enclosure HIL.

## Исправление и открытая граница

- split `HUNT/TX` удалён; canonical group теперь только `SG-N24`;
- automatic peer standby и hidden time-sharing запрещены;
- mixed role concurrency остаётся обязательной;
- status «Проведено ревью» не распространяется на mixed-TX/RX sensitivity до
  выбора `IMP-0039` и воспроизводимого OTA/conducted HIL.

## Первичный источник

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
