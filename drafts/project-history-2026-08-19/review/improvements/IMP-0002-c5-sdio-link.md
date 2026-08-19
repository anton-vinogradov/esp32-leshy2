# IMP-0002 — SDIO как обход GP-SPI блокера C5

- Статус: **⚠️ Предложение; требует архитектурного решения и прототипа**
- Связано: `FND-0001`, `DEC-0001`
- Этап решения: 3
- Обнаружено: 2026-08-15

## Legacy-ограничение

Legacy использует единственный general-purpose SPI C5 одновременно как S3↔C5 slave и как nRF24 master, что невозможно.

## Обход

Использовать S3 как SDMMC host, C5 как dedicated SDIO slave, а GP-SPI C5 полностью отдать трём nRF24. Для первого прототипа достаточно 1-bit SDIO (`CLK`, `CMD`, `DAT0`, `DAT1`); `DAT1` несёт interrupt, поэтому отдельный `DRDY` может не понадобиться.

Официальные Espressif-драйвер и пример предоставляют FIFO, shared registers, interrupts и DMA. S3 SDMMC host допускает гибкие GPIO; C5 module выводит фиксированные SDIO-линии. Legacy уже резервирует пять межпроцессорных сигнальных линий и сообщает о шести свободных GPIO S3 после split, поэтому вариант не требует очевидного увеличения межплатного разъёма.

## Цена и риски

- обязательные pull-up на CMD/DAT и high-speed routing;
- проверить точную ревизию C5: ранние v0.0/v0.1 не поддерживают SDIO slave;
- проверить конфликт фиксированных SDIO GPIO C5 с nRF/IR/strap/USB на реальном модуле;
- протокол сложнее UART и требует recovery/flow-control тестов;
- throughput/latency должны быть измерены на характерном 5 ГГц capture-трафике.

## Источники

- [ESP32-C5 SDIO slave driver](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/peripherals/sdio_slave.html)
- [ESP32-S3 SDMMC host](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdmmc_host.html)
- [Official SDIO host/slave example](https://github.com/espressif/esp-idf/blob/master/examples/peripherals/sdio/README.md)
- [ESP32-C5-WROOM-1/1U datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html)

Предложение не закрывает `FND-0001` до pin audit, минимального прототипа и решения владельца.
