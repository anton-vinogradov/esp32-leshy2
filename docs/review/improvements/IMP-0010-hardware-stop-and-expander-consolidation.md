# IMP-0010 — аппаратный STOP и удаление `U14` без конфликта с audio

- Статус: **Частично принято: hard STOP — `DEC-0024`; matrix/удаление `U14` остаются layout-кандидатом**
- Связано: `FND-0006`, `FND-0007`, `IMP-0006`, `DEC-0003`, `DEC-0005`, `DEC-0008`, `DEC-0009`
- Этап решения: 3 — после owner-confirmed wishlist freeze и сравнения полных компоновок; схемная реализация и proof — этапы 3–9
- Обнаружено: 2026-08-16

## Контекст

Исходный `IMP-0006` экономит третий PCA9555 `U14`, занимая все восемь свободных `U13.P10..P17`. После принятия ES8311 три из тех же линий понадобились audio-control (`FND-0006`). Одновременно детальная проверка показала, что текущий `SW_STOP` — лишь вход `U14`, а не аппаратный TX-kill (`FND-0007`).

Два пробела потенциально можно закрыть одним контрактом: убрать STOP из GPIO-бюджета и сделать его независимым hardware path.

## Оставшееся условие решения

`DEC-0024` уже принимает независимую latched hard-STOP topology. Оно не выбирает `U14`, button matrix, audio-control pins или exact safety BOM. Эти элементы сравниваются внутри нескольких полных компоновок на сводном demand model: прямые GPIO S3/C5, expander lines, fixed-function/strap pins, S3↔C5 transport, audio, UI/touch и внешние модули.

## Layout-кандидат для UI/expander

Принять следующую целевую архитектуру:

1. `STOP` не входит в button matrix и не зависит от PCA9555; нажатие напрямую утверждает аппаратный `TX_INHIBIT`.
2. `TX_INHIBIT` удерживает ESP32-S3 и ESP32-C5 через `CHIP_PU` в reset/off и отдельно гасит TX-capable периферию, которая может сохранить TX-state после host reset.
3. Для SA868, CC1101, внешнего `EXT-RF14` и остальных трактов этап 3 выбирает отдельный fail-safe inhibit/power gate; простого reset S3 недостаточно.
4. Пока STOP удерживается, передача физически невозможна. После отпускания rails/MCU проходят нормальный power-on/reset и загружаются по `DEC-0003`: все TX off, Lab `DISARMED`, без автоматического re-arm.
5. Девять неаварийных кнопок образуют diode-isolated `3×3` matrix на шести линиях из `U13.P10..P17`; `TOUCH_INT` занимает седьмую линию.
6. Восьмая линия `U13` и две освободившиеся после удаления бортового LoRa линии `U12` (`LoRa_NRESET`, `LoRa_TR`) обслуживают три slow control ES8311/selectors из `DEC-0009`.
7. `U14`, его развязка и индивидуальные pull-up большинства кнопок удаляются только после HIL proof матрицы и STOP.

Конкретное распределение трёх audio-control между этими линиями остаётся выходом этапа 3. Настоящее предложение предлагает ресурсный контракт, а не окончательную нумерацию net/pin.

## Поведение пользователя

Цена универсального аппаратного STOP — аварийная перезагрузка интерфейса. Это намеренно: сохранить UI работающим и при этом аппаратно погасить встроенный Wi-Fi S3 без дополнительного RF-isolation hardware невозможно. После отпускания устройство загружается заново в безопасном состоянии.

Long-BACK остаётся быстрым software panic-kill без обязательной перезагрузки, но не заменяет физический STOP.

## Варианты

### A. Аппаратный STOP + matrix + удаление `U14` — рекомендуется

Закрывает safety-пробел и pin collision одновременно. Экономия на `U14` частично компенсирует hardware inhibit/power-gate, но итоговая дельта пока неизвестна.

### B. Сохранить `U14`, но STOP всё равно сделать аппаратным

Минимальный pin/firmware риск: обычные кнопки остаются point-to-point, audio-control помещается на пяти свободных линиях `U14`. Минусы — третий expander, его обвязка и placements остаются; аппаратный STOP всё равно добавляется отдельно.

### C. Оставить STOP программным входом `U14`

Самый простой текущий hardware, но STOP теряется при отказе S3/I²C/expander. Этот вариант не соответствует рекомендуемой safety-границе и не должен считаться эквивалентной экономией.

## Критерии доказательства варианта A

1. Для каждого TX-path построена таблица `STOP asserted → physical off mechanism → measured kill time → release state`.
2. STOP прекращает continuous/max-power TX при зависших S3, C5, I²C и каждой прикладной задаче; actual-TX LED подтверждает прекращение RF.
3. Удержание STOP не вызывает циклического re-arm, back-power или неопределённых rail states.
4. После отпускания оба MCU и все RF-компоненты проходят допустимую power/reset sequence и остаются TX-off до явного действия.
5. Все девять кнопок, одиночные нажатия и принятые chords проходят ghosting/debounce/latency test; отказ строки/столбца обнаруживается self-test.
6. Touch interrupt, audio selector defaults и codec control не ухудшаются из-за общей PCA9555/I²C нагрузки.
7. Сводный pin audit подтверждает отсутствие повторного назначения после выбора S3↔C5 transport, удаления onboard LoRa и реализации `DEC-0009`.
8. Полная BOM/PCB/assembly/test дельта вариантов A и B посчитана на `1/10/100/1000`; экономия `U14` не выдаётся за чистую до учёта STOP gates.

## Первичные источники

- [TI PCA9555 datasheet: per-pin input/output configuration and input interrupts](https://www.ti.com/lit/ds/symlink/pca9555.pdf)
- [ESP32-S3 datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
