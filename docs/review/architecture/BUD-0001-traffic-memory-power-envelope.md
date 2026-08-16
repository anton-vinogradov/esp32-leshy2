# BUD-0001 — numeric traffic, memory and power envelope

- Статус: **Traffic и memory — проведено ревью; power — в работе до решения `IMP-0023`**
- Дата: 2026-08-16
- Этап: 3 — системная архитектура и владение
- Входы: `DM-0001`, `PIN-0001`, `DEC-0023`, `DEC-0024`, exact-source ceilings
- Назначение: один numeric input для `LAY-S3`, `LAY-C5` и `LAY-BAL`

## Правила чисел

- `MB/s` означает decimal bytes/s; `KiB`/`MiB` — binary memory.
- Числа ниже являются acceptance floors/caps для architecture, а не заявлением о производительности legacy artifact.
- Теоретический RF bitrate не является гарантированным capture goodput. Данные сверх принятого ingress cap могут быть отброшены только с явным counter, timestamp gap и degraded/unknown state.
- Каждый общий bus/link обязан иметь не менее 30% measured payload headroom после framing, turnaround, arbitration и error recovery; средняя occupancy за любое окно 100 ms не превышает 70%.
- Layout не может уменьшить этот envelope, чтобы поместиться. Изменение требует change review `DM-0001`.

## Traffic and latency envelope

| Domain | Derived demand | Numeric acceptance boundary |
|---|---:|---|
| 320×480 RGB565 display | one full frame = `320×480×2 = 307,200 B`; 10 full-frame equivalents/s = 3.072 MB/s | measured display payload ≥3.2 MB/s; one full-frame transfer ≤100 ms; ordinary input-to-visible feedback p95 ≤100 ms, max ≤250 ms in `SCN-01..06` |
| Shared-bus transaction | display and storage must not monopolize a radio service bus | non-preemptible chunk ≤4 KiB and ≤1 ms; longer work is split/yielded |
| 3×nRF24 local service | three 2 Mbit/s on-air ceilings sum to 0.75 MB/s before SPI command/status overhead | reserve ≥0.90 MB/s owner-local SPI payload; IRQ-to-first-status/read p99 ≤250 µs, max ≤400 µs; FIFO overflow remains counted, never hidden as lossless |
| CC1101 | 500 kBaud ceiling = 62.5 kB/s before framing | reserve ≥0.10 MB/s; FIFO service p99 ≤0.5 ms, max ≤1 ms at the qualified maximum-rate fixture |
| U214/SX1262 | accepted backend ceiling up to 300 kbit/s = 37.5 kB/s | reserve ≥0.10 MB/s SPI payload and event latency p99 ≤2 ms while attached |
| ES8311 I²S | 48 ksample/s × 16-bit × mono × two directions = 192 kB/s | continuous 0.192 MB/s DMA; one recorded mono track = 0.096 MB/s; no unreported sample gap in `SCN-03/04` |
| S3↔C5 bulk | filtered capture/update/crash/event traffic; no lossless Wi-Fi-monitor promise | simultaneous measured payload goodput ≥1.5 MB/s C5→S3 and ≥0.5 MB/s S3→C5; 2.0 MB/s C5 burst for 500 ms; control p99 ≤10 ms, max ≤20 ms under bulk |
| TX lease/dead-man over IPC | software safety below independent `DEC-0024` STOP | missing heartbeat/link cancels remote lease within 100 ms; no bulk queue can delay cancellation |
| microSD | C5 ingress cap plus audio/log/UI metadata | ≥2.0 MB/s sustained write for 10 min and ≥4.0 MB/s read on every qualified card profile; 512 KiB-equivalent bounded staging across owner pools; stalls/drop/recovery visible |
| UART accessories | GNSS 115200 and SA51x 9600-class control are low bandwidth | receive queue absorbs ≥250 ms wire time; no shared UART reconfiguration while another active profile owns it |

The display figure is a bus budget, not a promise of 10 animation frames/s everywhere. Dirty rectangles, rows and DMA may exceed the visible target efficiently, but a layout must also survive the full-frame acceptance case.

## Memory envelope

### S3 external PSRAM working set

The same pool is reused across mutually exclusive scenarios. The largest mandatory scenario, not the sum of every optional profile, determines the module floor.

| Pool | Reserved peak |
|---|---:|
| UI composition: one 300 KiB framebuffer plus two bounded stripes/metadata | 384 KiB |
| common event/state/cache and bounded asset window | 128 KiB |
| `SCN-02` radio/IPC capture ring | 512 KiB |
| `SCN-02` SD stall ring | 384 KiB |
| `SCN-02` parser/index scratch | 128 KiB |
| **Largest simultaneous S3 PSRAM working set** | **1,536 KiB** |
| Required free/fragmentation margin at that peak | **≥384 KiB and ≥20% of usable PSRAM, whichever is larger** |

This leaves N8R2 as a candidate only if the real build proves at least 1,920 KiB usable PSRAM under `SCN-02`, with no allocation failure. N8R8 is not selected automatically because `PIN-0001/FND-0029` show that it removes GPIO35–37. If N8R2 misses the measured floor, every affected layout is recalculated; features are not removed.

Other S3 overlay ceilings:

- audio record/play/DSP overlay ≤704 KiB including ≥192 KiB capture-stall buffering;
- update/IPC/crypto overlay ≤768 KiB, with firmware image streamed to inactive flash rather than duplicated wholly in RAM;
- at mandatory-scenario start, free internal DMA-capable SRAM ≥96 KiB and largest DMA-capable block ≥32 KiB;
- stack high-water marks retain ≥25% per-task margin after 30 min scenario soak.

### C5 memory

- N8R8 exact target supplies 8 MiB external PSRAM; radio/capture/IPC working allocation is capped at 2 MiB for the frozen baseline.
- At peak, free external PSRAM remains ≥4 MiB so optional protocol adapters and diagnostics do not silently consume all recovery margin.
- Free internal DMA-capable SRAM at scenario start is ≥64 KiB with largest block ≥16 KiB; IR RMT and radio driver DMA cannot depend on pageable/external memory where the exact driver forbids it.
- Buffer exhaustion applies documented backpressure/drop accounting; it cannot extend TX lease or block IR/STOP handling.

### Flash/update

- Each MCU keeps two independently verifiable application slots plus bootloader/partition table/NVS/recovery metadata.
- Signed application image cap is 3.0 MiB per slot on the current 8 MiB flash class. A larger build changes the exact module/partition decision; it cannot delete rollback.
- Update download is streamed and hashed; no requirement assumes an extra full image in PSRAM.
- Crash/fault metadata reserves at least 256 KiB total per MCU design, with secret redaction and bounded overwrite policy.

## Provisional power envelope

These are conservative architecture reservations. Exact component min/typ/max and allowed simultaneity are rechecked at stage 4. `VVOICE` remains unresolved because `FND-0030/IMP-0023` found that legacy 5 V overdrives the accepted SA518 1 W profile.

| Domain | Evidence/reservation | Provisional rail demand |
|---|---|---:|
| S3 | official 340 mA RF peak; design reserve | 3.3 V / 0.50 A |
| C5 | official 5 GHz RF peak up to 381 mA; design reserve | 3.3 V / 0.50 A |
| 3× exact nRF24 PA/LNA candidate | bare IC current is not a PA-module bound; connector/domain cap | 3.3 V / 0.25 A each = 0.75 A |
| CC1101 | 34.2 mA typical max-power TX; rounded reserve | 3.3 V / 0.05 A |
| display logic, microSD, codec/Si4732, control and margin | class reservation until exact BOM | 3.3 V / 0.40 A |
| **3.3 V permitted/fault-overlap load** | sum | **2.20 A; rail rating candidate ≥3.0 A** |
| U214 LoRa+GNSS | documented 155.03 mA max-power TX+GNSS; rounded | 5 V / 0.20 A |
| external Unit GPS v1.1 | documented 31.64 mA; mutually exclusive with U214 GNSS backend | 5 V / 0.05 A |
| U216/generic qualified Unit | provisional current-limited port cap pending exact revision | 5 V / 0.30 A |
| backlight/audio/accessory overhead | class reservation until exact panel/driver | 5 V / 0.40 A |
| **5 V non-voice load** | allowed attached-profile combination | **≤0.90 A; rail rating candidate ≥1.5 A continuous / 2.0 A transient** |
| SA518 | 4.0 V table: up to 0.90 A; 5 V table: up to 1.07 A and >1 W | **pending `IMP-0023`; recommended BAT-fed 4.0 V buck, ≥1.25 A continuous / 1.5 A transient** |

Power acceptance common to either final voice choice:

- regulator/switch/connector continuous load ≤80% of qualified rating at 40 °C ambient;
- pack/protection/master path candidate floor ≥4 A continuous and ≥6 A for 100 ms until exact scenario+BOM calculation replaces the class cap;
- fault overlap of normally mutually excluded transmitters must not brown out either MCU before `DEC-0024` STOP acts;
- rail transient droop remains within ±5% and above every exact module minimum; no reset may leave a TX path active;
- charging plus active load stays within negotiated USB/input limit by reducing or pausing charge current, never by silently relaxing the device safety margin;
- power/thermal HIL logs rail min/max, current, battery voltage, regulator and module temperature for `SCN-01..08` at 25 °C and 40 °C ambient.

## Primary sources

- [ESP32-S3 Series datasheet v2.2](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)
- [ESP32-C5 Series datasheet v1.4](https://documentation.espressif.com/esp32-c5_datasheet_en.pdf)
- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
- [TI CC1101 datasheet Rev. I](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [NiceRF SA518 v1.1 datasheet](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
- [M5Stack Cap LoRa868/U214 specifications](https://docs.m5stack.com/en/cap/Cap_LoRa868)
- [M5Stack Unit GPS v1.1 specifications](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [ST7796S controller datasheet](https://www.buydisplay.com/download/ic/ST7796S.pdf)

## Completion gate

- [x] display/radio/audio/IPC/storage traffic and latency envelopes;
- [x] S3/C5 PSRAM, internal-DMA and flash/update envelopes;
- [x] conservative power class reservations and rail margin rules;
- [ ] accepted voice-rail topology and resulting final 5 V/voice/pack calculation (`IMP-0023`).
