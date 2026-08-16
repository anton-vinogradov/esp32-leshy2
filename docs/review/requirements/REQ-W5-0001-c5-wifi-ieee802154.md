# REQ-W5-0001 — C5 dual-band Wi-Fi and IEEE 802.15.4 contract

- Статус набора: **На ревью — требуется решение `IMP-0018`**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-W5-01`–`C-W5-09`, пересечения `C-X-01`, `C-X-02`, `C-X-03`, `C-X-04`, `C-X-06`, `C-X-07`, `C-X-11`, `OUT-01`
- Обязательные решения: `DEC-0001`, `DEC-0002`, `DEC-0003`, `DEC-0004`, `DEC-0005`, `DEC-0010`, `DEC-0013`
- Находки: `FND-0001`, `FND-0002`, `FND-0007`, `FND-0022`–`FND-0025`
- Открытые решения: `IMP-0003`, `IMP-0018`; arbitrary management/deauth patch backend не принят

## Граница документа

ESP32-C5 — 1T1R dual-band Wi-Fi и shared 2.4 GHz BLE/IEEE 802.15.4 radio, а не simultaneous multi-radio monitor/inject platform. Этот контракт разделяет ordinary connectivity, passive observation, defensive detection, sensitive capture и active/disruptive testing. Public ESP-IDF baseline не подменяется undocumented binary patch; DFS/country/PMF/privacy/coexistence являются функциональными пререквизитами, а не сносками.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-W5-01` | все | `conditional` | Сквозной hardware | Exact C5 module/antenna/power artifact квалифицирован по `FND-0022`. Current candidate — standard `ESP32-C5-WROOM-1U-N8R8`/`C51950748`; штатная внешняя антенна идёт через module `ANT1`, а disabled `ANT2` не используется. Supplier candidate не является final BOM. |
| `REQ-W5-02` | все | `conditional` | Сквозной ownership | C5 владеет своими Wi-Fi/802.15.4 controllers, S3 вызывает typed bounded API. Transport закрывает `FND-0001`; reset/update/link loss не оставляют autonomous TX, а события двух MCU имеют синхронизируемые timestamps/age/owner. |
| `REQ-W5-03` | `C-W5-01`, `C-W5-08` | `conditional` | Основной | Ordinary STA connect, saved owner networks, AP scan и channel/security/RSSI view работают на 2.4 или 5 GHz. `AUTO` означает выбор band, не simultaneous receive; UI показывает actual band/channel/time/scan schedule и stale/unknown. |
| `REQ-W5-04` | `C-W5-01`, `C-W5-07`, `C-W5-08` | `conditional` | Сквозной regulatory | Каждая session фиксирует country/region source/revision/effective channel mask. Active scan/TX разрешены только профилем; DFS passive scan/connect отделены от TX, а C5 SoftAP на DFS запрещён. Hidden SSID на passive channel может оставаться `unknown/not observed`, не `absent`. |
| `REQ-W5-05` | `C-W5-02`, `C-W5-03` | `conditional` | Лаборатория | Public promiscuous RX даёт bounded capture management/control/data с band/channel/timestamp/FCS/error/filter/loss counters и measured packet classes. BSSID/client/payload по умолчанию минимизированы/redacted; background capture выключен. Не обещаются lossless monitor, radiotap fidelity или decryption. |
| `REQ-W5-06` | `C-W5-03` | `conditional` | Лаборатория | Beacon/probe/client inventory различает directly observed frame, inferred relation и unknown. Hidden SSID/client association не выводятся из отсутствия пакета; channel-hop coverage, dwell, age и packet loss доступны в UI/export. |
| `REQ-W5-07` | `C-W5-04` | `conditional` | Лаборатория | Defensive deauth/rogue/evil-twin detector использует explainable bounded rules и показывает PMF/security/evidence/confidence/unknown. Одно совпадение SSID или deauth frame не доказывает атаку; alerts сохраняют redacted evidence. |
| `REQ-W5-08` | `OUT-01` | `conditional`, `IMP-0003` | Лаборатория, `AUTHORIZED_TARGET` | Passive EAPOL/PMKID capture включается только после on-target 2.4/5 GHz fixture proof completeness/loss/PCAP validation. Это не on-device cracking/decryption; records — sensitive vault data с explicit export/delete/retention. |
| `REQ-W5-09` | `C-W5-06` | `conditional` | Контролируемая зона | Public raw TX ограничен документированными beacon/probe request/probe response/action и non-QoS data classes. Каждый caller имеет exact frame schema, rate/count/duration/power/channel preview, target policy, dead-man и STOP; unsupported frame нельзя вооружить raw bytes/import. |
| `REQ-W5-10` | `C-W5-05` | `defer` | Контролируемая зона, `AUTHORIZED_TARGET` | Deauth/disassoc/arbitrary management TX не входят в public baseline. Private patched-library backend возможен только после отдельного owner decision и exact IDF/provenance/redistribution/SBOM/hash/signature/rollback/HIL contract; PMF state/result показываются честно. |
| `REQ-W5-11` | `C-W5-06` | `conditional` | Контролируемая зона, `BOTH` | Broadcast beacon/probe flood и resilience load допускаются только conducted/RF-shielded на authorized fixture с no-leakage check, minimum qualified power, packet/time ceiling, countdown, hold-to-run, hardware STOP и audit record. Open-air nuisance mode отсутствует. |
| `REQ-W5-12` | `C-W5-07` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Evil Twin/Portal/Karma-like authentication/portal tests используют exact owned/authorized SSID/BSSID/client fixture, non-DFS SoftAP, fresh banner и explicit content preview. Credentials/identifiers считаются sensitive; third-party branding/captive impersonation и uncontrolled nearby-client attraction запрещены. |
| `REQ-W5-13` | `C-W5-09` | `conditional` | Лаборатория | Raw IEEE 802.15.4 passive mode предоставляет channel/ED/CCA/promiscuous frames с FCS/LQI/RSSI только если exact API действительно их выдаёт, timestamps/loss/coverage и redacted PCAP. Energy не означает Zigbee/Thread attribution. |
| `REQ-W5-14` | `C-W5-09` | `requires IMP-0018` | Основной | Ordinary Thread/Zigbee commissioning/join/control/diagnostics scope, roles и dependency boundary выбираются `IMP-0018`. Ни passive raw, ни Thread baseline не зависят от proprietary Zigbee binary. |
| `REQ-W5-15` | `C-W5-09` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Raw 802.15.4 injection/replay/commissioning-security tests targeting one fixture требуют exact PAN/channel/address identity, preview, bounded frame/count/time, conservative power, dead-man и STOP. Import/capture не вооружает TX автоматически. |
| `REQ-W5-16` | `C-W5-09` | `conditional` | Контролируемая зона, `BOTH` | 802.15.4 flood/interference/resilience test только conducted/RF-shielded с authorized endpoints, no-leakage validation, hard timeout и independent STOP. Open-air jammer отсутствует. |
| `REQ-W5-17` | все 2.4 | `conditional` | Сквозной coexistence | C5 Wi-Fi 2.4/BLE/802.15.4 делят один RF path; scheduler не обещает одновременность и публикует active owner/preemption/loss. Cross-MCU arbiter учитывает 3×nRF24 и S3 2.4 radio; unsafe simultaneous TX prohibited до RF HIL. |
| `REQ-W5-18` | все | `conditional` | Сквозной openness/update | Public-IDF/OpenThread core build воспроизводим и owner-controlled. Любой optional proprietary/patched binary изолирован build profile, имеет provenance/rights/SBOM/version/hash/signature/rollback и не блокирует сборку, обновление или восстановление открытого core product. |
| `REQ-W5-19` | все | `conditional` | Сквозной privacy/storage | Capture/session format versioned, bounded и fuzzed; identity/payload/location minimized, encrypted at rest where sensitive, explicit export/delete/retention/factory-reset tested. Imported records inert by default and cannot bypass zone/region/TX gates. |
| `REQ-W5-20` | все TX | `conditional` | Сквозной safety/HIL | Conservative minimum power default, visible actual band/channel/power/region/target/time, fresh Controlled-Zone banner, local dead-man and independent STOP. Exact module/antenna matrix tests country/DFS/PMF/public frame classes/capture loss/coexistence/reset/crash/update/link loss; no result is promoted from `unknown`. |

## Явно не обещается

- simultaneous 2.4+5 GHz operation одного C5;
- full/lossless monitor mode, arbitrary management injection или Pineapple-class stack;
- DFS SoftAP/TX без отдельной поддержанной radar/regulatory architecture;
- decryption/cracking captured Wi-Fi traffic на устройстве;
- protocol attribution из energy-only sample;
- simultaneous high-performance Wi-Fi+Thread/Zigbee gateway без измеренного coexistence proof;
- open-air disruption чужих сетей или обход PMF.

## Условие финального ревью

После ответа по `IMP-0018` выбранный ordinary 802.15.4 scope распространяется в матрицу и target README обоих репозиториев. `IMP-0003` и возможный patched Wi-Fi backend могут оставаться conditional/deferred: они не блокируют честный public baseline, но их UI не появляется как готовая функция до отдельного proof.

## Первичные источники

- [ESP32-C5 Wi-Fi driver guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi.html)
- [`esp_wifi_80211_tx()` API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/network/esp_wifi.html)
- [ESP32-C5 RF coexistence guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)
- [ESP32-C5-WROOM-1/WROOM-1U datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html)
- [ESP-IDF IEEE 802.15.4 CLI example](https://github.com/espressif/esp-idf/tree/master/examples/ieee802154/ieee802154_cli)
- [ESP-IDF OpenThread API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/network/esp_openthread.html)
- [Espressif Zigbee SDK](https://github.com/espressif/esp-zigbee-sdk)

