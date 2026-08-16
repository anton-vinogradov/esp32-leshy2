# REQ-N24-0001 — 3×nRF24 raw 2.4 GHz analysis and controlled-test contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-N24-01`–`C-N24-10`, пересечения `C-X-01`, `C-X-02`, `C-X-05`, `C-X-07`, `C-X-08`, `C-X-11`
- Обязательные решения: `DEC-0001`, `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0010`, `DEC-0013`, `DEC-0018`, `DEC-0019`
- Находки: `FND-0001`, `FND-0002`, `FND-0007`, `FND-0019`, `FND-0020`, `FND-0021`
- Условные входы реализации: C5 transport/GPIO/SPI budget, exact 3× radio module/AVL, power/antenna/TX detector/STOP, regional profiles, BLE-owner decision, storage/licence и HIL

## Граница документа

Три nRF24 остаются отдельными одновременными 2.4 GHz GFSK/Enhanced-ShockBurst transceivers C5, а не SDR, Wi-Fi receiver или BLE controller. `RPD` — бинарный detector threshold, pseudo-promiscuous ESB — ограниченная technique, а BLE-compatible advertising — экспериментальный subset. Ordinary measurement, passive security discovery, sensitive capture, active exploitation и RF interference никогда не скрываются под одним именем.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-N24-01` | все | `conditional` | Сквозной | ESP32-C5 физически/программно владеет всеми 3×nRF24 по `DEC-0001`; S3 использует typed inter-MCU API. Legacy S3 bus не наследуется, а transport закрывает `FND-0001` и полный post-`DEC-0018` resource budget. |
| `REQ-N24-02` | `C-N24-01` | `conditional` | Сквозной hardware | Три exact qualified module имеют manufacturer/MPN/revision/IC identity/AVL, одинаковый measured RX/TX profile либо явно раздельную calibration. Generic `PA/LNA` label не задаёт power, sensitivity, current, antenna или compliance (`FND-0019`). |
| `REQ-N24-03` | `C-N24-01` | `conditional` | Сквозной bus | C5-local SPI имеет независимый CS каждого radio, bounded bus arbitration и доказанные shared/individual CE+IRQ semantics. Reset даёт `CSN=high`, `CE=low`, `PWR_UP=0`; отсутствующий/stuck radio не блокирует остальные. |
| `REQ-N24-04` | `C-N24-02` | `conditional`, accepted A | Основной RX | По `DEC-0019` energy view хранит binary RPD samples, hit ratio, sample count, dwell, channel, data rate, common time window, age, radio/antenna ID и calibration ID/state. После fixture normalization сравниваются только синхронные сектора на одной частоте; UI даёт `stronger/comparable/unknown`, без dBm/RSSI/angle/bearing/VSWR. |
| `REQ-N24-05` | `C-N24-02`, `C-N24-03` | `conditional` | Основной RX | Parallel sweep использует три одновременно принимающих radio после минимум documented settle, показывает actual schedule/coverage/staleness. Wi-Fi/Zigbee/802.15.4 overlays — только frequency maps энергии: protocol attribution или packet decode не выводятся из RPD. |
| `REQ-N24-06` | `C-N24-04` | `conditional` | Лаборатория | Passive ESB discovery разделяет pseudo-promiscuous candidate, address lock/follow и validated frame. UI/record хранит channel/rate/address-width/prefix/CRC method/confidence/errors; arbitrary 2.4 signal не называется ESB packet. Payload по умолчанию redacted. |
| `REQ-N24-07` | `C-N24-05` | `conditional` | Лаборатория | MouseJack/KeyJack passive discovery показывает только fixture-proven vendor/device/advisory match и patch/unknown state; наличие ESB traffic не означает vulnerability. |
| `REQ-N24-08` | `C-N24-05`, `C-N24-07` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Single-target benign vulnerability confirmation, MouseJack/KeyJack injection, ESB replay и fake-device tests требуют fresh banner, exact authorized receiver/dongle identity, preview/hold, bounded packets/time и local STOP. Generic arbitrary script не запускается из discovery/import. |
| `REQ-N24-09` | `C-N24-06` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | HID/keystroke payload capture разрешён только на owned/explicitly authorized fixture, считается sensitive data, не работает background и хранится в encrypted/redacted session vault с explicit export/delete. |
| `REQ-N24-10` | `C-N24-07` | `conditional` | Контролируемая зона, `BOTH` | Address/prefix brute-force/network mapper активно probes только conducted/RF-shielded authorized fixtures. Показываются address space, channel set, packet/time limit и progress; broadcast/unknown target prohibited. |
| `REQ-N24-11` | `C-N24-08` | `conditional` | Смешанный | nRF24 BLE-compatible path не называется BLE controller: only proven legacy-1M advertising PDU/channel/payload matrix. Ordinary BLE идёт через будущий native BLE contract (`IMP-0017`); passive compatibility analysis = Lab, чужая identity/security TX = Controlled Zone. |
| `REQ-N24-12` | `C-N24-09` | `conditional` | Контролируемая зона, `BOTH` | Interference-resilience test работает только conducted/RF-shielded, на authorized fixture и при допустимом regulatory basis. Open-air jammer отсутствует; exact channel/power/duty/duration, independent STOP и no-leakage validation обязательны. |
| `REQ-N24-13` | `C-N24-10` | `conditional` | Контролируемая зона, `BOTH` | Constant carrier/sweep beacon — bounded external-instrument test source, не встроенный VSWR meter. Только permitted channel/power, conducted/shielded path, countdown/hold, hard timeout и STOP; `CONT_WAVE+REUSE_TX_PL` запрещён из-за documented CE-low caveat. |
| `REQ-N24-14` | все TX | `conditional` | Сквозной TX safety | Conservative default использует минимальный qualified conducted power exact module. Raw `RF_PWR` bits не маркируются dBm PA/LNA module без measurement. C5 local dead-man, S3 STOP и independent hardware kill прекращают TX при crash/reset/update/link loss/session exit. |
| `REQ-N24-15` | все | `conditional` | Сквозной RF coexistence | Один cross-MCU arbiter исключает небезопасный simultaneous TX с native 2.4 Wi-Fi/BLE/802.15.4 и учитывает desense между тремя nRF RX/TX. Parallel TX разрешается только отдельному shielded/conducted HIL profile. |
| `REQ-N24-16` | `C-X-08` | `conditional` | Сквозной storage | Typed ESB/RPD records bounded/fuzzed and versioned; import не вооружает TX. Address/payload/keystroke identifiers имеют consent/provenance/redaction/retention/export/delete policy. |
| `REQ-N24-17` | все | `acceptance` | Сквозной licence | C5 driver/parser/attack fixtures имеют per-file SPDX/SBOM/provenance. GPL RF24/MouseJack code не копируется в MIT target без явного совместимого решения; clean implementation доказывается tests, не отсутствием attribution. |
| `REQ-N24-18` | все | `acceptance` | Сквозной HIL | Exact three-module fixture проверяет register/reset/clone quirks, SPI isolation, RPD timing/calibration/temp, parallel scheduling, ESB false positives/CRC/hop, supported vulnerable devices, BLE subset, rail transients, antenna isolation, emissions, STOP/link loss и conducted/shielded containment. |

## Частоты и измерения

- Silicon `RF_CH` — только 0–125; UI не показывает 128 usable channels.
- RX tuning range не превращается в legal TX range. Каждый TX profile ограничивается exact module, antenna и регионом.
- RPD threshold/hit ratio не конвертируется в dBm по формуле и не сравнивается между radio до calibration.
- Краткий signal короче dwell/scan cycle может быть пропущен; occupancy является статистикой заданного окна, не абсолютной загрузкой эфира.

## Безопасность по умолчанию

- power/reset/update/link loss: все три radio `CE=low`, powered-down, FIFOs cleared, no auto-resume;
- Main — RX energy measurement без security interpretation;
- Lab — passive header/metadata discovery with payload redaction;
- Controlled Zone entry banner не начинает capture/TX; sensitive capture и каждое active действие имеют отдельный target/action gate;
- interference/continuous carrier/address sweep доступны только в physically contained test setup; разрешение владельца target не заменяет spectrum law.

## Стоимость без потери продукта

Количество 3×nRF24 принято и не уменьшается. По `DEC-0019` hunt использует существующие RPD тракты без нового measurement BOM. Один radio+RF switch теряет одновременный RX; один PA/LNA + два иных receiver меняют sensitivity/calibration/TX symmetry и не считаются zero-loss. Экономия ищется в exact common AVL, общей land/antenna strategy и direct-CS/decoder trade после pin budget, но не удалением CE safe-state, bulk/decoupling, STOP, RF detector или HIL.

## Первичные источники

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
- [Bastille MouseJack research](https://bastille.net/research/vulnerabilities-mousejack/)
- [Bastille MouseJack tools](https://github.com/BastilleResearch/mousejack)
- [Bastille wireless-peripheral research](https://bastille.net/research/wireless-peripherals/)
- [pyRF24 fake-BLE limitations](https://nrf24.github.io/pyRF24/ble_api.html)
- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [FCC jammer enforcement basis](https://docs.fcc.gov/public/attachments/DA-14-1785A1_Rcd.pdf)
- [Ofcom: radio spectrum and the law](https://www.ofcom.org.uk/spectrum/radio-equipment/radio-spectrum-and-the-law)
