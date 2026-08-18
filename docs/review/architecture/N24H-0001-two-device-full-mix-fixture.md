# N24H-0001 — staged two-device three-nRF full-mix fixture

- Статус: **Проведено ревью test-plan input; L0/T1 measurements not started**
- Дата: 2026-08-17
- Decision: [`DEC-0047`](../decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md)
- Requirement: [`REQ-N24-0001`](../requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)
- RF boundary: [`RFQ-0002`](RFQ-0002-g2f-3i-rf-concurrency-boundary.md)
- Exact DUT endpoint: [`N24E-0001`](N24E-0001-exact-three-nrf-electrical-endpoint.md)

## Уровни стенда

| Level | Hardware | Что закрывает | Чего не закрывает |
|---|---|---|---|
| `L0 DIV↔DIV` | два заказанных ESP32-DIV с записанными board/module identities | раннее воспроизведение `3R/1T2R/2T1R/3T`, packet manifest/log protocol, observed loss/self-desense, firmware-test ergonomics | Leshy2 sensitivity, rail/transient, antenna isolation, thermal, emissions или target reproducibility |
| `T1 TARGET` | два сопоставимых Leshy2 target revisions либо Leshy2 DUT + calibrated conducted/OTA peer | production versioned RF/power envelope и role-reversal/reproducibility acceptance | arbitrary untested channels, powers, poses или same-frequency full duplex |

`L0` — полезный pre-HIL, а не суррогат `T1`. Отличия modules, rails, bus sharing,
antenna geometry и enclosure всегда записываются, а результаты двух уровней не
смешиваются в одну pass-метку.

## Роли target-стенда

```mermaid
flowchart LR
    C["Test coordinator<br/>profile + common test ID"]
    D["Device A — DUT<br/>nRF0 / nRF1 / nRF2"]
    P["Device B — observer/peer<br/>nRF0 / nRF1 / nRF2"]
    E["Measured RF path<br/>distance / pose / attenuation / containment"]
    C --> D
    C --> P
    D <--> E
    E <--> P
```

Оба устройства сохраняют собственные журналы. Coordinator не управляет raw
CE/GPIO: он выдаёт один test ID, role/channel/rate/power manifest и start
barrier. Сопоставление выполняется по test ID, radio identity, packet sequence
и timestamps с записанной неопределённостью синхронизации.

## Обязательная матрица

| DUT role mix | Observer/peer action | Что доказывается |
|---|---|---|
| `3R` | три известных packet streams либо один последовательно calibrated source | isolated и simultaneous RX baseline, loss/age/RPD per radio |
| `1T+2R` | принимает DUT TX и одновременно подаёт два wanted streams на DUT RX | реальная TX continuity, peer RX continuity и measured desense без hidden gaps |
| `2T+1R` | принимает два DUT streams и подаёт wanted stream на DUT RX | two-local-TX current/coupling и remaining RX envelope |
| `3T` | принимает/считает все DUT streams | three-TX scheduling, packet rail peak/average, droop, thermal and emissions |
| role reversal | Device B becomes DUT, Device A observer | на `L0` — asymmetry двух DIV; на `T1` — target device-to-device calibration and reproducibility |
| same/near channel negative cases | known packet sequences and power | collision/desense classified as expected/qualified/unsupported, never hidden success |

## Записываемые параметры

- exact DUT/observer hardware, firmware, radio/module/antenna revision and
  calibration identity;
- per-radio PTX/PRX state, `RF_CH`, rate, configured/measured power, address,
  retry/ACK mode and packet sequence;
- distance, enclosure/hand pose, antenna orientation, attenuator/cable/shield
  identity where used, temperature and supply state;
- transmitted/received/CRC-failed/duplicate/lost counts, FIFO/IRQ latency,
  RPD hits, RX gaps, reset/fault and actual-TX evidence;
- actual-TX threshold/latency at `RF_CH` 0, 100 and 125, including a strong
  inbound-only negative case and detector hold through common-rail QOD fall;
- 10-Mbit/s buffer-path integrity, 100-ms POR, three identity reads and
  measured rail/no-backpower behavior before the RF role schedule starts;
- wanted/reference level or a calibrated path-loss proxy. Uncalibrated RSSI
  from an unrelated receiver cannot close nRF sensitivity acceptance.

## Pass boundary

`L0` passes as pre-HIL evidence only when both ESP32-DIV identities and all
hardware differences are recorded; он никогда не выдаёт target pass.

Target digital full mix passes only when the Leshy2 DUT executes the complete role schedule
without peer standby, hidden CE suppression or unexplained RX gaps. RF envelope
points pass individually with versioned limits; a passed far-channel point
does not promote same-channel operation. Power passes only if `3T` remains
inside rail, droop, temperature and STOP limits.

Open-air active security/interference cases are not implied. Dangerous cases
use the existing Controlled-Zone authorization plus conducted/shielded-room
containment requirements.
