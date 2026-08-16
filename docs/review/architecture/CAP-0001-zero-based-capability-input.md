# CAP-0001 — zero-based capability input

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, шаг 1
- Входы: `INV-0004`, `W-OWN-01..15`, reviewed `REQ-*`, accepted `DEC-*`
- Не входы: legacy source/schematic, прежние `DM/BUD/PIN/SC/LAY/CMP/ADR`, historical owner assumptions

## Цель

Зафиксировать, что должен давать готовый продукт и какие физические свойства для этого нужны, не выбирая MCU owner, bus, transport, expander, GPIO или component placement. Это единственный функциональный вход `CON-0001` и `RES-0001`.

## Неподвижные продуктовые инварианты

| ID | Инвариант | Что не следует из него |
|---|---|---|
| `CI-01` | автономный all-in-one field device | не запрещает optional accessories; phone/cloud не могут быть обязательны |
| `CI-02` | Main → Lab → Controlled Zone; install pledge; fresh banner каждый вход | вход в level не вооружает конкретный tool |
| `CI-03` | conservative TX, independent physical STOP, actual-TX evidence, bounded dead-man | application state не является достаточным safety proof |
| `CI-04` | cost reduction only without product loss | legacy routing/part count/cheap module не дают приоритета |
| `CI-05` | open owner-controlled signed update + rollback, no mandatory irreversible lockdown | device не становится closed appliance |
| `CI-06` | S3 remains application/native 2.4 Wi-Fi/BLE domain; native BLE baseline belongs to S3 | это не назначает S3 владельцем external radios |
| `CI-07` | C5 remains 2.4/5 GHz Wi-Fi + IEEE 802.15.4 domain and owns dual-path consumer IR | это не назначает C5 владельцем nRF24 |
| `CI-08` | exactly three simultaneous full-function nRF24 paths | owner/controller/topology полностью открыты |
| `CI-09` | onboard ES8311 mono digital audio with hardware-default analog bypass | I²S pins, muxes и audio owner ещё не выбраны |
| `CI-10` | no onboard GNSS or LoRa; external Unit GPS/U214/modular profiles retained | existing connector/pinout не обязателен |
| `CI-11` | external HF NFC first profile, onboard Si4732, CC1101 and conditional analog voice backend retained | exact ports/frontends/modules remain qualification work |
| `CI-12` | local UI and essential operation work without phone | exact button count, matrix и expander не заданы wishlist |

## Hardware-neutral capability atoms

| Atom | User result | Physical/service consequence without implementation choice |
|---|---|---|
| `CA-CORE` | launcher, local settings, policy, audit, self-test, factory reset | trusted application compute, local display/input, persistent configuration, clock and fault state |
| `CA-STORE` | SD files, databases, PCAP/audio/track/session logs, inert import/export | removable bulk storage, bounded buffering, power-loss recovery, protected secret vault |
| `CA-USB` | console/export/update and separately gated HID automation | recoverable wired data/service path, explicit host ownership and no dual-writer storage |
| `CA-UPD` | independently verifiable updates for every programmable domain | recovery entry, target identity, owner signature, rollback and TX-off update state |
| `CA-W24` | S3 2.4 GHz STA/AP/SoftAP/ESP-NOW, observation and contained tests | S3 native RF/time-sharing domain, antenna, region/power/safety evidence |
| `CA-BLE` | S3 native scan/advertise/connect/GATT/SMP/HID and privacy/security tools | same S3 radio coexistence domain; no separate BLE-sniffer promise |
| `CA-W5` | C5 selectable 2.4/5 GHz Wi-Fi observation/connect/public TX classes | C5 native RF domain, 5 GHz RF path, region/DFS/PMF evidence and typed host service |
| `CA-154` | raw IEEE 802.15.4, OpenThread and optional conditional Zigbee | C5 shared 2.4 GHz scheduler, protocol memory/storage and safe active-test boundary |
| `CA-N24` | 3× independent PTX/PRX/ESB/RPD paths, simultaneous PRX/hunt and contained tests | three radio/antenna/power/control/data paths, independent state and bounded common timing; no owner assumed |
| `CA-SUB` | CC1101 tune/RSSI/OOK/packet capture, replay and contained test source | qualified Sub-GHz RF/filter/antenna path, deterministic FIFO/event service and TX gate |
| `CA-RX` | Si4732 FM/RDS/LW/MW/SW, conditional SSB/CW, scan/audio/decode | receive-only RF frontend, control, mono analog audio, protection/mute around other TX |
| `CA-VOICE` | half-duplex analog FM voice, tones, scan, AFSK/AX.25/APRS/SSTV and bounded relay | qualified VHF/UHF module, UART/control, analog RX/TX audio, PTT/power/dead-man/actual-TX |
| `CA-IR` | robust receive + 30–60 kHz carrier learning + replay/remote/contained sweeps | C5 two capture paths, deterministic carrier TX, optical driver, optical-off STOP state |
| `CA-AUDIO` | onboard mono capture/play/record/decode/injection with analog fallback | full-duplex digital audio service, codec control, analog source/sink routing, amp/jack/mic paths |
| `CA-GNSS` | position/time/track/geotag/integrity via qualified external backend | removable powered serial profile, one active backend, attach/remove/fault policy |
| `CA-LORA` | external U214/common 868/915 LoRa/FSK/GNSS and later modular backend | removable powered packet-radio profile with event/control/data, antenna/region/STOP boundary |
| `CA-NFC` | external HF A/B/F/V read/write/analysis/emulation and conditional relay | removable 5 V, 3.3 V-safe control profile, RF-off unknown state and sensitive-data vault |
| `CA-UI` | touch + local physical navigation/text/PTT/STOP; status visible without phone | complete local human interface, separate emergency/control semantics and readable critical indication |
| `CA-SAFE` | hard STOP, per-action arming, actual-TX/fault state and containment | asynchronous hardware dominance over every TX-capable path plus trustworthy physical/readable evidence |
| `CA-PWR` | battery/charge/sleep, controlled rails, no TX after reset/brownout | power tree sized by scenarios, default-off TX domains, measurement and thermal/fault margins |
| `CA-EXP` | qualified external profiles without blanket compatibility | keyed/labelled electrical profiles, discovery, current limit, bus isolation/recovery and safe unknown behavior |

## Functional scope by reviewed group

| Wishlist group | Base or attached result retained | Optional/deferred boundary |
|---|---|---|
| `WG-01` platform/UI/safety/storage | `CA-CORE/STORE/USB/UPD/UI/SAFE/PWR/EXP` | auto-brightness only with sensor; service diagnostics separate from user tools |
| `WG-02` navigation/log/sessions | external GNSS, time/track/geotag, combined foreground sessions | no onboard GNSS, no safety-of-life claim, no hidden location capture |
| `WG-03` broadcast/voice | Si4732 + audio record/decode; conditional SA518/SA868S voice/modem | synchronous AM, VOX, digital voice/full duplex remain explicit deferred profiles |
| `WG-04` IR | dual receive evidence and own remote/replay; gated authorized/isolated sweeps | no 455 kHz learning without new proof |
| `WG-05` HF NFC/RFID | external U216-class HF operations with tiered gates | LF frontend, second relay frontend and heavy recovery compute remain optional/deferred |
| `WG-06` Wi-Fi/IP | S3 2.4 plus C5 2.4/5 services, passive evidence and public active classes | no lossless monitor/cracking/private management-TX promise |
| `WG-07` BLE/802.15.4 | S3 native BLE; C5 raw 802.15.4/OpenThread; conditional Zigbee | connection sniffer, Mesh and Classic do not burden base hardware |
| `WG-08` 3×nRF24 | all native radio modes, independent sessions, parallel RPD/PRX and contained tools | no one-radio+switch substitution and no fake RSSI/direction claim |
| `WG-09` Sub-GHz/LoRa | onboard CC1101 plus removable common-band U214/modular profile | no onboard LoRa and no open-air interference mode |

## Mandatory composition semantics

- A combined view stores source-labelled, timestamped evidence; energy, protocol and identity are never conflated.
- A compound session inherits the most restrictive safety/privacy/legal gate of every action it invokes.
- Capture and import remain inert; replay/TX revalidates target, region, profile, power, duration and evidence.
- `unknown`, `unsupported`, `unsampled`, `lost` and `fault` are first-class states and never converted to absence, success or safety.
- Simultaneous TX is not implied by having multiple transmitters. Simultaneous receive or TX/RX is a measured pair capability with visible degradation.
- Optional hardware does not burden base BOM unless its accepted attachment profile itself requires protection, discovery or recovery resources.

## Open architecture variables

Nothing below is decided by this document:

- nRF MCU/controller/bridge ownership and whether control/data are centralized or distributed;
- number and exact variants of programmable controllers beyond the fixed S3/C5 product domains;
- inter-controller transport and recovery topology;
- exact flash/PSRAM/RAM, SD topology and buffering;
- display/touch/control component choices and number/topology of physical buttons;
- SPI/I²C/UART/I²S/USB allocation, expanders/decoders/muxes and every GPIO;
- exact RF modules, RF switches/filters/antennas/detectors and their physical placement;
- power-tree components, rails, connectors, service ports and enclosure layout;
- whether any legacy circuit or net is reused.

## Coverage and review gate

| Source set | Coverage result |
|---|---|
| `W-OWN-01..15` | 15/15 represented in `CI-*`, composition semantics or document workflow |
| `WG-01..09` | 9/9 represented in capability atoms and scope table |
| `REQ-SYS/GNSS/RX/VHF/IR/NFC/W24/W5/BLE/N24/SUB/LORA/X` | 13/13 mapped to one or more `CA-*`; no requirement document omitted |
| `W-EXTRA-01..10B` | retained only at accepted conditional/deferred boundary; no hidden base resource assumed |
| Legacy owners/buses/pins/layouts | zero entries used as constraints |

No pin, bus or owner allocation is present in `CAP-0001` except owner placements explicitly accepted in product requirements (`CI-06/07`). Step 1 therefore receives **«Проведено ревью»** and becomes the sole functional input of `CON-0001`.
