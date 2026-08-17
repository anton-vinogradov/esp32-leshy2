# REQ-N24-0001 — 3×nRF24 raw 2.4 GHz analysis and controlled-test contract

- Статус набора: **Проведено ревью capability; `G2F-3I` leading owner/controller, full-mix policy принят `DEC-0047`, exact module/antenna открыт `IMP-0040`**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-N24-01`–`C-N24-10`, пересечения `C-X-01`, `C-X-02`, `C-X-05`, `C-X-07`, `C-X-08`, `C-X-11`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0010`, `DEC-0013`, `DEC-0018`, `DEC-0019`, `DEC-0021`; nRF24-часть `DEC-0001` переоткрыта
- Находки: `FND-0001`, `FND-0007`, `FND-0019`, `FND-0020`, `FND-0021`, `FND-0028`
- Условные входы реализации: zero-based compute/controller/transport synthesis, exact 3× radio module/AVL, power/antenna/TX detector/STOP, regional profiles, storage/licence и HIL

## Граница документа

Три nRF24 остаются отдельными одновременными полнофункциональными 2.4 GHz GFSK/Enhanced-ShockBurst transceivers, а не SDR, Wi-Fi receiver или BLE controller. Их MCU/controller/bridge placement ничем не предопределён: оно выводится из full-function timing, concurrency, safety, cost и pin/resource model по `DEC-0027`. `RPD` — бинарный detector threshold, pseudo-promiscuous ESB — ограниченная technique, а BLE-compatible advertising — лишь экспериментальный subset и не потолок самого nRF24. Ordinary measurement, passive security discovery, sensitive capture, active exploitation и RF interference никогда не скрываются под одним именем.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-N24-01` | все | `post-wishlist architecture` | Сквозной | Architecture даёт всем 3×nRF24 coherent scheduling, common monotonic time, independent per-radio state/session и bounded command/data path. Все три одновременно активны внутри `SG-N24`; каждый независимо выбирает PTX/PRX, поэтому обязательны `3R`, `1T+2R`, `2T+1R` и `3T` без automatic peer standby или hidden RX gaps. Legacy topology не наследуется. |
| `REQ-N24-02` | `C-N24-01` | `conditional` | Сквозной hardware | Три exact qualified module имеют manufacturer/MPN/revision/IC identity/AVL, одинаковый measured RX/TX profile либо явно раздельную calibration. Generic `PA/LNA` label не задаёт power, sensitivity, current, antenna или compliance (`FND-0019`). |
| `REQ-N24-03` | `C-N24-01` | `conditional` | Сквозной bus | Owner-local SPI имеет независимые logical CS и CE каждого radio, bounded bus arbitration и loss/latency proof. Shared IRQ допустим только при bounded безошибочной идентификации источника чтением каждого STATUS. Reset даёт `CSN=high`, `CE=low`, `PWR_UP=0`; отсутствующий/stuck radio не блокирует остальные. |
| `REQ-N24-04` | `C-N24-02` | `conditional`, accepted A | Основной RX | По `DEC-0019` energy view хранит binary RPD samples, hit ratio, sample count, dwell, channel, data rate, common time window, age, radio/antenna ID и calibration ID/state. После fixture normalization сравниваются только синхронные сектора на одной частоте; UI даёт `stronger/comparable/unknown`, без dBm/RSSI/angle/bearing/VSWR. |
| `REQ-N24-05` | `C-N24-02`, `C-N24-03` | `conditional` | Основной RX | Parallel sweep использует три одновременно принимающих radio после минимум documented settle, показывает actual schedule/coverage/staleness. Wi-Fi/Zigbee/802.15.4 overlays — только frequency maps энергии: protocol attribution или packet decode не выводятся из RPD. |
| `REQ-N24-06` | `C-N24-04` | `conditional` | Лаборатория | Passive ESB discovery разделяет pseudo-promiscuous candidate, address lock/follow и validated frame. UI/record хранит channel/rate/address-width/prefix/CRC method/confidence/errors; arbitrary 2.4 signal не называется ESB packet. Payload по умолчанию redacted. |
| `REQ-N24-07` | `C-N24-05` | `conditional` | Лаборатория | MouseJack/KeyJack passive discovery показывает только fixture-proven vendor/device/advisory match и patch/unknown state; наличие ESB traffic не означает vulnerability. |
| `REQ-N24-08` | `C-N24-05`, `C-N24-07` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Single-target benign vulnerability confirmation, MouseJack/KeyJack injection, ESB replay и fake-device tests требуют fresh banner, exact authorized receiver/dongle identity, preview/hold, bounded packets/time и local STOP. Generic arbitrary script не запускается из discovery/import. |
| `REQ-N24-09` | `C-N24-06` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | HID/keystroke payload capture разрешён только на owned/explicitly authorized fixture, считается sensitive data, не работает background и хранится в encrypted/redacted session vault с explicit export/delete. |
| `REQ-N24-10` | `C-N24-07` | `conditional` | Контролируемая зона, `BOTH` | Address/prefix brute-force/network mapper активно probes только conducted/RF-shielded authorized fixtures. Показываются address space, channel set, packet/time limit и progress; broadcast/unknown target prohibited. |
| `REQ-N24-11` | `C-N24-08` | `conditional` | Смешанный | Ordinary BLE принадлежит selected native BLE controller; former S3 profile из `DEC-0021` не является target. nRF24 BLE-compatible path не называется BLE controller: only proven legacy-1M advertising PDU/channel/payload matrix. Ограничение относится только к этому дополнительному subset; passive compatibility analysis = Lab, чужая identity/security TX = Controlled Zone. |
| `REQ-N24-12` | `C-N24-09` | `conditional` | Контролируемая зона, `BOTH` | Interference-resilience test работает только conducted/RF-shielded, на authorized fixture и при допустимом regulatory basis. Open-air jammer отсутствует; exact channel/power/duty/duration, independent STOP и no-leakage validation обязательны. |
| `REQ-N24-13` | `C-N24-10` | `conditional` | Контролируемая зона, `BOTH` | Constant carrier/sweep beacon — bounded external-instrument test source, не встроенный VSWR meter. Только permitted channel/power, conducted/shielded path, countdown/hold, hard timeout и STOP; `CONT_WAVE+REUSE_TX_PL` запрещён из-за documented CE-low caveat. |
| `REQ-N24-14` | все TX | `conditional` | Сквозной TX safety | Conservative default использует минимальный qualified conducted power exact module. Raw `RF_PWR` bits не маркируются dBm PA/LNA module без measurement. Local real-time owner dead-man, global policy cancellation и independent hardware kill прекращают TX при crash/reset/update/link loss/session exit независимо от выбранного owner. |
| `REQ-N24-15` | все | `conditional` | Сквозной RF coexistence | Один cross-MCU arbiter исключает cross-group TX с native 2.4 Wi-Fi/BLE/802.15.4 и учитывает desense между тремя nRF RX/TX. Внутри `SG-N24` любое одновременное PTX/PRX сочетание обязательно и не time-sliced; `IMP-0039` выбирает exact channel/power/wanted-level envelope, а arbitrary same/near-channel weak-signal sensitivity не объявляется без HIL. |
| `REQ-N24-16` | `C-X-08` | `conditional` | Сквозной storage | Typed ESB/RPD records bounded/fuzzed and versioned; import не вооружает TX. Address/payload/keystroke identifiers имеют consent/provenance/redaction/retention/export/delete policy. |
| `REQ-N24-17` | все | `acceptance` | Сквозной licence | Owner-side driver/parser/attack fixtures имеют per-file SPDX/SBOM/provenance независимо от выбранного compute target. GPL RF24/MouseJack code не копируется в MIT target без явного совместимого решения; clean implementation доказывается tests, не отсутствием attribution. |
| `REQ-N24-18` | все | `acceptance` | Сквозной HIL | Exact three-module fixture проверяет register/reset/clone quirks, SPI isolation, RPD timing/calibration/temp, every simultaneous `3R/1T2R/2T1R/3T` role mix, ESB false positives/CRC/hop, supported vulnerable devices, BLE subset, simultaneous 3T peak/average current, droop/thermal/coupling, rail transients, antenna isolation, emissions, STOP/link loss и conducted/shielded containment. Mixed RX результаты хранят channel separation, TX power, rate, antenna pose и wanted/reference level. |
| `REQ-N24-19` | `C-N24-01` | `acceptance` | Сквозной full-function | Каждый exact radio/driver доказывает PTX и PRX, 250 kbit/s/1 Mbit/s/2 Mbit/s, region-gated RF_CH, Enhanced ShockBurst auto-ACK/retransmit, static/dynamic payload до 32 bytes, ACK payload, dynamic ACK, six RX pipes/address widths, CRC modes, FIFO/IRQ и RPD. Scheduler допускает разные role/channel/rate/address/session для каждого radio одновременно, без принудительного standby соседей. |

## Частоты и измерения

- Silicon `RF_CH` — только 0–125; UI не показывает 128 usable channels.
- RX tuning range не превращается в legal TX range. Каждый TX profile ограничивается exact module, antenna и регионом.
- RPD threshold/hit ratio не конвертируется в dBm по формуле и не сравнивается между radio до calibration.
- Краткий signal короче dwell/scan cycle может быть пропущен; occupancy является статистикой заданного окна, не абсолютной загрузкой эфира.

## Безопасность по умолчанию

- вне `SG-N24`, а также при power/reset/update/link loss: общий nRF rail off,
  все три `CE=low`, controller clocks stopped, FIFOs cleared, no auto-resume;
- внутри `SG-N24` общий rail включён для всех трёх; TX одного не выключает
  остальных, но каждое TX по-прежнему требует собственный arm/lease;
- Main — RX energy measurement без security interpretation;
- Lab — passive header/metadata discovery with payload redaction;
- Controlled Zone entry banner не начинает capture/TX; sensitive capture и каждое active действие имеют отдельный target/action gate;
- interference/continuous carrier/address sweep доступны только в physically contained test setup; разрешение владельца target не заменяет spectrum law.

## Стоимость без потери продукта

Количество 3×nRF24 и полный native feature set приняты и не уменьшаются. По `DEC-0019` hunt использует существующие RPD тракты без нового measurement BOM. Один radio+RF switch теряет одновременный RX; один PA/LNA + два иных receiver меняют sensitivity/calibration/TX symmetry; общий неразделимый CE теряет независимые роли. Это не zero-loss. Экономия ищется в owner placement, exact common AVL, общей land/antenna strategy и direct-CS/decoder/latch trade после pin budget, но не удалением CE safe-state, bulk/decoupling, STOP, RF detector или HIL.

## Первичные источники

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
- [Bastille MouseJack research](https://bastille.net/research/vulnerabilities-mousejack/)
- [Bastille MouseJack tools](https://github.com/BastilleResearch/mousejack)
- [Bastille wireless-peripheral research](https://bastille.net/research/wireless-peripherals/)
- [pyRF24 fake-BLE limitations](https://nrf24.github.io/pyRF24/ble_api.html)
- [FCC jammer enforcement basis](https://docs.fcc.gov/public/attachments/DA-14-1785A1_Rcd.pdf)
- [Ofcom: radio spectrum and the law](https://www.ofcom.org.uk/spectrum/radio-equipment/radio-spectrum-and-the-law)
