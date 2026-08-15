# REQ-RX-0001 — Si4732 broadcast/HF receiver, scan, record and decode contract

- Статус набора: **На ревью; ожидает решение `IMP-0013`**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-RX-01`–`C-RX-07`, пересечения `C-X-01`, `C-X-02`, `C-X-05`, `C-X-08`, `C-X-11`
- Обязательные решения: `DEC-0002`, `DEC-0005`, `DEC-0009`, `DEC-0010`, `DEC-0013`
- Открытое несоответствие: `FND-0010`
- Условные входы реализации: RF/frontend, audio, storage, decoder, coexistence и HIL proof следующих этапов

## Граница документа

Этот набор определяет результат встроенного receive-only backend Si4732-A10. Он не выбирает окончательную driver library, task model, presets database, WAV filesystem layout, decoder implementation или RF protection topology.

Приёмник не создаёт TX-path и находится в основном уровне. Локальная запись и декодирование требуют явного запуска, privacy notice и применимого регионального профиля; этот документ не делает универсальных выводов о законности прослушивания или записи конкретного сигнала.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-RX-01` | все | `baseline` | Основной | Backend подтверждает Si4732 product/revision/component/firmware properties и показывает diagnostic identity. Неизвестная или несовместимая revision не получает blanket compatibility; недоступные режимы скрыты либо явно отключены. |
| `REQ-RX-02` | `C-RX-01` | `baseline` | Основной | FM broadcast profile покрывает документированный 64–108 MHz диапазон с региональными spacing/de-emphasis/band limits, manual tune и seek. Аппаратный product output остаётся mono по `DEC-0009`; UI не обещает stereo output. |
| `REQ-RX-03` | `C-RX-01` | `baseline` | Основной | RDS/RBDS показывает только валидированные PI/PS/PTY/RT/clock поля, учитывает block errors, очищает stale text и не использует непроверенное эфирное время как безусловный RTC authority. Отсутствие RDS явно отлично от parser/I²C fault. |
| `REQ-RX-04` | `C-RX-02` | `baseline` | Основной | Обычная AM поддерживает только квалифицированные региональные LW/MW/SW band profiles внутри документированных возможностей receiver/frontend. Частоты, шаг, полоса, antenna path и units видимы; расширение за доказанную RF/front-end границу не обещается. |
| `REQ-RX-05` | часть `C-RX-03` | `conditional` | Основной | USB/LSB и CW listening через BFO доступны только после успешной загрузки совместимого SSB patch по принятому варианту `IMP-0013`. Patch status, BFO sign/offset и filter width видимы; ordinary AM не маркируется как SSB. |
| `REQ-RX-06` | часть `C-RX-03` | `defer` | Основной | Synchronous-AM не входит в обещанный baseline до отдельного primary-source и on-target proof. Ordinary AM, SSB/BFO или host audio post-processing нельзя называть synchronous-AM без измеримого carrier-lock contract. |
| `REQ-RX-07` | `C-RX-04` | `baseline/conditional` | Основной | Manual tune, seek, presets и regional band plans работают транзакционно; supported bandwidth, AGC/attenuation, soft-mute, AVC, AFC/calibration и BFO показываются только для применимого mode/component. Ошибка mode switch восстанавливает последний валидный receive state. |
| `REQ-RX-08` | `C-RX-04` | `baseline` | Основной | S-meter/diagnostics показывает frequency, tune-valid, RSSI, SNR и доступные multipath/AFC indicators с units, update age и saturation/unknown state; значения не выдаются за calibrated field strength до fixture calibration. |
| `REQ-RX-09` | `C-RX-05` | `conditional` | Основной | Bandscope является последовательным tune/RSSI sweep, а не FFT/IQ/real-time spectrum. UI показывает start/stop/step/dwell/elapsed age и пропуски; sweep прерываем, безопасно управляет audio mute и не обещает обнаружить сигнал короче dwell/scan cycle. |
| `REQ-RX-10` | `C-RX-06` | `conditional` | Основной | Scanner log пишет timestamp/source, frequency, mode, step/dwell, RSSI/SNR/validity и profile ID в versioned bounded records на SD. Full/remove/power-loss восстанавливаются без выдачи повреждённого хвоста за валидный лог; raw content не пишется без отдельного record consent. |
| `REQ-RX-11` | часть `C-RX-07` | `conditional` | Основной с privacy gate | WAV capture по `DEC-0009` запускается явно, записывает mono с видимыми rate/bit depth/source/duration/space estimate и различает drop/overrun. Stop, SD full/remove, reset и power loss закрывают либо восстанавливают файл; ложная stereo fidelity не заявляется. |
| `REQ-RX-12` | часть `C-RX-07` | `conditional` | Основной с privacy gate | CW/RTTY/SSTV/WEFAX decoders принимаются по отдельным versioned test corpora, mode/rate/tone scope и false-positive thresholds. UI хранит raw-audio reference и confidence/error state; «что-то распознано» не считается proof всех вариантов протокола. |
| `REQ-RX-13` | пересечения TX | `conditional` | Сквозной | Любой onboard/external TX, способный перегрузить Si4732/frontend/audio, до keying переводит receiver в доказанное mute/blank/protect state, а после TX выполняет bounded recovery/retune. Одновременный RX во время TX не обещается без isolation/desense HIL. |
| `REQ-RX-14` | все | `conditional` | Сквозной | Reset, brownout, I²C fault и mode/power transition не создают опасного pop, зависшего patch/tune state или ложных данных. Analog bypass сохраняет обычное прослушивание там, где это допускает hardware; volatile patch state после потери питания всегда `not loaded`. |
| `REQ-RX-15` | запись/декод | `baseline policy` | Сквозной | Нет auto-upload и скрытой фоновой записи. Export/delete локальны, session metadata показывает source/время и privacy scope; security/legal уровень принятого сигнала не меняется только потому, что subsystem receive-only. |

## Обязательные acceptance-наборы

### Receiver API и диапазоны

- identity/firmware query, I²C timeout/recovery и unsupported command fixtures;
- lower/upper-edge FM/LW/MW/SW tuning, regional steps/de-emphasis и invalid frequency rejection;
- RDS clean/error/stale/FIFO traces, seek stop/threshold и RSSI/SNR/AGC state transitions;
- ten-minute tune/audio soak и repeated FM↔AM↔conditional SSB transitions.

### Sweep, storage и audio

- signal-generator sweep с известными carriers, timing budget и доказательством sequential RSSI semantics;
- scan cancel, storage full/remove, corrupt tail and power-cut recovery;
- WAV rate/bit-depth/header/duration, clipping/noise, overrun и mono path verification;
- audio mute/pop/click и analog-bypass regression по `DEC-0009`.

### Patch и декодеры

- все negative patch cases из `IMP-0013`, если принят вариант с SSB;
- USB/LSB/BFO/filter fixtures; synchronous-AM отдельно до снятия `defer`;
- versioned clean/noisy/off-frequency corpora для каждого принятого CW/RTTY/SSTV/WEFAX mode;
- CPU/RAM/storage/thermal budget при одновременных UI, audio capture и decoder tasks.

### RF coexistence и privacy

- limiter/blanking/desense HIL для SA868 и каждого другого TX-path на целевом enclosure/antenna configuration;
- отсутствие ложного scan/decode результата после TX recovery;
- explicit record consent, no background content capture и deterministic delete/export tests.

## Стоимость без потери продукта

Документированный FM/AM baseline не добавляет BOM. Вариант `IMP-0013/A` сохраняет SSB/CW также без изменения BOM, но добавляет loader/UI/HIL NRE. Запись и декодеры используют уже принятый ES8311, однако требуют firmware/test effort и не считаются реализованными самим фактом наличия codec. Замена receiver допустима только как отдельное решение с доказанной дополнительной ценностью.

## Первичные источники

- [Skyworks AN332 — Si47xx programming guide](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN332.pdf)
- [Skyworks Si4732-A10 data short](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [Skyworks Si4730/31/34/35-D60 datasheet — documented receive bands](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si4730-31-34-35-D60.pdf)
- [PU2CLR SI4735 library](https://github.com/pu2clr/SI4735)
