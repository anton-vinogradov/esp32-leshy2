# REQ-LORA-0001 — external SX1262 LoRa/FSK/GNSS expansion contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-LORA-01`–`C-LORA-09`, `C-HWX-02`
- Обязательные решения: `DEC-0003`, `DEC-0005`, `DEC-0006`, `DEC-0008`, `DEC-0010`, `DEC-0013`, `DEC-0022`, `DEC-0023`
- Пересечение: `REQ-GNSS-0001`, `REQ-X-0001`

## Граница документа

LoRa и GNSS не входят в base-board BOM. M5Stack U214 — первый `EXT-RF14` backend: SX1262 plus AT6668 GNSS, с квалифицируемыми common 868/915 profiles внутри фактических 868–923 MHz module limits. Silicon-wide 150–960 MHz не переносится на готовый U214. Другой expansion carrier допустим только как отдельный профиль, а не как обязательный второй LoRa.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-LORA-01` | все | `conditional` | Сквозной attachment | Runtime определяет exact backend/revision, antenna and regional profile. Одновременно активен один LoRa backend; hot-plug не допускает TX, bus contention или key exposure. |
| `REQ-LORA-02` | `C-LORA-01` | `conditional` | Основной | LoRa P2P TX/RX предоставляет explicit frequency/BW/SF/CR/power/preamble/network profile, conservative defaults, peer identity and interoperable fixture tests. |
| `REQ-LORA-03` | `C-LORA-02` | `defer-release` | Основной | Meshtastic-compatible profile сохраняется как optional software adapter после version/API/licence/key/storage/interoperability proof. Core P2P/GNSS/update от него не зависит. |
| `REQ-LORA-04` | `C-LORA-03` | `conditional` | Основной | LoRa APRS beacon/RX and optional iGate/digipeater требуют callsign/licence/band-plan/path/duplicate/Internet-forwarding profile; gateway работает только с явным consent. |
| `REQ-LORA-05` | `C-LORA-04` | `conditional` | Основной | LoRaWAN OTAA/ABP Class A входит с owner keys, regional channel plan, frame-counter persistence and secure key lifecycle. Class C включается только при measured power/thermal budget. |
| `REQ-LORA-06` | `C-LORA-05` | `conditional` | Лаборатория | Passive scan/log показывает profile/coverage/RSSI/SNR/error/loss; LoRa sync detection не равна packet decode, а encrypted payload не представляется plaintext. Sensitive identifiers are minimized. |
| `REQ-LORA-07` | `C-LORA-06` | `conditional` | Основной | Link/range test показывает measured RSSI/SNR/PER/profile/location-quality/sample count. Он не обещает абсолютную дальность и соблюдает region/duty/power limits. |
| `REQ-LORA-08` | `C-LORA-07` | `conditional` | Основной | Доказанные SX1262 packet profiles FSK/GFSK/MSK/GMSK/OOK могут поддерживать host-generated RTTY/AX.25-compatible sessions после interoperability and emission proof. CW — только bounded continuous-wave test source, не универсальный modulation mode. |
| `REQ-LORA-09` | `C-LORA-08` | `conditional` | Основной | Bounded file transfer использует integrity, resume, size/rate/duty budget and authenticated peer where required. Firmware transfer остаётся inert package и не обходит signed-update verification. |
| `REQ-LORA-10` | `C-HWX-02` | `conditional` | Основной/performance | SX1262 boosted-RX profile включается только после measured sensitivity/current/thermal/coexistence comparison. Legacy `+15–30%` не является требованием и удалено как недоказанное. |
| `REQ-LORA-11` | `C-LORA-09` | `conditional` | Контролируемая зона, `BOTH` | Carrier/reactive resilience test — only conducted/RF-shielded on authorized endpoints, no-leakage validated, minimum power, bounded frequency/rate/time, dead-man and independent STOP. Open-air jammer отсутствует. |
| `REQ-LORA-12` | all keys/records | `conditional` | Сквозной security/storage | LoRaWAN/mesh/P2P keys have typed encrypted storage, least privilege, explicit rotation/revoke/delete and factory-reset proof. Imported configs/files are versioned, bounded, fuzzed and inert until validated. |
| `REQ-LORA-13` | all TX | `conditional` | Сквозной regulatory | Region source/revision, exact U214 frequency limit, channel mask, EIRP, antenna gain, duty/dwell and licence/callsign gates checked before every session; no silicon-only band appears in UI. |
| `REQ-LORA-14` | all | `conditional` | Сквозной coexistence | Shared SPI/UART/GNSS/resources and other transmitters use measured scheduler with active owner/preemption/loss visibility; RF self-desense and power peaks pass HIL. |
| `REQ-LORA-15` | all update | `conditional` | Сквозной openness | Optional mesh/gateway adapters are removable, versioned and owner-controlled; proprietary service or cloud is not required to build, update, recover or use P2P/GNSS baseline. |
| `REQ-LORA-16` | all | `acceptance` | Сквозной HIL | Exact U214 and each later carrier pass revision detection, 868/915 regional profiles, P2P/LoRaWAN/optional adapters, GNSS coexistence, sensitivity/current/TX spectrum, STOP/reset/hot-plug/update and contained-test fixtures. |

## Явно не обещается

- onboard LoRa/GNSS или одновременно два LoRa backend;
- U214 operation outside its exact 868–923 MHz module specification;
- universal LoRa promiscuous decode/decryption;
- fixed range improvement from boosted gain;
- open-air interference against third parties.

## Первичные источники

- [M5Stack Cap LoRa-1262 U214 documentation](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [Semtech SX1262 product page](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262)
- [LoRaWAN Link Layer Specification 1.0.4](https://lora-alliance.org/wp-content/uploads/2021/11/LoRaWAN-Link-Layer-Specification-v1.0.4.pdf)
