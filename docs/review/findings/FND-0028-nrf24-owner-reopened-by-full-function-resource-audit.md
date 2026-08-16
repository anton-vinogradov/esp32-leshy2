# FND-0028 — владелец 3×nRF24 переоткрыт full-function/resource audit

- Статус: **Три static layouts сравнены; owner decision открыт в `IMP-0021/CMP-0001`**
- Серьёзность: architecture/resource/performance blocker
- Затрагивает: `DEC-0001`, `DEC-0009`, `FND-0001`, `FND-0019`, `REQ-N24-0001`, S3↔C5 transport и stage-3 pin budget
- Обнаружено: 2026-08-16

## Несоответствие

`DEC-0001` ранее назначил три nRF24 C5, но не доказывал оптимальность или реализуемость. Детальный аудит показал:

- C5 имеет один GP-SPI, а legacy одновременно назначает его S3↔C5 slave и nRF24 master (`FND-0001`);
- legacy C5 pin budget использует один общий CE, что не позволяет независимо назначать трём полнофункциональным radio разные PTX/PRX sessions;
- текущая физическая разводка уже ведёт nRF24 на S3, хотя сама ещё не qualified и также использует общий CE (`FND-0019`);
- S3 имеет два GP-SPI, владеет UI/storage/security parsing и теперь baseline BLE (`DEC-0021`), но его общий SPI2 разделён с display/SD/CC1101/U214, а четыре I²S-линии ES8311 должны войти в тот же pin budget;
- внешний U214 не освобождает legacy SPI/UART/IRQ/BUSY pins: официальный Cap-Bus использует SPI, IRQ, BUSY, RST и отдельный GNSS UART.

Владелец потребовал полнофункциональные nRF24 и предложил заново проверить S3 как возможного лучшего владельца. Поэтому старое C5 ownership нельзя использовать как окончательный вход этапа 3 без повторного решения.

## Критерий закрытия

После `DEC-0023` три полные static-компоновки сравнены в `CMP-0001`. Выбранный вариант назначает одного владельца всех трёх radio и доказывает:

1. независимые logical CS/CE/role/channel/rate/address для каждого тракта;
2. bounded IRQ source identification и отсутствие packet-loss overclaim;
3. совместимость с ES8311 I²S, U214, IR C5, USB/recovery и S3↔C5 transport;
4. measured bus latency/throughput при display/SD/radio load;
5. reset-safe CE, STOP/dead-man, exact-module power/RF/antenna и HIL;
6. отсутствие скрытой потери capability или ложной zero-loss экономии.

## Источники

- [ESP32-S3: два GP-SPI controller](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5: один GP-SPI и отдельный SDIO slave](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [M5Stack U214 Cap-Bus pin map](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
