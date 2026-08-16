# SYN-0001 — zero-based whole-device architecture candidates

- Статус: **Проведено ревью набора candidates; победитель не выбран**
- Дата: 2026-08-16
- Этап: 3, шаг 4
- Канонические входы: reviewed `CAP-0001`, `CON-0001`, `RES-0001`, `SRC-0001`
- Не входы: legacy schematic/source, прежние owner/bus/pin maps и названия прежних layouts
- Правило выбора: только единый atomic package по `DEC-0026`; статус этого документа не принимает ни один candidate

## Как candidates выведены с нуля

Минимум два compute/RF domain уже следуют из принятых product capabilities: S3 нужен для application/native 2.4 GHz Wi-Fi/BLE, C5 — для native 2.4/5 GHz Wi-Fi, IEEE 802.15.4 и dual-path IR. Остальные `RC/RI-*` допускают три недоминируемых способа консолидации:

1. **минимум programmable domains** — deadline-sensitive external I/O остаётся на более богатом application MCU;
2. **radio-domain consolidation** — packet radios обслуживаются существующим C5 radio-domain, освобождая S3 от их deadlines;
3. **deadline isolation** — дешёвый третий controller заменяет remote real-time loops и часть glue logic.

Это не варианты «кто владеет nRF». Каждый способ назначает все compute, storage, audio, UI, radio, accessory, safety, update и recovery roles; nRF ownership получается внутри полной раскладки.

## Общий product shell для всех candidates

Следующие части одинаковы, потому что выведены из capabilities, а не из выбранного compute split.

### Fixed RF и compute blocks

- `ESP32-S3-WROOM-1U` application/native 2.4/BLE module, exact memory variant указывается candidate;
- `ESP32-C5-WROOM-1U-N8R8`, minimum silicon revision с working SDIO при использовании SDIO, native dual-band/802.15.4 и два IR RX + IR TX;
- три физически отдельных full-function nRF24 paths;
- один onboard CC1101 path;
- onboard Si4732 receive-only path;
- conditional SA518 preferred analog-voice backend с отдельным `VVOICE`, SA868S — explicit fallback stuffing profile;
- external U214/`EXT-RF14`, Unit GPS и Unit NFC profiles без onboard GNSS/LoRa/NFC frontend.

### UI/storage/audio interface envelope

До component qualification каждый candidate резервирует один и тот же function-complete envelope:

| Envelope | Физический контракт этапа 3 | Что остаётся этапу 4 |
|---|---|---|
| display | bounded SPI write path, `CS/DC`, reset-safe reset, PWM backlight; optional reads/TE не требуются для baseline | exact panel, resolution, optical/thermal/mechanical proof |
| touch | I²C-class controller с bounded polling либо source-identifiable interrupt | exact controller, cover/glove/noise HIL |
| local input | keypad/encoder-class local controller: navigation, back/menu/shortcut/text path; отдельный direct foreground PTT | exact number/form/ergonomics of ordinary controls; no safety function may depend on this controller |
| STOP/re-arm | independent hardware latch, physical STOP and separate deliberate physical re-arm/power-cycle semantics | exact switch/latch/supervisor MPN and fault-injection schematic |
| storage | removable microSD on dedicated bulk/SDMMC-class slot, exclusive-writer state | socket/card detect/ESD/exact card qualification |
| audio | ES8311 full-duplex mono I²S + slow control + hardware-default analog bypass | exact mux/amp/mic values and acoustic HIL |
| status/sense | low-speed battery/current/thermal/light inputs plus ordinary LED/buzzer control; separate physical STOP/TX indicators remain hardware-derived | exact sensors, visibility, acoustic and quiescent-power proof |

The envelope prevents a cheap display/button choice from silently deleting local operation, but does not import the legacy panel, button count or expander topology.

### Common safety/power fabric

All candidates contain a non-programmable STOP latch with asynchronous dominance over:

- S3/C5 `EN` and any third-controller reset;
- reset-safe nRF `CE` state plus STOP-switched/inhibited external-radio TX power domain;
- CC1101 TX-capable domain;
- voice `PTT`, `PD` and dedicated `VVOICE` enable/discharge;
- IR LED driver enable;
- external `VEXT_RF`/LoRa power or hardware inhibit;
- external NFC RF-field/power profile.

Release does not re-arm. A physical re-arm action starts a fresh TX-off boot. Actual-TX evidence and the physical STOP-latched indicator do not derive solely from software command state. The common 2S power tree retains separate `3V3_LOGIC/RF`, `5V_EXT`, `VVOICE≈4.0 V`, audio and switched accessory domains; exact converters/current limits are candidate-package rows, not assumed legacy circuits.

### Common update/recovery behavior

- S3 has owner-signed A/B-or-equivalent update plus native USB recovery;
- C5 has independently verified owner-signed image/rollback plus native USB and physical boot/reset access; 1-bit SDIO must not replace this recovery;
- every added programmable domain receives its own signature check, working-image rollback and independent recovery identity;
- update mode asserts global TX-off, expires all leases and cannot be exited into an armed state;
- irreversible eFuse/OTP lockdown remains a separate owner opt-in and is not required by a production image.

## Candidate `SYN-2A` — two-domain application consolidation

### Derivation

Keep the minimum two programmable domains. Place external deterministic peripherals on S3 because it has two GP-SPI controllers, two cores, mature DMA-capable I/O and direct access to application/storage, while C5 remains focused on its fixed native radios and IR.

### Complete placement

| Resource group | Physical/runtime owner |
|---|---|
| application, policy, UI, audit, vault, files | S3 |
| S3 Wi-Fi/BLE/ESP-NOW | native S3 |
| C5 2.4/5 Wi-Fi, 802.15.4, dual-path IR | native C5/local C5 task |
| 3×nRF24 + CC1101 register/FIFO/event service | S3 deterministic high-priority service on one local GP-SPI |
| nRF/CC control compression | reset-safe serial output latch with STOP-dominant output-disable and per-output safe pulls; protected IRQ aggregation plus status fan-out proof |
| display + U214 LoRa data/control | second S3 GP-SPI with priority and chunked display writes |
| U214/Unit GPS serial, U216 NFC and accessory discovery | S3 UART plus isolated/switched I²C profile manager; qualified 5 V profiles |
| ES8311, Si4732, audio DSP/record/modem | S3 I²S/I²C/DMA application domain |
| SA518/SA868 command/PTT/dead-man | S3 local UART/control service plus independent hardware STOP/PTT release |
| microSD | S3 SDMMC slot |
| S3↔C5 `CH-*` | C5 1-bit SDIO slave ↔ second S3 SDMMC slot; DAT1 interrupt, typed priority queues |

### Exact architecture choices

- S3 baseline variant: `ESP32-S3-WROOM-1U-N16R2`; 16 MB flash is retained for update/data partitions, 2 MB Quad PSRAM retains GPIO35…37 and must pass the later memory ledger.
- C5 baseline variant: `ESP32-C5-WROOM-1U-N8R8`; 8 MB flash/PSRAM with chip revision ≥1.0 when SDIO is populated.
- nRF `CSN/CE` and CC select are latch outputs, not remote GPIO calls. `OE` is STOP-dominant; when disabled, external pulls force `CE=0` and active-low `CSN/CS=1` before either MCU boots. Firmware loads and verifies the complete safe vector before enabling outputs.
- latch clock/strobe are not the selected-radio SCK. Data may share MOSI only with a separate latch clock: otherwise shifting the deassert vector would clock an unintended byte into the still-selected radio. Exact `PIN-*` reserves the independent clock/strobe rather than claiming a free shared-SPI latch.
- nRF IRQ aggregation is acceptable only because each IRQ condition is level-retained until status clear; firmware reads all three STATUS registers before clearing. Open-drain assumptions are forbidden: exact diode/logic interface and stuck-low isolation are required.

### Strength and exposed risk

- minimum firmware targets and likely lowest recurring BOM;
- no raw packet IPC between nRF/CC and application storage;
- highest S3 interrupt/bus contention: native Wi-Fi/BLE, audio, display, SD, U214, voice and four packet radios share one MCU;
- N16R2 memory sufficiency and ≤70% worst-case nRF/CC SPI occupancy are hard measurement gates;
- pin map is expected to require both output-latch and local-input expander with little direct-GPIO reserve.

## Candidate `SYN-2B` — two-domain radio-service consolidation

### Derivation

Keep two programmable domains, but move narrow-packet radio deadlines away from UI/audio/storage. C5 owns the local packet-radio bus in addition to its fixed native radios and IR; S3 retains application, UI, audio, storage, voice and external expansion.

### Complete placement

| Resource group | Physical/runtime owner |
|---|---|
| application, UI, storage, vault, USB | S3 |
| S3 Wi-Fi/BLE/ESP-NOW | native S3 |
| C5 native radio + dual IR | native C5/local C5 task |
| 3×nRF24 + CC1101 register/FIFO/event service | C5 high-priority local service on sole GP-SPI2 |
| nRF/CC control compression | C5-driven reset-safe serial latch with STOP-dominant output-disable/safe pulls; protected nRF IRQ aggregate and direct/qualified CC GDO inputs |
| display + U214 | S3 GP-SPI; bounded priority/chunking |
| U214/Unit GPS, U216 NFC, ES8311, Si4732, voice, local controls | S3 local buses/services; external I²C/5 V is isolated and profile-switched |
| microSD | S3 SDMMC slot |
| S3↔C5 control/event/bulk | 1-bit C5 SDIO slave ↔ S3 second SDMMC slot, including per-radio source/time/sequence/loss metadata |

### Exact architecture choices

- S3 and C5 memory variants remain `N16R2` and `N8R8` for the same flash/GPIO/recovery reasons as `SYN-2A`.
- C5 SDIO is dedicated hardware, leaving GP-SPI2 for nRF/CC and GPIO13/14 for native USB recovery.
- radio service never waits for S3 acknowledgment to clear FIFO, expire a TX lease or force safe state; bulk capture may drop with per-radio counters under IPC backpressure.
- as in `SYN-2A`, the control latch has an independent clock/strobe and disabled-state pulls `CE=0`, `CSN/CS=1`; neither radio SPI traffic nor a simple all-zero clear may define safety.
- C5 native Wi-Fi/802.15.4 and external packet radios share an explicit local scheduler; unsafe TX pairs remain prohibited before RF HIL.

### Strength and exposed risk

- S3 loses four packet-radio real-time loops and receives already framed events/data;
- all 2.4 GHz activity can be coordinated close to the C5 RF state, while S3 native 2.4 remains cross-domain;
- C5 is single-core, has one GP-SPI and only 21 exposed PSRAM-variant GPIO before USB/SDIO/IR/straps; map depends on safe control compression;
- simultaneous C5 native-radio load, dual IR capture and maximum admitted nRF/CC FIFO service is a hard latency/overflow gate;
- IPC carries capture bulk, so SDIO throughput/priority/liveness proof is more demanding than `SYN-2A`.

## Candidate `SYN-3A` — isolated deterministic RF/I/O domain

### Derivation

Add one low-cost controller only where `RES-0001` asks for local bounded radio/PTT service. The controller must remove glue and scheduling pressure rather than merely add GPIO. `RP2354A A4` is the first concrete comparison part because it combines 30 GPIO, 520 KB SRAM, 2 MB stacked flash, two SPI and twelve PIO state machines in 7×7 mm QFN60 with an open SDK and owner-controlled update options.

### Complete placement

| Resource group | Physical/runtime owner |
|---|---|
| application, policy, UI, files, vault, USB | S3 |
| S3 native Wi-Fi/BLE and C5 native radio/IR | respective Espressif domain |
| 3×nRF24 register/FIFO/CE/IRQ + CC1101 FIFO/GDO | RP2354A local deterministic service with direct source-identifiable controls/events |
| analog-voice UART, PTT/PD/H-L, physical PTT input and dead-man | RP2354A; audio samples remain S3/ES8311 |
| display + U214/Unit GPS + U216 NFC | S3 GP-SPI/UART and isolated/switched I²C/5 V accessory manager |
| ES8311, Si4732, DSP/record/storage | S3 I²S/I²C/SDMMC |
| S3↔C5 | C5 1-bit SDIO slave ↔ S3 SDMMC slot |
| S3↔RP2354 | local full-duplex SPI slave/service protocol plus dedicated event/lease line; framed `CH-CTL/EVT/BULK/LIVE/REC` |
| STOP | asynchronous clear/reset reaches RP2354 and its RF/PTT outputs independently of either IPC link |

### Exact architecture choices

- exact auxiliary silicon is `RP2354A A4`, never generic early RP2350; stacked flash avoids a separate QSPI flash part;
- baseline uses direct `CSN/CE/IRQ` for all three nRF and direct `CS/GDO0/GDO2` for CC1101; no GPIO expander lies in a radio deadline path;
- provisional 2 MB flash architecture reserves immutable/minimal recovery loader, two signed application slots and redundant metadata; exact slot sizes must be proven against linked A4 firmware before acceptance;
- normal update is delivered by S3 but verified and committed by RP2354 itself; dedicated USB/SWD/recovery pads remain usable when S3 is broken;
- RP2354 ROM-enforced OTP signing is optional and off in the open baseline. Software verification with owner keys must not depend on irreversible lock bits.

### Strength and exposed risk

- best isolation of nRF/CC/voice deadlines from both Espressif radio stacks and S3 display/storage/audio load;
- direct per-radio pins improve failure diagnosis and eliminate radio control latch/IRQ aggregation;
- S3/C5 pin reserve and future I/O flexibility increase;
- adds a third signed image, boot/recovery implementation, IPC protocol, active/idle power and HIL matrix;
- recurring cost is acceptable only if dated quotes plus removed latch/decoder/expander/PCB complexity make total product cost competitive, not merely MCU unit price.

## Screened alternatives, not hidden fourth decisions

### Split the three nRF radios between S3 and C5

This remains a conditional fallback, not a primary candidate. Once a grouped owner already pays three shared SPI wires plus the independent clock/strobe of a reset-safe control latch and one protected IRQ ingress, moving one radio to the other MCU does not release those shared resources. It adds another SPI service, safety/update interaction, cross-domain timestamp calibration and packet path. Its only unique benefit is aggregate SPI/load distribution.

Therefore split ownership is reopened automatically if the single-owner 10 Mbit/s nRF bus or local service latency fails the numeric gate. It is not rejected as impossible, but building it now as a fourth full map would duplicate complexity without a currently demonstrated hard-resource benefit.

### CPLD/FPGA or one controller per radio

Pure glue logic can compress selects/interrupts but does not independently drain packet FIFOs, apply protocol policy or verify updates; it is already represented by the latch/logic inside `SYN-2A/2B`. A larger programmable-logic device or three per-radio controllers adds more cost/update/test domains than `SYN-3A` without an accepted capability gain. Either re-enters only after a measured hard gate, not from legacy preference.

## Common preliminary gate matrix

`pass` here means «the candidate contains a credible mechanism to be instantiated in `PIN/BUD/PWR`», not that implementation is qualified.

| Gate | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| all 21 capability atoms placed | pass | pass | pass |
| three simultaneous full-function nRF | pass via local S3 bus | pass via local C5 bus | pass via local RP2354 service |
| C5 dual IR + native radio fixed roles | pass | pass, higher local load | pass |
| UI/audio/storage/accessory coverage | pass | pass | pass |
| local bounded radio loops | conditional S3 scheduling proof | conditional C5 scheduling proof | strongest; still needs firmware/HIL |
| native S3/C5 recovery preserved | pass via 1-bit SDIO + USB | pass via 1-bit SDIO + USB | pass via 1-bit SDIO + USB |
| every programmable target update/recovery | 2 targets | 2 targets | 3 targets; extra proof |
| independent STOP/TX-off path | topology reserved | topology reserved | topology reserved incl. RP2354 |
| exact GPIO/controller closure | next `PIN-*` | next `PIN-*` | next `PIN-*` |
| memory/throughput/power margin | next `BUD-*` | next `BUD-*` | next `BUD-*` |
| comparable dated cost | next `CST-*` | next `CST-*` | next `CST-*` |

## Why candidate-set review may close without a winner

The set spans the meaningful resource trade: minimum silicon, reuse of existing radio compute, and dedicated deterministic compute. Every candidate covers the whole product and exposes its own failure/cost burden. None inherits the old nRF owner, transport or pin map; none is promoted by narrative scoring.

The next step instantiates exact module pins, peripheral controllers, straps, recovery and direct/latch/interrupt signals for all three. A candidate that cannot produce a collision-free map is removed by hard fail, not repaired by deleting a wishlist function. `SYN-0001` therefore receives **«Проведено ревью набора candidates»**, while the architecture decision remains open and atomic.
