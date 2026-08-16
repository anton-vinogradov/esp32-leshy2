# REQ-W24-0001 — S3 Wi-Fi 2.4 GHz and ESP-NOW contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-W24-01`–`C-W24-12`, `C-X-01`–`C-X-04`, `C-X-06`–`C-X-08`, `C-X-11`, `C-UX-01`, `W-EXTRA-01`, `OUT-01`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0004`, `DEC-0005`, `DEC-0010`, `DEC-0013`, `DEC-0021`, `DEC-0022`, `DEC-0023`
- Пересечение: `REQ-W5-0001`, `REQ-BLE-0001`, `REQ-X-0001`

## Граница документа

ESP32-S3 остаётся основным application MCU, владельцем своего 2.4 GHz Wi-Fi/BLE radio и baseline native BLE. Wi-Fi scan/connect/SoftAP/ESP-NOW, passive observation, defensive detection, identity tests и disruptive resilience tests — разные режимы с разными prerequisites. Публичный ESP-IDF не представляется как произвольный monitor/injection stack.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-W24-01` | `C-W24-01`, `C-W24-09` | `include` | Основной | AP scan, channel/security/RSSI view, подключение к собственным/администрируемым STA/AP и opt-in MAC randomization. UI показывает actual interface/mode/channel/region и не выдаёт отсутствие наблюдения за отсутствие сети. |
| `REQ-W24-02` | `C-W24-03` | `conditional` | Основной | Packet-rate/channel-load view публикует измеренное окно, dwell, пропуски и метод; это не абсолютная утилизация эфира и не protocol attribution. |
| `REQ-W24-03` | `C-W24-12` | `conditional` | Основной | Локальный authenticated SoftAP/Web UI обслуживает настройку, export и recovery. Он не стартует скрыто, не занимает radio во время несовместимой session и не заменяет on-device управление. |
| `REQ-W24-04` | `C-W24-12` | `conditional` | Основной/update | Wi-Fi OTA принимает только owner-authorized signed image, проверяет target/version/hash/signature/rollback и не снижает `DEC-0013`; firmware C5 передаётся через отдельно проверенный меж-MCU update path. |
| `REQ-W24-05` | `C-W24-11` | `conditional` | Основной | ESP-NOW link предназначен для собственных peers, использует explicit provisioning, PMK/LMK lifecycle, peer allowlist, replay/freshness policy и видимый encryption state. Unencrypted broadcast не переносит secrets. |
| `REQ-W24-06` | `C-W24-01`, `C-W24-02` | `conditional` | Лаборатория | Passive AP/client/beacon/probe/management/control/data capture через public promiscuous API сохраняет channel/timestamp/class/FCS/error/filter/loss/coverage и privacy-redacted PCAP. Full/lossless monitor и decryption не обещаются. |
| `REQ-W24-07` | `C-W24-04` | `conditional` | Лаборатория | Deauth/rogue/evil-twin detector показывает PMF/security/evidence/confidence/unknown; единичный frame или совпавший SSID не доказывает атаку. |
| `REQ-W24-08` | `C-W24-11` | `conditional` | Лаборатория | ESP-NOW passive observation отделено от link mode, минимизирует identifiers/payload и не обещает plaintext для encrypted peers. |
| `REQ-W24-09` | `W-EXTRA-01`, `OUT-01` | `conditional` | Лаборатория, `AUTHORIZED_TARGET` | Passive EAPOL/PMKID collection разрешается только на своей/письменно разрешённой сети после fixture proof полноты и PCAP interoperability. Это не active exploit и не встроенный cracking; записи — sensitive vault data. |
| `REQ-W24-10` | `C-W24-07` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Evil Portal использует exact authorized SSID/target/content preview. Credential collection выключена по умолчанию; при явно разрешённом тесте данные шифруются, имеют retention/delete и не уходят третьей стороне. |
| `REQ-W24-11` | `C-W24-08` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Evil Twin/rogue/honeypot/Karma-like tests требуют exact target identity, nearby-client exclusion plan, bounded duration, conservative power и audit record. Uncontrolled attraction of third-party clients отсутствует. |
| `REQ-W24-12` | `C-W24-09` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Identity spoof допускается только как отдельный test action с exact address preview; privacy randomization Main не делит с ним кнопку или сохранённый armed state. |
| `REQ-W24-13` | `C-W24-10` | `conditional` | Внутренний enabling API | Raw TX не является пользовательским обходом gates. Каждый caller имеет typed schema и разрешён только для документированных public frame classes: beacon, probe request/response, action и non-QoS data. Import/raw bytes инертны. |
| `REQ-W24-14` | `C-W24-05` | `defer` | Контролируемая зона, `AUTHORIZED_TARGET` | Deauth/disassoc/arbitrary management TX не входят в public baseline. Version-locked private backend возможен только отдельным решением с provenance/rights/SBOM/hash/signature/rollback/HIL и честным PMF result. |
| `REQ-W24-15` | `C-W24-06` | `conditional` | Контролируемая зона, `BOTH` | Beacon/probe/auth/assoc load tests выполняются только conducted/RF-shielded на authorized fixture: no-leakage check, minimum power, packet/time ceiling, countdown, dead-man, independent STOP. |
| `REQ-W24-16` | `C-W24-11` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | ESP-NOW replay/spoof/security tests используют exact allowlisted peer/session corpus, bounded count/time and preview; они не наследуют ключи ordinary link автоматически. |
| `REQ-W24-17` | все radio | `conditional` | Сквозной coexistence | S3 Wi-Fi/BLE делят radio; C5 Wi-Fi/802.15.4, три nRF24 и прочие TX входят в общий scheduler. UI показывает active owner/preemption/loss; одновременный unsafe TX запрещён до RF HIL. |
| `REQ-W24-18` | все records | `conditional` | Сквозной privacy/storage | Capture/session formats versioned, bounded и fuzzed; identifiers/payload/location/keys типизированы по чувствительности, минимизированы, шифруются где нужно и имеют явные export/delete/retention/reset tests. |
| `REQ-W24-19` | все TX | `conditional` | Сквозной safety | Region/channel/power/target/duration preview, conservative default, fresh Controlled-Zone banner, per-tool arming, local dead-man, actual-TX indication и independent STOP обязательны; reset/crash/update не оставляют autonomous TX. |
| `REQ-W24-20` | все | `acceptance` | Сквозной HIL | Exact S3 module/antenna/IDF fixture проверяет STA/AP/SoftAP/ESP-NOW, public capture/TX classes, PMF/privacy, loss, coexistence, update/rollback, crash/reset/STOP и contained active tests. `Unknown` не превращается в success/safe. |

## Явно не обещается

- lossless/full monitor, decryption или universal client inventory;
- public deauth/disassoc/arbitrary management injection;
- одновременная независимая работа S3 Wi-Fi и BLE;
- on-device password cracking;
- open-air disruptive testing чужих сетей.

## Первичные источники

- [ESP32-S3 Wi-Fi driver guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/wifi-driver/index.html)
- [`esp_wifi_80211_tx()` API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/network/esp_wifi.html)
- [ESP-NOW programming guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/network/esp_now.html)
- [ESP32-S3 Wi-Fi security](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/wifi-security.html)
