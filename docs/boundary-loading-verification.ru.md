# Loading M1, expansions и service boundaries · historical R1

`H3.4.3` проверено: `49` машинных checks, незакрытых аналитических findings нет. Исторический маркер прогресса R1 — `H3.6.1`.

## Worst-case границы M1

Точная 80-контактная пара FX8C переносит 51 net. Даже нарочно сверхконсервативное предположение, что весь принятый main rail 2,5 А проходит через M1, нагружает каждый из семи контактов лишь на `0.357 А` при rating 0,4 А; максимальные connector drop `28.571 мВ`, loss `71.429 мВт`. AON использует `0.082 А` на контакт. Каждый IPC/USB contact соседствует с POWER_GROUND; каждый low-level audio contact находится не дальше двух позиций от AUDIO_GROUND. Rating connector 8 Гбит/с в `16.667 раза` выше USB2 High-Speed.

## Границы expansions

Каждая активная 5-В ветка ограничена 1,25 А ниже гарантированного eFuse floor 1,632 А (margin `23.407%`). Envelope пути 60 мОм даёт `75.000 мВ` и `93.750 мВт`. One active signal group делает U214 и native Unit взаимоисключающими в эксплуатации; даже ошибочный двойной запрос на обоих eFuse floors суммарно равен `3.264 А` и остаётся ниже converter floor 4 А.

Контролируемая пара HLE/TSM рассчитана на 4,1 А на pin, native `1125R-SMT-4P` — на 2 А. Неописанные material/plating штырей stock U214 всё равно остаются received-sample gate H5: rating розетки молча не присваивается её ответной части.

U214 SPI допускается на 10 МГц: buffer 4,7 нс и envelope 22 Ом/30 пФ оставляют `43.848 нс` внутри half-cycle. U214 I2C допускается только при <=150 пФ (`279.609 нс` с 2,2 кОм). Native Unit profiles остаются <=400 кГц I2C или <=1 Мбит/с UART; 1-Wire — только HIL.

Service VBUS не может питать продукт. Два service ports потребляют лишь 10 мкА через bleeders; четыре data lines при снятом питании ограничены 8 мкА через точные FSUSB42. Signal integrity и wrong-accessory injection остаются семью явными gates H5/H8.

Машинное evidence: [`H3-VRF43-boundary-loading.json`](../hardware/verification/generated/H3-VRF43-boundary-loading.json).
