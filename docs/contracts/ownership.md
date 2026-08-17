# Контракт владения аппаратными блоками

Статус: **Владельцы переоткрыты `DEC-0032`; требования к локальной
ответственности сохранены**.

Ни один ESP32/RP/expander, bus или exact pin сейчас не является target owner.
Former `PKG-0001/SYN-3A` maps остаются reference studies. Будущие complete
candidates обязаны назначить каждую строку ниже и сравниваться целиком.

| Capability group | Обязательная локальная ответственность | Owner |
|---|---|---|
| product UI/state/files | автономный UI, единственный normal filesystem writer, visible failure states | open |
| native Wi-Fi 2.4/5 and IEEE 802.15.4 | timing, country/profile checks, queues, local safe-off | open |
| native Bluetooth LE and 2.4 Wi-Fi/ESP-NOW | product identity/bonds, ordinary profiles, explicit security boundaries | open |
| 3× full-function nRF24 | native feature set, independent PTX/PRX, simultaneous RX, source/drop/timestamp evidence | open |
| packet Sub-GHz | precise RSSI/capture/decode evidence and bounded TX control | open |
| analog voice/PTT | local PTT/dead-man/TX evidence and fail-safe control | open |
| broadcast/audio/IR | continuous audio failure path, measured IR carrier provenance and safe TX | open |
| external GNSS/LoRa/NFC | profile identity, power/isolation/no-backfeed and removal-safe state | open |
| hard STOP/re-arm | AON hardware-dominant reset of S3+C5+RP plus independent TX gates; no release-to-rearm | paper-reviewed exact circuit; electrical/HIL proof remains |
| updates/recovery/diagnostics | owner-controlled signed lifecycle plus independent physical service access for every programmable chip | open |

## Междоменные правила будущих candidates

- IPC передаёт typed intent and bounded data, а не remote raw GPIO.
- Peripheral deadlines и TX lease expiry остаются локальными у физического owner.
- Peer/link/reset/brownout failure приводит к видимому safe/degraded state.
- STOP, physical PTT, re-arm and critical actual-TX evidence cannot depend solely
  on a non-safety GPIO expander or another programmable peer.
- Every selected programmable chip remains recoverable and diagnosable without a
  functioning peer or application image.

Exact ownership, transports, pins and reset topology become normative only at
`FLOW-0001/G7` after reviewed product design, whole-device optimality and
conceptual placement. Any candidate that drops a reviewed capability must create
a finding and owner decision instead of changing this table silently.
