# INV-0001 — дедуплицированная инвентаризация legacy-возможностей

- Статус подшага: **Проведено ревью** (`REV-0002A`)
- Этап: 2 — возможности и исключения
- Смысл статуса: полнота переноса проверена; кандидаты **не приняты** как требования
- Дата: 2026-08-15

## Источники и метод

| Код | Источник | Роль |
|---|---|---|
| `FW-CAP` | firmware `drafts/legacy-2026-08-15/docs/capability-tree.ru.md` | основной полный список leaf-кандидатов и потолков |
| `FW-UI` | firmware `drafts/legacy-2026-08-15/docs/firmware-tree.ru.md` | независимая группировка по приложениям и составные пользовательские сессии |
| `HW-SCOPE` | hardware `drafts/legacy-2026-08-15/root/README.ru.md`, этапы 1–2 | аппаратные обещания и независимое подтверждение крупных функций |
| `HW-ROAD` | hardware `drafts/legacy-2026-08-15/docs/roadmap.ru.md` | дополнительные software-кандидаты и потолки |

Русская и английская версии `FW-CAP` содержат одинаково по 139 строк таблиц: 12 заголовков, 118 потенциальных кандидатов и 9 строк `⛔`. Каждая из 118 строк получила ровно один `C-*` ниже. Повторы из `FW-UI` и `HW-SCOPE` не размножались; добавлены только 3 составные UX-сессии и 4 отдельные оптимизации `HW-ROAD`.

## Обозначения зоны

По `DEC-0010` зоны отображаются на три пользовательских уровня: основной режим → «Лаборатория» → вложенная «Контролируемая зона». Install-time акт, banner третьего уровня и per-tool arming — независимые гейты.

- `MAIN` — обычная полевая функция, не позиционируемая как security-research;
- `LAB-P` — уровень 2: пассивное/защитное security-исследование в обычной «Лаборатории»;
- `LAB-I` — уровень 3 по умолчанию: интерактивное воздействие, инъекция или имперсонация в «Контролируемой зоне»;
- `LAB-D` — уровень 3: disruptive/DoS/jam и наиболее серьёзное воздействие; для излучения помех разрешение цели не заменяет изоляцию и spectrum rules;
- `SYS` — инфраструктура и safety;
- `MIXED` — legacy-строка объединяет функции разных зон и должна быть разложена до появления `REQ-*`.

Зона предварительна, но уже подчиняется `DEC-0002`: security-функция не может оказаться в main только потому, что она пассивна.

## 2.4 ГГц Wi-Fi — `FW-CAP §1`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-W24-01 | Скан AP, станций и клиентов | LAB-P | dual-use; назначение нужно сформулировать |
| C-W24-02 | Снифф beacon/probe и promiscuous PCAP | LAB-P | одноканально, payload шифрован |
| C-W24-03 | Пакетрейт и загруженность канала | MAIN | радиодиагностика |
| C-W24-04 | Детектор deauth-атаки | LAB-P | защитный security-инструмент |
| C-W24-05 | Deauth/disassoc точечный и broadcast | LAB-D | PMF ограничивает результат |
| C-W24-06 | Beacon/probe/auth/assoc management-флуды | LAB-D | DoS/spectrum impact |
| C-W24-07 | Evil Portal | LAB-I | credential/phishing risk |
| C-W24-08 | Evil Twin, rogue/honeypot AP, Karma | LAB-I | имперсонация/DoS |
| C-W24-09 | MAC spoof/randomization и STA-подключение | MIXED | разложить privacy и connection |
| C-W24-10 | Примитив raw-инъекции 802.11 | LAB-I | enabling API, каждый caller гейтован |
| C-W24-11 | ESP-NOW link, sniff и spoof | MIXED | link = main, sniff/spoof = Lab |
| C-W24-12 | Web UI и OTA через SoftAP | SYS | интерфейс/обновление |

## 2.4 ГГц raw / nRF24 — `FW-CAP §2`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-N24-01 | Драйвер регистров/SPI nRF24 | SYS | C5 target; transport `FND-0001`, current artifact `FND-0019`, clean ESP-IDF/licence proof |
| C-N24-02 | Параллельный RPD energy sweep, waterfall, occupancy | MAIN | `DEC-0019`: calibrated binary hit ratio по трём секторам; не RSSI/dBm/bearing |
| C-N24-03 | Оверлей энергии Wi-Fi/Zigbee/802.15.4 | MAIN | только frequency/energy overlay без protocol attribution |
| C-N24-04 | ESB sniff и поиск адресов | LAB-P | pseudo-promiscuous candidate → CRC/confidence-validated record, payload redacted |
| C-N24-05 | MouseJack scan и инъекция | MIXED | passive advisory discovery = Lab; confirmation/injection = Controlled Zone `AUTHORIZED_TARGET` |
| C-N24-06 | KeySniffer незашифрованных нажатий | LAB-I | sensitive capture = Controlled Zone `AUTHORIZED_TARGET`, vault/redaction/retention |
| C-N24-07 | ESB replay, fake device, address brute-force | LAB-I | single target = `AUTHORIZED_TARGET`; mapper/brute-force = `BOTH` |
| C-N24-08 | BLE advertising sniff/spoof через nRF24 | MIXED | limited legacy-1M compatibility only; ordinary BLE → native boundary `IMP-0017`/`IMP-0019` |
| C-N24-09 | Одноканальный и reactive jam | LAB-D | Controlled Zone `BOTH`, conducted/RF-shielded only; open-air mode excluded |
| C-N24-10 | Sweep beacon, carrier test, VSWR aid, 3-антенный hunt | MIXED | `DEC-0019`: calibrated RPD sector hunt; carrier = external-instrument source only, no VSWR |

## 5 ГГц Wi-Fi и 802.15.4 — `FW-CAP §3`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-W5-01 | AP scan, channel view и RSSI | MIXED | ordinary diagnostics = Main; privacy/security survey = Lab; active только non-DFS, DFS passive |
| C-W5-02 | Promiscuous management/control/data capture | LAB-P | public RX существует, но не обещает lossless/full-monitor; EAPOL/PMKID conditional `IMP-0003` |
| C-W5-03 | Клиенты, beacon inventory, hidden SSID | LAB-P | observed/inferred/unknown; passive DFS может не раскрыть hidden SSID |
| C-W5-04 | Детект deauth и rogue/evil-twin | LAB-P | защитный evidence/confidence-инструмент, PMF state обязателен |
| C-W5-05 | Deauth/disassoc | LAB-I | `defer`: public API не поддерживает; private version-locked patch требует отдельного решения/provenance/HIL; PMF |
| C-W5-06 | Beacon/probe spam | LAB-D | Controlled Zone `BOTH`, conducted/RF-shielded; public frame classes bounded |
| C-W5-07 | Evil Twin SoftAP, Evil Portal, Karma | LAB-I | Controlled Zone `AUTHORIZED_TARGET`, non-DFS, privacy/credential vault |
| C-W5-08 | STA-подключение | MAIN | только собственные/администрируемые сети, region/credential gates |
| C-W5-09 | 802.15.4 raw RX/TX, Zigbee и Thread | MIXED | `DEC-0020`: OpenThread open baseline, Zigbee optional conditional adapter; passive = Lab, active tests = Controlled Zone |

## BLE — `FW-CAP §4`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-BLE-01 | Advertising scan, ext-adv и Coded PHY | MAIN | native ESP поддерживает; owner требует `IMP-0019` |
| C-BLE-02 | Offline device DB, OUI/company ID, RSSI proximity | MAIN | versioned/licensed DB; RPA и RSSI не дают stable identity, метры или направление |
| C-BLE-03 | Детект AirTag/Find My и stalking trackers | MAIN | personal-safety detector conditional on signatures+temporal evidence; не доказывает owner/intent/absence |
| C-BLE-04 | Continuity/Flipper/device-type sniff | LAB-P | passive corpus требует provenance/licence/version и confidence |
| C-BLE-05 | Wardriving, geo-log и adv PCAP | LAB-P | foreground privacy vault, retention/export/delete и external-GNSS provenance |
| C-BLE-06 | GATT service/characteristic enumeration | MIXED | ordinary paired service = Main; security enumeration = Controlled Zone `AUTHORIZED_TARGET` |
| C-BLE-07 | HID host и BadBLE injection | MIXED | paired input = Main; scripted injection = Controlled Zone `AUTHORIZED_TARGET` |
| C-BLE-08 | iBeacon/Eddystone/custom advertising | MIXED | own/open beacon = Main; identity imitation = Controlled Zone `AUTHORIZED_TARGET`; rights gate |
| C-BLE-09 | Proximity-pairing spam | LAB-D | Controlled Zone `BOTH`, conducted/RF-shielded only |
| C-BLE-10 | Sour Apple crash spam | LAB-D | Controlled Zone `BOTH`, conducted/RF-shielded only |
| C-BLE-11 | Find My/AirTag beacon emulation | LAB-I | Controlled Zone `BOTH`; protocol/rights/corpus proof and no third-party-network participation |
| C-BLE-12 | BLE connection flood / GATT DoS | LAB-D | Controlled Zone `BOTH`, conducted/RF-shielded only |

## Sub-GHz / CC1101 — `FW-CAP §5`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-SUB-01 | RSSI frequency hunter и frequency counter | MAIN | только полосы PLL |
| C-SUB-02 | Sequential RSSI spectrum/waterfall | MAIN | не realtime/IQ |
| C-SUB-03 | RAW OOK capture и auto-record по squelch | MAIN | RX |
| C-SUB-04 | Multiband hopper scan/log | MAIN | короткие сигналы могут теряться |
| C-SUB-05 | Static-code/rtl_433 decode и rolling-code recognition | MIXED | RX; security intent разложить |
| C-SUB-06 | RAW replay и protocol emulation | MIXED | своё использование vs Lab |
| C-SUB-07 | Fixed-code/de Bruijn brute-force | LAB-D | активная атака |
| C-SUB-08 | Signal library, tags и playlist replay | MIXED | storage vs active replay |
| C-SUB-09 | Arbitrary CC1101 config и CW test tone | MIXED | config = SYS, TX test = Lab |
| C-SUB-10 | SP4T filter control | SYS | инфраструктура RF path |
| C-SUB-11 | Одноканальный/reactive jam | LAB-D | narrow target, duty и STOP |

## LoRa/SX1262 и GPS — `FW-CAP §6`

Аппаратный scope уточнён `DEC-0006` и `DEC-0008`: бортовых LoRa и GNSS нет; U214 — первый LoRa+GNSS-модуль `EXT-RF14`, другие LoRa carrier опциональны. GNSS доступен через отдельный M5 Unit GPS v1.1 либо встроенный AT6668 U214. Одновременно активен один LoRa backend и один GNSS backend. `REQ-GNSS-0001` прошёл ревью: `DEC-0014` заменяет ошибочную legacy-привязку к u-blox обязательным NMEA baseline и условным advanced CASIC profile.

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-LORA-01 | LoRa P2P TX/RX | MAIN | обычная связь |
| C-LORA-02 | Meshtastic-compatible mesh | MAIN | большой объём, late release |
| C-LORA-03 | LoRa APRS beacon/RX/iGate/digipeater | MAIN | callsign/licence gates |
| C-LORA-04 | LoRaWAN Class A/C node | MAIN | band plan и свои ключи |
| C-LORA-05 | Passive spectrum scan и promiscuous log | LAB-P | закрытые payload не декодировать |
| C-LORA-06 | Link/range test RSSI/SNR | MAIN | TX limits |
| C-LORA-07 | (G)FSK, RTTY, CW и AX.25 beacon | MAIN | licence/band limits |
| C-LORA-08 | LoRa OTA и file transfer | MAIN | duty/скорость |
| C-LORA-09 | Одноцелевой carrier/reactive jam | LAB-D | narrow target, duty и STOP |
| C-GPS-01 | Position/navigation, module config, time sync | MAIN | внешний M5Stack Unit GPS v1.1 или GNSS U214; NMEA baseline, профильные команды только после proof |
| C-GPS-02 | Track log, waypoints и geofences | MAIN | privacy, fix-quality и storage-recovery gates в `REQ-GNSS-0001` |
| C-GPS-03 | AssistNow offline assistance | SYS | торговое имя u-blox неприменимо; `DEC-0014` принимает backend-native assistance без обязательного Интернета |
| C-GPS-04 | GNSS jamming/spoofing indicator | MAIN | защитный readout; CASIC status возможен, но conditional per-profile proof и никогда не false-safe |

## Si4732 Radio RX — `FW-CAP §7`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-RX-01 | FM broadcast и RDS | MAIN | RX-only |
| C-RX-02 | AM LW/MW/SW | MAIN | RX-only |
| C-RX-03 | SSB/CW и заявленная synchronous AM | MAIN | `DEC-0015`: SSB/CW conditional через открытый owner-imported loader; synchronous AM `defer` до отдельного proof |
| C-RX-04 | Tuning/DSP/AGC/BFO/presets/band plans | MAIN | — |
| C-RX-05 | Bandscope и sweep-RSSI spectrum | MAIN | не FFT |
| C-RX-06 | Scanner log на SD | MAIN | — |
| C-RX-07 | WAV recording и CW/RTTY/SSTV/WEFAX decode | MAIN | `conditional`: `DEC-0009`; electrical/firmware proof ожидается |

## SA868 UHF radio — `FW-CAP §8`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-VHF-01 | NFM voice RX/TX | MAIN | `FND-0011`: PTT/PD/H-L safe defaults исправлены; licence profile, independent STOP и RF power HIL ожидаются |
| C-VHF-02 | CTCSS/DCS/squelch/channel/band/volume | MAIN | точный набор условен backend API/readback; tone не является privacy |
| C-VHF-03 | Channel/tone scan и carrier/RSSI detect | MAIN | UART даёт binary carrier/raw RSSI; tone scan conditional через ES8311 host decode (`FND-0012`) |
| C-VHF-04 | Parrot, roger beep, VOX, 1750 tone, DTMF encode | MIXED | parrot = Lab; audio TX conditional `DEC-0009`; VOX `defer` без mic capture (`FND-0013`) |
| C-VHF-05 | DTMF decode | MAIN | `conditional`: `DEC-0009`; electrical/decoder proof |
| C-VHF-06 | APRS/AFSK, AX.25 KISS, SSTV TX, fox-hunt beacon | MAIN | `conditional`: `DEC-0016` предпочитает SA518 dual-band, SA868 UHF fallback; licence/TX/modem proof |
| C-VHF-07 | Cross-band audio relay и UHF WAV recording | MIXED | `conditional`: `DEC-0009`; relay только Lab/default-off + authorized content/legal/HIL proof |

## NFC/RFID optional unit — `FW-CAP §9`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-NFC-01 | ISO14443A detect, UID/ATQA/SAK/fingerprint | MAIN | `conditional`: `DEC-0017` U216 first target; current port power fails `FND-0015` |
| C-NFC-02 | MIFARE dictionary, dump и write/restore | MIXED | known-key owner read separate from Controlled-Zone recovery/credential write |
| C-NFC-03 | MIFARE nested attack | LAB-I | Controlled Zone/authorized card; runtime/provenance/corpus proof, hardnested separate |
| C-NFC-04 | Magic-card detect и wipe/format | MIXED | read-only detect in Lab; destructive write in Controlled Zone |
| C-NFC-05 | Ultralight/NTAG read/write/PWD_AUTH | MIXED | ordinary tag read/write vs credential/config/lock write |
| C-NFC-06 | NDEF parse/build/write | MIXED | ordinary NDEF Main with preview; credential/irreversible regions gated |
| C-NFC-07 | UID clone to magic card | LAB-I | Controlled Zone `AUTHORIZED_TARGET`; clone is not identity/auth proof |
| C-NFC-08 | Amiibo NTAG215 read/identify | MAIN | read only; no proprietary keys/authenticity claim |
| C-NFC-09 | ISO14443-4/DESFire APDU и EMV contactless read | MIXED | privacy-gated diagnostic; no payment/compliance claim |
| C-NFC-10 | Card library на SD | SYS | typed sensitive vault/export/redaction/factory-reset contract |

## IR — `FW-CAP §10`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-IR-01 | IR receive, protocol decode и raw capture | MIXED | `DEC-0018`: TSOP38238 robust envelope + TSMP95000 measured carrier 30–60 kHz; Main own receive, passive third-party analysis = Lab |
| C-IR-02 | IR command TX, raw replay и carrier select | MIXED | `DEC-0018`: provenance-aware carrier; own-tagged replay Main; unknown/security replay Controlled Zone; `FND-0001`, `FND-0017` |
| C-IR-03 | TV-B-Gone universal power-off | LAB-D | Controlled Zone `BOTH`: nuisance/mass action, isolated authorized targets |
| C-IR-04 | Universal remote for appliances | MAIN | corpus-proven protocols/models only; stateful HVAC and code-DB licence gates |
| C-IR-05 | IR code brute-force, import/export и SD library | MIXED | brute-force/sweep = Controlled Zone `BOTH`; bounded import/export/storage = Main |

## System/UI/storage — `FW-CAP §11`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-SYS-01 | Launcher, GUI, status bar, themes/settings | SYS | — |
| C-SYS-02 | Touch, encoder/buttons и on-screen keyboard | SYS | `conditional`: UI matrix пересекается с audio/STOP, `FND-0006`/`IMP-0010` |
| C-SYS-03 | BadUSB/DuckyScript HID injection | LAB-I | native S3 USB, authorized host |
| C-SYS-04 | USB serial CLI и SD mass storage | SYS | — |
| C-SYS-05 | OTA S3 over Wi-Fi/SD и OTA C5 через link | SYS | C5 path зависит от `FND-0001` |
| C-SYS-06 | SD file manager, config import/export, offline DB | SYS | — |
| C-SYS-07 | Battery status, sleep и peripheral/C5 power gating | SYS | — |
| C-SYS-08 | WS2812 status LED и buzzer | SYS | — |
| C-SYS-09 | Grove/M5 enumeration, hot-plug и unit drivers | SYS | only 3.3 V I2C units |
| C-SYS-10 | Analog audio mux/amp/jack control | SYS | legacy path сам не даёт MCU digital audio; расширение `conditional` по `DEC-0009` |
| C-SYS-11 | Self-test, crash/core dump, factory reset, RTOS tasks | SYS | — |

Декомпозиция этой группы в пользовательские и safety-требования подготовлена в `REQ-SYS-0001`. Legacy transport/pin/hot-plug/USB assumptions не перенесены автоматически; расхождения перечислены в `FND-0008`.

## Cross-cutting — `FW-CAP Cross-cutting`

| ID | Группа кандидатов | Зона | Первичная пометка |
|---|---|---|---|
| C-X-01 | STOP, long-BACK, TX-live, shutdown и reset safe-state | SYS | обязательный safety слой; hardware STOP не реализован, `FND-0007` |
| C-X-02 | Agreement/authorization и TX settings | SYS | legacy max-default заменён `DEC-0003` |
| C-X-03 | TDD RF coexistence arbitration | SYS | гипотеза требует RF/architecture review |
| C-X-04 | S3↔C5 command/telemetry IPC | SYS | `BLOCKED`, `FND-0001` |
| C-X-05 | Cross-band target tracking и combined spectrum | MIXED | passive views vs active callers |
| C-X-06 | GPS-tagged capture, Wardrive и PCAP logging | MIXED | privacy gate |
| C-X-07 | RTC from GPS/NTP | SYS | — |
| C-X-08 | Capture/replay storage for Sub-GHz/IR/ESB | MIXED | storage vs Lab replay |
| C-X-09 | BLE keyboard input from phone | SYS | native owner pending `IMP-0019`; explicit pairing/allowlist/local fallback |
| C-X-10 | Drone Remote-ID detection | MAIN | passive public broadcasts |
| C-X-11 | Detection alerts by LED/buzzer/GPS | SYS | — |

## Дополнительные недублирующиеся кандидаты

| ID | Группа кандидатов | Источник | Зона | Первичная пометка |
|---|---|---|---|---|
| C-UX-01 | One-shot Wardrive: Wi-Fi+BLE+Sub-GHz+GPS в общий лог | FW-UI | MIXED | составная privacy/security session |
| C-UX-02 | Единый DuckyScript для BadBLE и BadUSB | FW-UI | LAB-I | общий parser/tool UX |
| C-UX-03 | Quick replay собственного tagged-сигнала | FW-UI | MIXED | граница main/Lab требует декомпозиции |
| C-HWX-01 | Auto-dim backlight | HW-ROAD | SYS | power optimization |
| C-HWX-02 | SX1262 Rx Boosted Gain | HW-ROAD | MAIN | заявленные +15–30% предстоит доказать |
| C-HWX-03 | Dirty-rectangle display rendering | HW-ROAD | SYS | performance optimization |
| C-HWX-04 | SPI DMA/double buffer/bus arbiter и SD watchdog | HW-ROAD | SYS | legacy 11–21% contention не считается доказанным |

## Дедуплицированные legacy-потолки

По `DEC-0004` ни одна строка ниже не является окончательным исключением. Обязательная повторная проверка ведётся в `AUD-0001`.

| ID | Исключённая группа | Основание legacy | Состояние новой проверки |
|---|---|---|---|
| OUT-01 | WPA PMKID/EAPOL capture и полный 5 ГГц monitor+inject | ESP32/SDK ceiling | кандидат на повторную техническую проверку, не обещание |
| OUT-02 | Wideband/full-band jamming на любом диапазоне | legal/ethos и отсутствие wideband hardware | остаётся вне scope; узкополосные Lab-кандидаты проверяются отдельно |
| OUT-03 | Bluetooth Classic, BLE connection-follow sniff и BLE jam | S3/C5 LE-only; native controller не обещает connection follow; jam требует отдельного shielded source | Classic = `exclude-proven` для текущих radio; connection sniff = `IMP-0004`; jam = `BOTH` и не baseline |
| OUT-04 | nRF24 как 802.11 или полноценный BLE receiver | PHY ceiling | оставить вне scope, если datasheet подтверждает |
| OUT-05 | HF TX, VHF airband/weather, 30–64 MHz и DRM через Si4732 | tuner/DSP ceiling | оставить вне scope, если компонент сохраняется |
| OUT-06 | NFC card emulation/relay, ISO15693, FeliCa, LF 125 kHz, hardnested/darkside | WS1850S ceiling | `DEC-0017` selects U216 for F/V/emulation/custom mode; relay needs two frontend, LF separate, recovery needs compute/license proof |
| OUT-07 | SA868 full-duplex repeater и digital voice | half-duplex analog module ceiling | оставить вне scope, если компонент сохраняется |
| OUT-08 | HackRF-class wideband SDR, arbitrary RF TX и onboard Linux analytics | иной класс hardware/compute | отдельное расширение, не базовый scope |
| OUT-09 | Cellular/GSM | модем отсутствует | вне базового scope |

## Что этот артефакт не решает

- `C-*` — кандидаты, не `REQ-*` и не обещания продукта.
- Legacy reuse/license/gate заметки сохранены в источнике, но будут перепроверены по актуальным первичным источникам.
- `MAIN`/`LAB-*` — первичная сортировка; строки `MIXED` обязательно декомпозируются.
- Ни один legacy ceiling не наследуется без повторной проверки по `DEC-0004`; реалистичный обход оформляется как `IMP-*`.
