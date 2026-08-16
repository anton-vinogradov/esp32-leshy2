# RES-0001 — hardware-neutral resource demand model

- Статус: **Historical candidate/reference; active prerequisite superseded by `DEC-0032/FND-0041`**
- Дата: 2026-08-16
- Этап: 3, шаг 3
- Входы: reviewed `CAP-0001`, reviewed `CON-0001`
- Проверочные источники: reviewed `REQ-*`, accepted `DEC-*`
- Не входы: legacy schematic/source, прежние MCU variants, owner maps, transports, buses, GPIO и part placement

## Цель и граница

> `RB-FIX-01/02`, `RC-NATIVE-*` and several `RI-*` rows below freeze former
> S3/C5 owners. The document is therefore not hardware-neutral under the
> corrected process. Its equations and safety questions are reference evidence
> only until independently re-derived after G3.

Документ переводит capabilities и обязательные scenarios в логические ресурсы. Он задаёт то, что должна вместить каждая полная архитектура, но не назначает ресурс конкретному MCU, контроллеру или выводу.

Единица ниже — не обязательно отдельный физический pin или peripheral. Decoder, latch, wired interrupt, shared bus, DMA и дополнительный controller допустимы, если сохраняют safe reset state, source identity, deadlines, recovery и failure isolation. Совмещение считается экономией только после такого proof.

## Уже фиксированные compute/RF boundaries

| ID | Принятая граница | Что остаётся открытым |
|---|---|---|
| `RB-FIX-01` | S3 application domain и native S3 Wi-Fi/BLE | module memory variant, все внешние peripherals, storage/UI/audio placement |
| `RB-FIX-02` | C5 native 2.4/5 GHz Wi-Fi, IEEE 802.15.4 и dual-path IR | module variant, inter-domain transport и любые дополнительные peripherals |
| `RB-FIX-03` | три full-function nRF24 | один/несколько owners, отдельный controller, bus/control/event topology |
| `RB-FIX-04` | hard STOP — непрограммируемая доминирующая safety path | exact latch/supervisor/load-switch/gate tree |
| `RB-FIX-05` | S3/C5 и любой новый programmable domain обновляемы owner-signed способом | image transport, flash sizes, recovery connector и boot topology |

Других placement constraints нет. Даже если accepted component имеет привычный интерфейс, его bus instance и физический owner выводятся только в `SYN-*`.

## Классы вычислительных обязанностей

| Класс | Обязательства | Критерий размещения в будущем synthesis |
|---|---|---|
| `RC-APP` | UI, policy, session graph, files, privacy, databases, export, audit | локальная отзывчивость сохраняется при radio/storage load; secrets изолированы от untrusted import |
| `RC-NATIVE-S3` | S3 Wi-Fi/BLE controller lifecycle, coexistence, timestamped events | остаётся в S3 domain; bounded service к `RC-APP` |
| `RC-NATIVE-C5` | C5 Wi-Fi/802.15.4/IR lifecycle, scheduler and local dead-man | остаётся в C5 domain; не зависит от постоянной доступности UI link для safe-state |
| `RC-DET` | nRF/CC1101/voice/audio и иные deadline-sensitive register/FIFO/edge services | должен находиться по сторону bounded local path; remote raw GPIO over best-effort IPC не проходит |
| `RC-CODEC` | audio DMA, sample routing, AFSK/AX.25/APRS/SSTV and receive decoders | не допускает underrun/overrun без счётчика; не блокирует safety/event service |
| `RC-STORE` | bounded queues, schema/provenance, atomic metadata, encryption and removable-media ownership | producer не блокируется медленным/отсутствующим media; sensitive vault имеет least-privilege boundary |
| `RC-EXP` | exact accessory discovery, power, protocol adaptation, removal recovery | unknown profile remains off; attached backend cannot bypass base safety/policy |
| `RC-UPD` | manifest/signature/target identity/write/first-boot/rollback | для каждого programmable domain есть независимый recovery route и TX-off state |
| `RC-SAFE` | lease/dead-man/status aggregation plus independent hardware STOP | software часть может улучшать видимость, но не является единственным kill mechanism |

Классы могут жить на одном процессоре либо распределяться. Новый controller допустим только если снижает общий риск/стоимость или закрывает hard resource gap после учёта собственного flash/update/recovery/IPC/BOM.

## Логические interface primitives

| ID | Capability | Минимальный логический ресурс | Нельзя потерять при оптимизации |
|---|---|---|---|
| `RI-DISP` | UI | один bounded bulk-write display path, backlight off/dim control, reset/fault semantics | critical state readable; display traffic не блокирует STOP/radio deadlines |
| `RI-TOUCH` | UI | slow-control path плюс source-identifiable event либо bounded polling | stuck touch не создаёт action/TX и не блокирует physical controls |
| `RI-LOCAL` | UI/safety | local navigation/text events, отдельный foreground PTT input и отдельные STOP/re-arm physical semantics | phone/touch не являются единственным путём; PTT не multiplexed с обычным selection |
| `RI-SD` | storage | removable bulk block path, detect/ownership/fault state | no dual writer; slow/full/remove bounded |
| `RI-USB` | service/update/HID | native service/recovery-capable wired path with target identity | HID has no boot autorun; device recovery does not depend on working application |
| `RI-AUD` | ES8311/audio | full-duplex mono synchronous serial: clock, word-select, sample-out and sample-in; slow control; source/sink/mute safe controls | simultaneous ADC/DAC, DMA service and hardware-default analog bypass |
| `RI-N24` | 3×nRF24 | packet-register serial service; three logical selects; three independent reset-safe `CE`; source-identifiable IRQ state for all three; common time; kill and TX evidence | simultaneous three-radio PRX, independent PTX/PRX/config/FIFO/IRQ and isolation of absent/stuck radio |
| `RI-SUB` | CC1101 | packet-register serial service, independent select, bounded FIFO/event source, safe TX gate and TX evidence | RX timing/RSSI/packet modes plus independent contained TX lifecycle |
| `RI-RX` | Si4732 | slow control, reset/recovery, receive antenna/frontend and mono analog output into audio fabric | receive remains available without digital patch; TX self-desense is visible |
| `RI-VOICE` | analog voice | bounded command channel; `PTT`, power-down/enable and power-profile control; RX/TX mono analog audio; busy/squelch/TX evidence as qualified | release/dead-man/STOP force RX/off; backend identity and rail profile never guessed |
| `RI-IR` | C5 IR | two simultaneous timer/capture inputs and one deterministic carrier output with independent optical-driver inhibit | 30–60 kHz measured-carrier path, robust demodulated path and optical-off safe state |
| `RI-GNSS` | Unit GPS/U214 | selected bidirectional serial profile, powered attachment identity/removal state and timestamps | exactly one backend; stale/remove invalidates dependent result |
| `RI-RF14` | U214/later LoRa | packet-radio command/data/event resources, GNSS serial where present, reset/busy/IRQ identity, switched power and TX inhibit | one exact backend, regional profile, removal disarm, no blanket connector compatibility |
| `RI-NFC` | U216-class | 5 V accessory power profile, 3.3 V-safe bounded control/event path, attachment identity and RF-field inhibit | unknown/removal/fault = RF off; sensitive state protected |
| `RI-IPC` | cross-domain | typed control, event and bulk-data classes; monotonic time correlation; liveness/reset/version and lease cancellation | no unbounded message, stale owner or TX survival after link loss |
| `RI-REC` | each programmable domain | independent reset/boot/recovery entry plus observable target identity | a broken peer/application cannot prevent reflashing or safe boot |
| `RI-STOP` | all TX | asynchronous latch input, physical re-arm, reset dominance for S3/C5, separate inhibit/cut reach to external TX domains and independent visible state | no firmware/I²C/expander dependency in the kill path |

`RI-*` counts logical requirements. Physical pin cost is calculated later for each implementation: direct signals, decoder/latch, interrupt aggregation and extra controller are compared on the same semantics.

## Capability-to-resource demand

| Capability atoms | Compute classes | Interface/resource pressure | Mandatory concurrent scenario |
|---|---|---|---|
| `CA-CORE/UI` | `RC-APP/STORE/SAFE` | `RI-DISP/TOUCH/LOCAL`, nonvolatile config, monotonic clock | every `CS-*` foreground or fault screen |
| `CA-STORE/USB/UPD` | `RC-STORE/UPD/APP` | `RI-SD/USB/REC/IPC`, two-image or equivalent working-image rollback capacity | `CS-02/03/12` |
| `CA-W24/BLE` | `RC-NATIVE-S3/APP` | S3 RF/antenna domain, bounded event/capture queues | `CS-05/11`; internal time-sharing |
| `CA-W5/154/IR` | `RC-NATIVE-C5/DET` | C5 RF/antenna plus `RI-IR/IPC/REC` | `CS-05/08/11/12` |
| `CA-N24` | `RC-DET/STORE/SAFE` | `RI-N24`, three RF/antenna/power paths, calibration identity | `CS-04/11`; 3×PRX mandatory |
| `CA-SUB` | `RC-DET/STORE/SAFE` | `RI-SUB`, qualified RF/filter/antenna path | `CS-05/11` |
| `CA-RX` | `RC-DET/CODEC` | `RI-RX/AUD`, receive RF and analog routing | `CS-06` |
| `CA-VOICE` | `RC-DET/CODEC/SAFE` | `RI-VOICE/AUD`, dedicated voice rail and RF/antenna path | `CS-07/11` |
| `CA-AUDIO` | `RC-CODEC/STORE` | `RI-AUD`, DMA/buffers and fail-safe analog selectors | `CS-06/07` |
| `CA-GNSS/LORA/EXP` | `RC-EXP/STORE/SAFE` | `RI-GNSS/RF14/STOP`, switched profile power | `CS-05/09/11/12` |
| `CA-NFC/EXP` | `RC-EXP/STORE/SAFE` | `RI-NFC/STOP`, protected records | `CS-10/12` |
| `CA-SAFE/PWR` | `RC-SAFE` plus hardware | `RI-STOP`, per-domain default-off/inhibit/evidence, current/thermal state | all scenarios |

## Timing and event classes

| Class | Work | Required property; exact number deferred to qualification |
|---|---|---|
| `RT-HARD` | hardware STOP, TX inhibit, voice PTT release path | asynchronous or independently bounded in hardware; cannot wait for task scheduling or IPC |
| `RT-EDGE` | two IR capture paths, IR carrier generation | hardware timer/capture/PWM-class service with simultaneous RX and documented jitter/resolution proof |
| `RT-RADIO` | nRF IRQ/FIFO/CE, CC1101 FIFO/events, voice state | local bounded interrupt/event latency and service time at maximum accepted profile |
| `RT-AUDIO` | full-duplex mono samples | continuous DMA-class servicing; storage/UI backpressure cannot starve clocks |
| `RT-NATIVE` | S3/C5 native radio stacks | vendor-controller deadlines isolated from bulk application work; time-sharing state exported |
| `RT-BULK` | display, SD, USB export, captures | preemptible/chunked or independently controlled; may degrade before `RT-*` deadlines |
| `RT-SLOW` | control/config/accessory discovery | timeout/retry/recovery and stuck-bus isolation; never carries sole emergency action |

Any architecture that puts an `RT-HARD`, `RT-EDGE`, `RT-RADIO` or `RT-AUDIO` loop behind an unbounded peer link fails before pin mapping.

## Hardware-neutral memory and throughput envelopes

These are sizing equations, not product throughput claims. A synthesis must substitute exact display/profile/driver measurements and retain margin.

| Demand | Lower-bound/stress equation | Interpretation |
|---|---|---|
| display working set | `W × H × bytes_per_pixel × buffered_fraction` plus dirty/tile metadata | full framebuffer is optional; a tiled implementation must still meet UI latency and never monopolize shared bulk path |
| mono audio one direction | `sample_rate × bytes_per_sample`; reference stress point `48 kHz × 2 B = 96 kB/s` | chosen as an architecture sizing point, not a promise of audio bandwidth/fidelity |
| simultaneous audio ADC+DAC | `2 × one_direction = 192 kB/s` at the reference point, before container/metadata overhead | local DMA queues and codec clocks sized independently from SD stalls |
| three nRF upper transport stress | `3 × 2 Mbit/s ÷ 8 = 750 kB/s` before packet/register/SPI overhead | conservative service ceiling for placement comparison; not a sustained lossless-air capture promise |
| nRF queue | `3 × admitted_rate × worst_service_gap` plus event metadata | each radio retains independent overflow/loss counters and state |
| native Wi-Fi/BLE/802.15.4 capture | measured peak callback/event rate × admitted service gap | excess is filtered/dropped with counters; no lossless claim is inferred from link rate |
| storage write | sum of admitted persistent streams plus atomic metadata/encryption overhead and recovery margin | exact SD result must exceed scenario demand under display/radio contention or session degrades visibly |
| update flash | working image + candidate image + boot/recovery/manifest state for each target | exact partitioning may differ, but failed first boot cannot destroy the working route |
| protected records | keys/secrets plus bounded sensitive capture indexes and crypto workspace | capacity and access control measured independently from removable bulk storage |

No queue is dimensioned as infinite. Every producer has an admission policy, maximum record/frame size, high-water response, loss counter and recovery state. PSRAM may hold bulk/UI/capture data only if deadlines and secret policy survive its absence/fault; hard safety state never depends solely on PSRAM.

## Transport classes, not transport choices

The final S3↔C5/extra-controller topology must provide:

| Channel | Traffic | Required semantics |
|---|---|---|
| `CH-CTL` | commands/config/arming/cancel | typed, authenticated where needed, idempotent, bounded, priority-aware |
| `CH-EVT` | IRQ-derived events/state/fault/TX evidence | source/time/sequence/overflow and priority; cannot be starved by bulk |
| `CH-BULK` | capture/audio/update blocks | framed, checksummed, flow-controlled and abortable; loss/partial state explicit |
| `CH-LIVE` | heartbeat/version/clock correlation/lease | independent enough to detect wedged bulk path and expire TX locally |
| `CH-REC` | recovery/update entry | available when normal application protocol or peer is broken |

A single physical link may carry `CH-*` only with priority, bounded framing and recovery proof. Separate links are not automatically better: their pins, power, boot straps and fault coupling count against the same package.

## Power and safety resource classes

| Domain | Accepted demand | Synthesis obligation |
|---|---|---|
| `PW-BAT` | accepted 2S source, charge/state/sleep/brownout | exact worst-case scenario peak, protection, efficiency and shutdown behavior |
| `PW-LOGIC` | S3/C5, digital logic, storage and low-voltage radios | rail transient/sequencing/isolation; reset never produces TX pulse |
| `PW-VOICE` | dedicated 4.0 V SA518-class rail from `DEC-0025` | separate enable/discharge/current/thermal proof; fallback has explicit stuffing/profile |
| `PW-EXT5` | qualified NFC/Grove-class 5 V accessory | current limit, wrong-profile isolation, reverse/backfeed and removal behavior |
| `PW-EXT-RF` | U214/later radio accessory | profile-switched supply plus hardware TX inhibit/cut reachable by STOP |
| `PW-AUDIO` | codec/analog routing/amp/mic | pop/click/mute/default-bypass and RF-noise proof |
| `PW-RF` | nRF/CC1101 and any external PA/LNA | per-path decoupling/transient/thermal/default-off; shared rail allowed only if one fault cannot defeat required independent state |

Required power scenarios are not «all transmitters at maximum». They are the legal/accepted concurrency set from `CON-0001`: three-radio nRF receive hunt; voice TX with local UI/audio/safety; U214 TX with its GNSS service; one qualified contained TX pair; receive/record/wardrive sessions; boot/update/recovery. Simultaneous unqualified TX cannot be used to inflate cost, while an actually accepted peak cannot be omitted to save it.

## Independent safe-state/evidence obligations

The architecture must expose separate controllable or hardware-dominant safe-state reach to:

- S3 and C5 reset/enable domains;
- three nRF `CE` states plus their STOP-reachable TX-capable power/inhibit domain;
- CC1101 TX-capable domain;
- analog voice PTT and voice power domain;
- IR optical driver;
- attached LoRa/RF accessory power/inhibit;
- external NFC RF field path when attached.

Actual-TX evidence is a separate signal class from command/enable. Exact detector topology is chosen per path; lack of a qualified detector is shown as `unknown/unavailable`, never synthesized from software state. Critical STOP latch indication has an independent physical path.

## Pin/resource optimization rules for later synthesis

1. First allocate direct/dedicated resources required by `RT-HARD`, `RT-EDGE`, recovery and boot safety.
2. Then allocate `RT-RADIO/RT-AUDIO` local owners and bounded event paths.
3. Only then share `RT-BULK/RT-SLOW` buses or compress selects/events through decoder, latch, expander or extra controller.
4. A shared signal passes only if all attached devices have compatible reset state, voltage, ownership, timing and failure behavior.
5. Boot strapping, flash/PSRAM use, native USB, crystal/RF pins and module-reserved pads are removed before counting generic GPIO.
6. Connector signals count together with power, ground, orientation, retention, ESD, backfeed, keying and removal detection; a header label alone is not compatibility.
7. Each candidate publishes used/free/reserved/strap/recovery pins and peripheral instances, not just a total GPIO number.
8. A pin-saving circuit includes its BOM, board area, quiescent power, propagation, safe defaults, driver/update burden and stuck-fault behavior.

## Zero-loss cost ledger required from every candidate

Each `SYN-*` separates:

- base-board recurring BOM and assembly;
- optional accessory cost paid only when attached;
- one-time engineering/qualification/HIL cost;
- area/layer/connector/enclosure cost;
- software/update/recovery cost of every added programmable domain;
- savings from removed duplicate resource;
- any changed margin, lifecycle or second-source risk.

Removing one of three radios, onboard audio, hard STOP, external-profile electrical support, independent recovery, safe defaults, actual-TX evidence or required HIL is product loss, not saving. Replacing direct GPIO with shared logic or a low-cost controller may be zero-loss, but only when the complete ledger and fault proof are better.

## Gate to full synthesis

Every complete `SYN-*` must now instantiate:

1. all fixed boundaries `RB-FIX-*` and all logical `RI-*` obligations;
2. compute placement for every `RC-*` and a local owner for each real-time loop;
3. exact memory/flash/queue/storage equations with measured or sourced substitutions;
4. exact interface instances and physical signal count, including recovery/strap/reserved pins;
5. power peaks for every mandatory `CS-*` scenario and safe-state reach for every TX domain;
6. typed `CH-*` transport behavior and failure recovery;
7. base/accessory/NRE cost ledger and quantified headroom;
8. no inherited legacy net or part unless it wins the same comparison as a new candidate.

`RES-0001` maps every capability and scenario to resource classes without choosing placement. Step 3 therefore receives **«Проведено ревью»**. Exact quantitative component facts are collected separately for each synthesis so that the package compares realizable architectures rather than narrative pin counts.
