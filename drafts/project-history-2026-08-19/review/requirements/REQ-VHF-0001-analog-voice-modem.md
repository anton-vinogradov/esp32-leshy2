# REQ-VHF-0001 — analog voice, signalling, modem and relay contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-VHF-01`–`C-VHF-07`, пересечения `C-X-01`, `C-X-02`, `C-X-05`, `C-X-07`, `C-X-11`, `OUT-07`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0009`, `DEC-0010`, `DEC-0013`, `DEC-0016`, `DEC-0024`, `DEC-0025`
- Находки: `FND-0003`, `FND-0007`, `FND-0011`–`FND-0014`
- Условные входы реализации: backend/BOM, STOP/PTT, RF/legal profile, audio/modem/storage/network и HIL proof следующих этапов

## Граница документа

Этот набор определяет пользовательский результат half-duplex analog-FM voice-radio backend. По `DEC-0016` preferred conditional target — SA518 dual-band 136–174/400–470 MHz; текущий SA868S остаётся честным UHF-only 400–470 MHz fallback до stage-4 qualification. Их диапазоны, мощность, pinout и protocol никогда не смешиваются как одна доказанная деталь.

Наличие перестраиваемого TX не создаёт права передачи. Без активного квалифицированного regional/operator profile subsystem работает RX-only. Этот документ не выдаёт CEPT PMR446 или amateur rules за универсальные правила другой юрисдикции.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-VHF-01` | все | `conditional` | Основной | По `DEC-0016` production manifest фиксирует exact module, preferred SA518 либо fallback SA868S, hardware/firmware revision и protocol profile. UI показывает backend identity и доказанные RX/TX ranges; fallback всегда UHF-only, неизвестная revision не получает blanket compatibility. |
| `REQ-VHF-02` | `C-VHF-01` | `baseline policy` | Основной | Без применимого region/licence/operator profile TX отсутствует или остаётся disabled. Profile versioned и задаёт RX/TX frequencies, spacing/bandwidth, tone/code, power ceiling, antenna/ERP assumptions, callsign/ID, duty/timeout и expiry; пользовательские частоты не обходят hardware STOP и explicit arming. |
| `REQ-VHF-03` | `C-VHF-01` | `conditional` | Сквозной safety | По `FND-0011` reset/high-Z default: `PD=0`, `PTT=1`, `H/L=low`. По `DEC-0025` SA518 использует отдельный STOP-dominant `VVOICE` около 4.0 V, а каждый fallback имеет явный stuffing/supply manifest. Модуль включается RX-only, low-power readback/profile применяется до arming. High-power появляется только после явного выбора текущего сценария и доказанного fail-safe H/L path; module EEPROM не восстанавливает armed/high state. |
| `REQ-VHF-04` | `C-VHF-01` | `conditional` | Основной | Manual PTT — hold-to-transmit с видимыми frequency/profile/power/callsign и actual-TX indication. Release, timeout, STOP, session exit, screen lock, watchdog, low battery, audio fault или profile expiry снимают PTT; повторное включение не происходит автоматически. |
| `REQ-VHF-05` | `C-VHF-01` | `conditional` | Основной | Ordinary analog RX и mic voice сохраняют hardware-default bypass по `DEC-0009`. RX/TX frequency могут различаться только внутри разрешённого profile; split не называется duplex и не разрешает simultaneous RX/TX. |
| `REQ-VHF-06` | `C-VHF-02` | `conditional` | Основной | CTCSS/CDCSS, squelch, volume и доказанная bandwidth/filter configuration применяются транзакционно и повторно после reset. Tone/code не называется encryption/privacy. Unsupported/readback-unknown состояние видно; firmware cache не выдаётся за module state. |
| `REQ-VHF-07` | `C-VHF-03` | `conditional` | Основной RX | Channel scan использует binary vendor sweep и raw vendor-relative RSSI с явными dwell/step/age semantics. RSSI не маркируется dBm без calibration. CTCSS/DCS tone scan доступен только после host-audio/filter/corpus proof; отсутствие decode не означает отсутствие carrier. |
| `REQ-VHF-08` | `C-VHF-04` | `conditional` | Основной TX | Roger beep, manual 1750 burst и DTMF encode генерируются через доказанный DAC→`MIC_IN` path, никогда сами не выбирают частоту/мощность и не поднимают PTT вне текущей armed manual session. Tone duration/deviation/filter response ограничены profile и HIL. |
| `REQ-VHF-09` | `C-VHF-04` | `defer` | Основной TX | VOX отсутствует до закрытия `FND-0013`. Будущая реализация требует mic capture/special variant, отдельной armed session, threshold/hang/false-trigger tests и hard maximum key time; VOX не является persistent global default. |
| `REQ-VHF-10` | `C-VHF-04` | `conditional` | Лаборатория | Simplex parrot записывает только bounded RX segment и retransmits после приёма, никогда не одновременно. Default-off, явный authorized channel/content scenario, ID/duty/max-session/storage/privacy gates и STOP обязательны; неизвестный/third-party content не ретранслируется молча. |
| `REQ-VHF-11` | `C-VHF-05` | `conditional` | Основной RX с privacy gate | DTMF decode работает по versioned clean/noisy/twist/level corpus, показывает confidence/raw reference и не запускает команду по одному decode без отдельного authenticated rule. RX content не записывается/передаётся в сеть скрытно. |
| `REQ-VHF-12` | `C-VHF-06` | `conditional` | Основной licensed data | AFSK1200/AX.25/APRS RX/TX и KISS TNC требуют interoperable golden frames, deviation/timing/CSMA/channel-busy tests, callsign/profile gate и explicit TX. SA868S fallback покрывает только разрешённые UHF profiles; VHF/2 m требует принятого dual-band/другого backend. Proprietary SA518 short-data не называется AX.25. |
| `REQ-VHF-13` | `C-VHF-06` | `conditional` | Основной licensed/networked | APRS iGate по умолчанию receive-only; Internet upload требует endpoint credentials, privacy notice, duplicate/path filtering, rate/backpressure и no-fix semantics из `REQ-GNSS-0001`. RF transmit/digipeat — отдельная вооружаемая функция, не следствие сетевого подключения. |
| `REQ-VHF-14` | `C-VHF-06` | `conditional` | Основной licensed TX | SSTV TX и fox-hunt beacon имеют отдельные protocol fixtures, callsign/ID, location privacy, interval/duty/max-duration и explicit start/stop. Beacon state не восстанавливается после reset/update; storage/audio error снимает PTT. |
| `REQ-VHF-15` | `C-VHF-07` | `conditional` | Основной RX / Лаборатория TX | UHF/VHF RX WAV следует `REQ-RX-0001` storage/privacy semantics. Cross-band Si4732→voice-radio relay — default-off Lab session с bounded buffer, authorized destination/content, ID/duty/timeout и STOP; наличие audio route не является разрешением ретрансляции. |
| `REQ-VHF-16` | `OUT-07` | `defer` | Отдельный future scope | Current SA868S/SA518 analog backend остаётся half-duplex и не обещает true duplex repeater, DMR/C4FM/dPMR или vocoder. Эти product functions не получают `exclude-proven`: отдельный dual-radio/duplexer либо digital-voice expansion рассматривается после user-value, BOM/RF isolation и legal review. |
| `REQ-VHF-17` | все TX | `conditional` | Сквозной | `FND-0007` закрывается независимым hardware STOP/TX power gate, actual-TX detection и fault-injection. I²C/PCA9555, UART, codec, UI и application state не являются единственным способом снять PTT. |
| `REQ-VHF-18` | все | `conditional` | Сквозной | Conducted RF и enclosure HIL измеряет frequency error, occupied bandwidth/deviation, harmonics/spurs, low/high power spread, 1 A-class supply transient, thermal/duty и desense каждого onboard/external receiver. TX arbitration действует до PTT, а recovery не создаёт ложный carrier/decode. |
| `REQ-VHF-19` | PMR legacy note | `exclude-current-hardware` | Сквозной legal | По `FND-0014` текущий external-SMA product не называется licence-exempt PMR446 equipment. Channel table допустим для RX/reference либо отдельно разрешённого profile; licence-exempt SKU требует integral antenna, ERP/conformity и country qualification. |

## Обязательные acceptance-наборы

### Backend, UART и state recovery

- exact variant/revision manifest, handshake/timeout/malformed response/retry и UART fuzz;
- protocol frequency edges, official 470/480 inconsistency и invalid group/tone/code rejection;
- reset/power-cycle reapplication с доказательством, что EEPROM state не вооружает TX;
- binary sweep, raw RSSI monotonicity/calibration и unsupported feature UI.

### TX safety, power и RF

- oscilloscope trace `PD/PTT/H-L` for power-on/reset/brownout/watchdog/expander fault/STOP;
- held/stuck PTT, UART hang, codec overrun и low-battery fault injection;
- conducted low/high power over VBAT/temperature, deviation, occupied bandwidth, spurs/harmonics;
- antenna mismatch/no-load protection boundary, thermal/duty soak and receiver desense matrix.

### Audio, signalling и modem

- bypass voice intelligibility plus ES8311 capture/injection gain/noise/pop/latency;
- CTCSS/CDCSS host tone-scan corpus with filter/pre-emphasis combinations;
- DTMF level/twist/duration, 1750/roger deviation and false-command protection;
- AFSK1200/AX.25/APRS golden frames, KISS framing/backpressure and real-radio interoperability;
- WAV/parrot/relay storage full/power cut, privacy and session timeout.

### Legal/profile behavior

- no-profile is RX-only; profile expiry/change disarms immediately;
- callsign/ID, frequency, power, duty and timeout cannot be bypassed by imported preset;
- CEPT PMR reference never displays a false licence-free/compliant claim;
- destructive/disruptive test transmitters, если появятся позже, остаются только в Контролируемой зоне по `DEC-0010`.

## Стоимость без потери продукта

`FND-0011` adds three passives and reduces current draft risk. ES8311 already pays the prerequisite for RX capture/TX injection, but does not pay for mic capture/VOX. `DEC-0016` may replace one module with one module and reduce peak power stress, yet price/stock are unknown, board area grows, and 2 W peak is lost; it is an accepted capability trade, not proven zero-loss savings. A second voice radio is explicitly not a cost optimization.

## Первичные источники

- [NiceRF SA868S datasheet rev. 1.7](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
- [NiceRF SA518 product page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html)
- [NiceRF SA518 datasheet rev. 1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
- [ECC/DEC/(15)05 — PMR446](https://docdb.cept.org/download/2783)
- [ETSI EN 303 405 V1.1.1](https://www.etsi.org/deliver/etsi_en/303400_303499/303405/01.01.01_30/en_303405v010101v.pdf)
- [TAPR AX.25 Link Access Protocol v2.2](https://tapr.org/pdf/AX25.2.2.pdf)
- [APRS Protocol Reference 1.0.1](https://www.aprs.org/doc/APRS101.PDF)
