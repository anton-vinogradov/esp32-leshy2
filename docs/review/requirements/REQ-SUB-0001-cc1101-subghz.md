# REQ-SUB-0001 — CC1101 Sub-GHz receive, decode and controlled-TX contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-SUB-01`–`C-SUB-11`, `C-X-01`–`C-X-03`, `C-X-05`, `C-X-08`, `C-UX-01`, `C-UX-03`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0010`, `DEC-0022`, `DEC-0023`

## Граница документа

CC1101 — узкополосный packet transceiver с RSSI и последовательно перестраиваемым synthesizer, а не wideband SDR, realtime spectrum analyzer или precision frequency counter. Полезный Sub-GHz scope сохраняется; каждое TX-действие привязано к квалифицированной полосе, RF frontend, региональному профилю и происхождению сигнала.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-SUB-01` | `C-SUB-01` | `conditional` | Основной | Frequency hunter сканирует только квалифицированные диапазоны CC1101/RF path, показывает tuned frequency, RSSI, bandwidth/dwell/calibration и uncertainty. Название «frequency counter» в UI не используется без внешнего instrument-grade proof. |
| `REQ-SUB-02` | `C-SUB-02` | `conditional` | Основной | Sequential RSSI spectrum/waterfall показывает sample age, step, dwell, missed windows и saturation; это не simultaneous FFT/IQ/realtime spectrum. |
| `REQ-SUB-03` | `C-SUB-03`, `C-SUB-04` | `conditional` | Основной | RAW OOK capture, squelch-triggered recording и multiband hopper сохраняют exact radio profile, timing, RSSI и coverage/loss. UI предупреждает о пропуске коротких сигналов при hopping. |
| `REQ-SUB-04` | `C-SUB-05` | `conditional` | Основной/Лаборатория | Versioned licensed decoder corpus распознаёт только доказанные static protocols; rolling-code observation выдаёт структуру/confidence без обещания секрета, синхронизации или универсального decode. Third-party security analysis — Lab. |
| `REQ-SUB-05` | `C-SUB-08` | `include` | Основной | Signal library хранит typed provenance (`own`, `authorized`, `unknown`), band/profile/timing, sensitivity, tags и immutable original; import остаётся inert. |
| `REQ-SUB-06` | `C-SUB-06`, `C-UX-03` | `conditional` | Основной | One-shot replay собственного tagged-сигнала разрешён только для квалифицированного licence-exempt/authorized profile после preview; неизвестный capture не повышается до Main автоматически. |
| `REQ-SUB-07` | `C-SUB-06` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Unknown/security replay и protocol emulation требуют exact authorized receiver/fixture, schema/profile preview, bounded repeat/time, conservative power, dead-man, actual-TX and STOP. |
| `REQ-SUB-08` | `C-SUB-08` | `conditional` | Смешанный | Playlist как организация библиотеки — Main; каждое TX-событие независимо проверяет provenance/region/target/gate. Playlist не превращается в массовый universal replay. |
| `REQ-SUB-09` | `C-SUB-07` | `conditional` | Контролируемая зона, `BOTH` | Fixed-code/de Bruijn resilience test работает только conducted/RF-shielded на authorized fixture с bounded corpus, no-leakage check, minimum power, rate/count/time ceiling и independent STOP. |
| `REQ-SUB-10` | `C-SUB-09` | `conditional` | Внутренний configuration API | Arbitrary register/profile editor доступен как validated expert configuration: hard electrical/regional limits нельзя обойти импортом или raw register write. |
| `REQ-SUB-11` | `C-SUB-09` | `conditional` | Контролируемая зона, `BOTH` | CW/test-tone только conducted/RF-shielded на authorized load/fixture, minimum power, hard timeout and actual-TX proof. |
| `REQ-SUB-12` | `C-SUB-10` | `conditional` | Сквозной hardware | SP4T/filter control входит только вместе с exact band/filter truth table, safe power-up, loss/isolation measurement and antenna no-TX state; одна GPIO-команда не считается квалифицированным RF path. |
| `REQ-SUB-13` | `C-SUB-11` | `conditional` | Контролируемая зона, `BOTH` | Narrow single-target interference/reactive resilience source — conducted/RF-shielded only. Open-air jammer, unattended mode, sweep/full-band interference и external trigger bypass отсутствуют. |
| `REQ-SUB-14` | `C-X-05`, `C-UX-01` | `conditional` | Основной/Лаборатория | Combined view/wardrive объединяет timestamped measurements, но не приписывает протокол energy-only sample; foreground privacy session and external-GNSS provenance mandatory. |
| `REQ-SUB-15` | все TX | `conditional` | Сквозной regulatory/safety | Qualified region/band/duty/power/antenna profile, explicit target, conservative default, per-tool arming, dead-man, independent STOP, actual-TX indication и reset/crash safe state обязательны. |
| `REQ-SUB-16` | all records | `conditional` | Сквозной storage | Raw timing/profile metadata versioned and fuzzed; sensitive capture encrypted with export/delete/retention policy; corrupt/imported data cannot arm TX. |
| `REQ-SUB-17` | все | `acceptance` | Сквозной HIL | Exact CC1101/front-end/antenna fixture measures frequency error, sensitivity, RSSI repeatability, scan loss, filters, TX power/harmonics/duty, coexistence, STOP/reset and contained tests across every enabled band. |

## Явно не обещается

- realtime/IQ/FFT spectrum или calibrated instrument-grade frequency counter;
- универсальный rolling-code decode/bypass;
- RF bands outside exact qualified CC1101/filter/antenna path;
- open-air brute-force, replay или jammer чужого оборудования.

## Первичный источник

- [Texas Instruments CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
