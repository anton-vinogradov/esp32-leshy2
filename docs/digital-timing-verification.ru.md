# Digital bandwidth, latency и timing

`H3.4.2` проверено: `40` машинных checks, незакрытых аналитических findings нет. Точный текущий маркер — `H3.4.4`.

## Закрытые бумажные бюджеты

| Тракт | Проверенный результат |
|---|---|
| Display + storage | Quad display 40 МГц даёт 20 МБ/с и полный RGB565 frame за `15.360 мс`; каждый display quantum — 20 кБ/1 мс. Qualified SD profile 50 МГц оставляет ровно 4,0 МБ/с после 1,25 МБ/с protocol/card reserve и 1,0 МБ/с allowance дисплея. Ring 512 КиБ покрывает `349.525 мс` при записи 1,5 МБ/с. |
| Audio | 48 кГц, stereo, samples 24 bit в slots 32 bit: BCLK 3,072 МГц, payload 288 кБ/с в каждом направлении и `21.333 мс` в четырёх DMA buffers. |
| Три nRF24 | Каждый отдельный SPI 10 Мбит/с выгружает 32 bytes за `26.400 мкс`; даже serial upper bound трёх radios — `79.200 мкс` при guard трёхуровневого FIFO >`457.500 мкс`. |
| CC1101 | Watermark 32 bytes заполняется за `426.667 мкс` при 600 кбит/с и выгружается за `26.400 мкс` по SPI 10 Мбит/с. |
| S3↔RP | Payload floor 1,5 МБ/с превышает теоретический payload трёх nRF плюс CC (`0.825 МБ/с`) на `0.675 МБ/с`. |
| S3↔C5 | One-bit SDIO 20 МГц даёт 2,5 МБ/с raw; admitted occupancy 70% оставляет 1,5 МБ/с payload и 0,25 МБ/с framing. Это admitted waterfall/metadata/events, а не обещание переслать каждый raw Wi-Fi frame или RF sample. |
| SYS_I2C | Нарочно крупная transaction 32 bytes занимает `0.812 мс`; sweep одиннадцати clients — `8.938 мс`, намного меньше обычного UI deadline 100 мс. |

Режим SD 50 МГц разрешён только после проверки identity и CMD6 high-speed admission. Fallback-карта может работать на 25 МГц, но не получает заявленный профиль 4 МБ/с. Radio FIFO не делит controller, PIO state machine или persistent DMA channel с display/storage.

Семь физических timing gates явно остаются H8: logic-analyzer traces, реальные media stalls, USB/IPC load и audio underrun/overrun stress.

Машинное evidence: [`H3-VRF42-digital-timing.json`](../hardware/verification/generated/H3-VRF42-digital-timing.json).
