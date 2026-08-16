# DM-0001 — единый resource-demand model полной базовой конфигурации

- Статус: **В работе — functional/pin/controller/STOP и numeric traffic/memory прошли ревью; power ждёт решения `IMP-0023`**
- Этап: 3 — системная архитектура и владение
- Дата начала: 2026-08-16
- Обязательный вход: frozen wishlist `INV-0004`, `DEC-0023`, reviewed `REQ-*`
- Назначение: единый неизменный вход для S3-heavy, C5-heavy и balanced/modular layouts

## Правило модели

Demand описывает нужный сервис, а не любимую реализацию. В строках ниже нельзя удалять сигнал или одновременность ради того, чтобы вариант поместился. Допустимо менять MCU owner, controller, decoder/expander/latch, transport и component placement, если acceptance boundary сохраняется и все новые failure modes учтены.

`hard` — без этого функция или safety contract теряется. `conditional` — ресурс резервируется только в конкретном qualified profile. `candidate` — способ удовлетворения demand, не само требование.

## Фиксированные ownership boundaries

| Домен | Fixed owner/boundary | Что остаётся открытым |
|---|---|---|
| Product UI, policy, storage, signing orchestration | S3 application domain | конкретные peripheral controllers/tasks/pins |
| S3 2.4 GHz Wi-Fi, ESP-NOW, native BLE | S3 integrated radio | coexistence schedule and memory budgets |
| C5 2.4/5 GHz Wi-Fi, IEEE 802.15.4 | C5 integrated radio | inter-MCU transport and scheduler |
| Consumer IR | C5 | exact GPIO, driver and STOP/power topology |
| 3× full-function nRF24 | **owner open** | S3-heavy, C5-heavy or balanced placement; function set fixed |
| External GNSS/LoRa/NFC | removable qualified accessories | connector sharing, muxing and power profiles |
| Safety authority | `DEC-0024`: latched hardware STOP resets both MCUs and dominates every external TX domain | exact latch/gate/rail BOM and measured HIL |

## Base-board hardware demand

| ID | Подсистема | Interface/controller demand | Direct/real-time demand | Concurrency and acceptance boundary |
|---|---|---|---|---|
| `DM-CORE-01` | ESP32-S3 application MCU | native USB device/recovery; internal Wi-Fi/BLE; enough flash/PSRAM; debug/recovery | reset/boot path independent of UI expander | UI/storage/audio/security parsing remain responsive under worst accepted capture; signed update and rollback recover without C5 |
| `DM-CORE-02` | ESP32-C5 radio MCU | internal Wi-Fi/802.15.4; native recovery; typed S3 link endpoint | own reset/boot; IR real-time channels | radio reset/link loss cancels TX lease; C5 is recoverable without working S3 application firmware where silicon permits |
| `DM-LINK-01` | S3↔C5 transport | full-duplex command/event/bulk capture/update; framing, flow control, DMA/IRQ where available | bounded interrupt/wakeup and reset handshake | must coexist with every local peripheral of both MCUs; no controller double-booking; update, crash dump and passive capture loss are measured |
| `DM-UI-01` | Display | high-bandwidth write bus, independent select/control, TE if used | predictable refresh deadline | spectrum/waterfall continues during SD write and radio IRQ; dirty rect/DMA are mechanisms only |
| `DM-UI-02` | Touch and ordinary controls | touch data bus/IRQ; ten ordinary physical controls or proven equivalent matrix | no lost/stuck key; local navigation without phone | long-BACK and ordinary input remain available under radio/storage load; matrix scan cannot create ghost dangerous action |
| `DM-SAFE-01` | Physical STOP | `DEC-0024` latched `TX_KILL`: both MCU reset paths plus independent power/inhibit of every TX-capable external domain | asynchronous dominance; separate physical re-arm; own latch indicator | works with hung S3/C5, stalled bus, corrupt UI, update/reset and attached TX accessory; release does not re-arm; old TX lease never returns |
| `DM-SAFE-02` | Actual-TX indication | hardware or independently trustworthy detectors/enable-state per TX domain | visible latency bounded independently of application screen | software intent alone is insufficient; detector unknown/fault is visible and can inhibit Controlled operation |
| `DM-STO-01` | microSD | bulk read/write, card detect, recoverable filesystem, DMA-capable path preferred | bounded write chunks and backpressure | capture does not claim lossless; removal/full/corrupt card cannot block STOP, audio deadline or radio servicing |
| `DM-USB-01` | USB | native S3 device, signed update/recovery, serial; optional MSC/HID profiles | boot/recovery controls remain reachable | BadUSB execution has separate Controlled gate; normal service cannot arm it |
| `DM-AUD-01` | ES8311 mono codec | four S3 I²S signals without required MCLK; I²C control | continuous bidirectional mono DMA and clock | simultaneous ADC+DAC, SD recording and selected radio session; exact rate/buffer budget later measured |
| `DM-AUD-02` | Analog audio routing | RX source select, speaker select, TX mic select/codec enable as separate safe controls | hardware default-to-analog without MCU/codec | ordinary listening and mic voice survive reset/power loss; selector action never raises PTT |
| `DM-RX-01` | Si4732 receiver | I²C/control plus analog audio to RX mux; reset/power if required | optional status/interrupt | scan/audio/capture coexist with codec/SD; patch load is bounded and not a firmware trust bypass |
| `DM-VHF-01` | SA518 target / SA868S fallback | one UART command path; PTT, power-down and power-level controls; analog RX/TX audio | PTT and high-power enable are direct safe-state demands | half-duplex; PTT default RX, high power physically unavailable until gated; voice/modem audio deadlines measured |
| `DM-SUB-01` | CC1101 | full-duplex SPI, own CS, two GDO-class event signals preferred, SP4T/filter controls | low-latency RX/TX FIFO service and actual TX inhibit | sequential sweep/capture under display+SD; no shared-bus burst may cause undocumented loss; reset returns IDLE |
| `DM-N24-01` | 3× nRF24 | one qualified SPI master domain; three independent logical CS and CE; IRQ source identification; exact module power | all three CE/roles independently controlled; simultaneous RX IRQ service | three simultaneous PRX and independent PTX/PRX sessions; no one-radio+switch substitute; shared IRQ allowed only with bounded identification/loss proof |
| `DM-IR-01` | Consumer IR on C5 | two independent RX capture paths plus TX carrier path/driver; exact C5 RMT allocation | both RX resources and deterministic TX carrier; optical inhibit | robust envelope and carrier-learning can be sampled as specified; TX defaults off and STOP dominates driver |
| `DM-RF-01` | RF coexistence | cross-MCU lease/scheduler and per-path antenna/power knowledge | bounded preemption and actual owner visibility | unsafe simultaneous TX prohibited until pairwise self-desense/EMC HIL; receive loss and degraded modes are explicit |
| `DM-IND-01` | Status LED/buzzer/backlight | low-rate controls; dimming waveform if brightness accepted | active-TX/critical state has priority | quiet/dim does not hide TX, STOP fault, update failure or critical battery |
| `DM-PWR-01` | Battery/power domains | gauge/ADC, charger status, controllable peripheral rails, brownout and wake sources | hardware safe defaults for all TX enables | peak/thermal budget covers selected simultaneous session; reset/brownout cannot leave accessory or PA transmitting |
| `DM-EXP-01` | I/O expanders/decoders/latches | addressable control with defined reset state and interrupt aggregation | safety-critical output allowed only behind hardware-safe default and STOP dominance | exact count selected after direct-pin budget; an expander may reduce GPIO but cannot become the only STOP path |

## Qualified removable-accessory demand

Эти строки не означают, что аксессуар установлен одновременно или входит в base BOM. Base board обязан иметь только принятый attachment profile; accessory-specific runtime resources активируются после обнаружения и qualification.

| ID | Профиль | Demand | Mutual exclusion / boundary |
|---|---|---|---|
| `DM-EXT-01` | M5 Unit GPS v1.1 | 5 V `PORT.C`, one UART RX/TX profile, power control/detection desirable | отдельный GPS и GNSS U214 mutually exclusive as active backend; no third onboard GNSS |
| `DM-EXT-02` | U214 `EXT-RF14` | SPI plus CS, IRQ/DIO, BUSY, reset; independent GNSS UART; qualified accessory power and antenna gate | one active LoRa backend; its GNSS may replace external Unit GPS; SPI/UART pins are not called free when Cap attached |
| `DM-EXT-03` | M5 Unit NFC U216 | qualified 5 V `PORT.A-NFC`, I²C plus interrupt/reset if exact revision exposes them, hot-plug-safe policy | not generic 3.3 V Grove; sensitive operations inherit Controlled gate |
| `DM-EXT-04` | Generic low-risk I²C Unit | separately labelled electrical descriptor, discovery and address-conflict policy | no blanket M5 compatibility and no borrowing safety-critical lines |
| `DM-EXT-05` | Later optional radio/compute profiles | explicit external power/data/descriptor contract only after change review | no internal GPIO/BOM reservation now; attachment delta reopens affected architecture artifacts |

## Mandatory concurrency scenarios

| ID | Scenario | Simultaneously demanded resources | Pass condition for every layout |
|---|---|---|---|
| `SCN-01` | 3-sector 2.4 GHz hunt | 3×nRF24 PRX/IRQ/SPI, UI/display, timestamp, optional SD log | all three radios sampled in comparable windows; loss/age visible; controls responsive |
| `SCN-02` | One-shot wardrive | S3 Wi-Fi/BLE time sharing, C5 passive radio selected profile, CC1101 scan, external GNSS, SD, display | scheduler states actual coverage; privacy session bounded; absence is never inferred from unsampled time |
| `SCN-03` | Radio audio record/decode | Si4732 or voice RX, analog mux, ES8311 ADC/I²S DMA, SD, display | no unreported audio gap; SD backpressure visible; STOP remains immediate |
| `SCN-04` | Voice modem/TX | ES8311 ADC/DAC, SA51x UART/audio/PTT, region/power gate, UI, actual-TX, STOP | bounded key time; reset/underrun releases PTT; ordinary analog bypass survives codec fault |
| `SCN-05` | U214 field session | U214 LoRa SPI/events, U214 GNSS UART, SD, UI, other-radio scheduler | LoRa TX self-desense effect on GNSS measured; one backend rules enforced |
| `SCN-06` | Local management/update | S3 SoftAP or USB, storage, signature verification, optional C5 bulk update over link | rollback/recovery works; no stale TX lease; update cannot starve STOP |
| `SCN-07` | Contained resilience test | one armed TX path, actual-TX detector, countdown/dead-man/STOP, audit log | hardware containment and target authorization are proven before arm; hard timeout works with UI/MCU fault |
| `SCN-08` | Failure storm | SD fault plus IPC loss or peripheral timeout during active receive/TX preparation | no unintended TX, bounded recovery, honest loss/unknown state, local control remains usable |

## Numeric budgets still to fill before layout scoring

| Budget | Required evidence |
|---|---|
| Direct GPIO and strapping | exact S3/C5 module pin capability table including boot, USB, flash/PSRAM and input-only constraints |
| Peripheral controllers | exact SPI/I²C/I²S/UART/RMT/SDMMC/SDIO allocation with DMA/interrupt conflicts |
| Bus bandwidth/latency | measured or conservative traffic envelopes for display, SD, CC1101, 3×nRF24, U214 and inter-MCU link |
| Memory | worst simultaneous buffers, protocol stacks, databases, UI assets, audio and update staging with margin |
| Power/thermal | min/typ/max and startup/TX peaks per rail/scenario, battery/charger limits and brownout margin |
| RF coexistence | pairwise TX/RX matrix, antenna isolation/self-desense, forbidden and degraded combinations |
| Recovery/safety | BOOT/RESET/debug access, signed update/rollback, independent STOP fan-out and actual-TX proof |
| Cost/area | base BOM/PCB/test NRE; optional accessories counted separately and compared by full ownership cost |

## Gate to layout generation

До выпуска сравнительных layouts требуется:

- [x] frozen functional wishlist and reviewed `REQ-*`;
- [x] fixed/open ownership boundaries stated without contradiction;
- [x] base and optional accessory demand separated;
- [x] mandatory concurrency/failure scenarios listed;
- [x] exact S3/C5 pin capability and controller inventory (`PIN-0001`);
- [x] conservative numeric traffic/memory envelopes (`BUD-0001`, `REV-0003D`);
- [ ] final power/rail envelope after `IMP-0023`;
- [x] independent STOP fan-out target architecture (`DEC-0024`);
- [x] scoring rubric with hard-fail criteria (`SC-0001`).

После решения оставшейся power/rail строки один и тот же revision `DM-0001` копируется в scorecard всех вариантов. Изменять demand внутри отдельного layout запрещено.
