# BUD-0002 — zero-based memory and traffic budget

- Статус: **Проведено ревью числовой модели; hardware qualification gates открыты**
- Дата: 2026-08-16
- Этап: 3, шаг 5b
- Входы: reviewed `CAP-0001`, `CON-0001`, `RES-0001`, `SRC-0001`, `SYN-0001`, `PIN-0002`
- Scope: одинаковые capability/scenario ceilings для `SYN-2A`, `SYN-2B`, `SYN-3A`
- Не входы: archived `BUD-0001`, legacy owners/queues/throughput claims и прежние layouts

> **Current correction:** `FND-0051` proves that the display row cannot qualify
> either verified low-cost ST7796S reference: its datasheet ceiling is 1.89
> MB/s before overhead, below both 3.072 MB/s demand and 4.5 MB/s gate. This
> historical arithmetic remains review evidence for the superseded candidates.
> `DEC-0043` replaces this display subsection with task/dirty-region acceptance;
> none of the full-frame numbers below is an active G2F prerequisite.

## Метод и единицы

Бюджет заново выведен из принятых сценариев и физических интерфейсных потолков. `kB/s` означает 1000 bytes/s, `KiB` — 1024 bytes. Datasheet maximum не является обещанием приложения; гарантией становится только измеренный admitted profile с bounded latency, drop/overflow counters и явным состоянием деградации.

Для разделяемого ресурса действуют две разные границы:

1. `absolute ceiling` — верхняя оценка, нужная, чтобы не выдать физически невозможное за гарантированное;
2. `admitted guarantee` — нагрузка, которую scheduler вправе принять как гарантированную после HIL.

Ни одна функция не удаляется при превышении admitted guarantee: режим остаётся доступным, но новая session получает честный `unsupported-at-requested-rate/degraded`, либо данные теряются только с точным счётчиком. Скрытое снижение частоты наблюдения запрещено.

## Сценарные overlay, а не сумма всех максимумов

`CON-0001` не требует одновременно держать максимальные radio-capture, audio/decode и update/export working sets. Поэтому память резервируется как common resident plane плюс один максимальный foreground overlay.

| Overlay | Сценарии | Что одновременно обязательно |
|---|---|---|
| `OV-RADIO` | `CS-04/05/09/11` | selected radio producers, timestamps/loss, UI, bounded storage queue, safety |
| `OV-AUDIO` | `CS-06/07` | mono full-duplex codec path, decode/modem working set, UI, storage, safety |
| `OV-SERVICE` | `CS-02/03` | signed image or bounded import/export parser, durable progress, UI, TX-off |

Попытка запустить два максимальных overlay одновременно проходит admission заново. Это не legacy-ограничение и не скрытая потеря: ни один reviewed scenario такой суммы не требует.

## S3 `N16R2` PSRAM budget

`PIN-0002` сохраняет GPIO35…37 ценой 2 MiB Quad PSRAM. Достаточность проверяется не номиналом, а runtime allocator floor.

### Common resident ceiling

| Consumer | Ceiling, KiB | Содержимое |
|---|---:|---|
| UI/draw/assets | 256 | partial/tiled renderer, screen state and bounded decoded assets; full double framebuffer не предполагается |
| producer/event queues | 256 | metadata, timestamps, ordinary background capture and loss accounting |
| audio base | 128 | codec rings/state; DMA descriptors/data remain internal-capable |
| inter-domain links | 128 | C5 SDIO and, only for `SYN-3A`, RP framing/control queues |
| filesystem/system state | 128 | VFS/log/config/UI service objects, not file cache without bound |
| **Resident total** | **896** | hard post-initialization ceiling |

### Foreground overlay ceiling

| Overlay | Ceiling, KiB | Reason |
|---|---:|---|
| `OV-RADIO` | 512 | ≥250 ms queue at the 1.5 MB/s storage-admission boundary plus framing margin |
| `OV-AUDIO` | 384 | decoder/modem/export workspace in addition to the resident audio ring |
| `OV-SERVICE` | 384 | streaming signature/decompression/import; complete image is never staged in PSRAM |

Acceptance equation for the worst overlay:

`896 KiB resident + 512 KiB overlay + 384 KiB allocator/fragmentation reserve = 1792 KiB`.

Therefore every S3 build must report at least `1792 KiB` usable PSRAM after boot-time reservations; resident allocations must remain ≤`896 KiB`, a foreground overlay ≤`512 KiB`, and the minimum free/largest-allocation probes must demonstrate the reserved margin during `CS-12`. If the floor fails, switching silently to N16R8 is forbidden because it removes three mapped GPIO. The remedy is allocation reduction or a new complete `PIN/SYN` candidate.

### Historical display envelope — superseded by `DEC-0043`

This former candidate used the following synthetic `480×320 RGB565` envelope:

- one full image: `480 × 320 × 2 = 307,200 B`;
- 10 full-frame-equivalents/s: `3.072 MB/s` pixel payload;
- baseline renderer uses ≤`256 KiB` tiled/partial buffers and therefore cannot depend on a full 307,200-byte framebuffer;
- a future panel above this envelope reopens `BUD/PIN`, rather than silently consuming reserve.

The active contract no longer requires periodic full frames. It uses dirty/tiled
regions, critical/menu first visible response `≤100 ms`, visible waterfall
coalescing/drop evidence and preemptible bulk transfers. When U214 shares the
bus, the uninterrupted pixel quantum is `≤256 B` and measured accessory
IRQ-to-first-transfer remains `≤250 µs`.

### Internal DMA-capable memory gate

PSRAM does not replace every controller/DMA allocation. At the worst admitted session the S3 must retain a measured `192 KiB` internal DMA-capable pool before starting foreground I/O. The planned simultaneous ceiling is:

| Consumer | KiB ceiling |
|---|---:|
| I²S RX/TX DMA | 32 |
| microSD SDMMC descriptors/data | 24 |
| C5 SDIO descriptors/data | 24 |
| display/U214 SPI | 24 |
| RF SPI (`2A`) or RP IPC (`3A`) | 24 |
| USB endpoints/service | 16 |
| safety/control/emergency log | 16 |
| **Allocated ceiling / uncommitted reserve** | **160 / 32** |

`SYN-2B` may use the unused 24 KiB line as additional reserve; it may not spend it in the comparison to appear faster.

## C5 memory and image budget

All candidates use `ESP32-C5-WROOM-1U-N8R8`.

- Runtime HIL must expose ≥`7168 KiB` usable PSRAM.
- Common native-radio/IR/link resident allocations are limited to `2048 KiB`.
- `SYN-2B` packet-radio capture/admission queues may use at most another `2048 KiB`; `SYN-2A` U214/GNSS services remain within the same ceiling.
- One temporary parser/export/coexistence overlay is limited to `1024 KiB`, leaving ≥`2048 KiB` nominal runtime/fragmentation margin at the measured floor.
- Internal-memory HIL, not PSRAM arithmetic, must prove zero unexplained IR edge loss and bounded radio/link service under native C5 stress.

The 8 MiB C5 flash envelope is `1 MiB` boot/partition/NVS/recovery + `2 × 3 MiB` owner-signed application slots + `1 MiB` diagnostics/reserve. Update transfer is streamed and verified; no full-image RAM staging is required.

The 16 MiB S3 flash must independently retain two working images. Stage 7 may adjust exact partition sizes, but may not reduce the two-image rollback contract or consume the PSRAM reserve to do so.

## `SYN-3A` RP2354A budget

The third domain is admissible only as a complete update/recovery target, not as a GPIO expander.

### 520 KiB SRAM

| Class | Ceiling, KiB |
|---|---:|
| runtime, stacks, radio/voice state | 256 |
| active packet/event overlay | 96 |
| SPI0/SPI1 DMA/link buffers | 64 |
| **Used / guard** | **416 / 104** |

The guard covers stack high-water uncertainty, fault injection and allocator fragmentation. A firmware build that needs more does not borrow S3 memory across IPC for a deadline path.

### 2 MiB stacked flash

| Region | KiB |
|---|---:|
| first-stage recovery and verifier | 128 |
| application A | 768 |
| application B | 768 |
| version/key/rollback metadata | 64 |
| factory/HIL diagnostics | 64 |
| unallocated growth reserve | 256 |
| **Total** | **2048** |

Both slots are owner-signed and independently boot-tested. Optional ROM enforcement remains an owner choice; baseline openness and physical USB/SWD/RUN recovery are preserved.

## Common packet-radio SPI calculation

Nordic specifies nRF24 SPI up to 10 Mbit/s and 2 Mbit/s maximum air data rate. Three independent radios therefore have a deliberately loose absolute payload upper bound of:

`3 × 2 Mbit/s ÷ 8 = 750 kB/s`.

This overestimates useful payload because it ignores preamble/address/control/CRC and radio timing, but is valid for bus impossibility screening. A maximum 32-byte dynamic payload requires command/width/status/clear service; the architecture reserves a `1.20×` SPI byte factor. CC1101's documented 600 kbit/s air ceiling gives `75 kB/s`; its SPI/FIFO factor is conservatively `1.25×`.

| Load case | Bus bytes/s | 10 Mbit/s bus occupancy | Result |
|---|---:|---:|---|
| impossible-screen: nRF absolute 750 + CC 75 kB/s | `750×1.20 + 75×1.25 = 993.75 kB/s` | 79.5% | not an admitted lossless promise |
| `CS-04` guarantee: 3×nRF, 200 kB/s payload each | `600×1.20 = 720 kB/s` | 57.6% | passes ≤70% bus gate |
| mixed selected producers: nRF 450 + CC 60 kB/s | `450×1.20 + 60×1.25 = 615 kB/s` | 49.2% | passes |

The `CS-04` guarantee means three concurrent full-function PRX instances, each with independent mode/channel/rate/FIFO/IRQ and an admitted sustained payload of `200 kB/s`. It does **not** redefine RPD as RSSI and does not claim lossless capture of three theoretical air maxima. A native mode remains selectable above the guarantee, but the request/result contains admitted rate, gaps and exact overflow/drop counters.

The common-bus acceptance test is:

- p99.999 IRQ-to-first-transaction ≤`100 µs`, observed maximum ≤`200 µs` at admitted load;
- drain three maximum nRF payloads from one FIFO in ≤`150 µs` after service begins;
- CC FIFO service begins ≤`250 µs` and completes ≤`500 µs` at its mixed admitted load;
- 30-minute `CS-04` stress has no unexplained loss; injected/real FIFO overflow increments the correct source counter;
- latch candidates include latch update and IRQ fan-out time in the same measurement; RP direct pins receive no synthetic discount.

All three current candidates share one 10 Mbit/s nRF/CC data bus, so none can claim the 79.5% absolute-screen case. Split ownership is reopened automatically, without a new product-scope decision, if the accepted 600 kB/s nRF target or latency gate fails. This is the exact trigger promised by `SYN-0001`.

## Display, audio, storage and inter-domain traffic

| Path | Derived demand | Acceptance gate |
|---|---|---|
| display SPI — historical | 3.072 MB/s at the former stage-3 panel envelope | superseded by `DEC-0043`; task HIL, `≤256 B` shared-bus quantum and U214 wait `≤250 µs` are active |
| I²S audio | `48,000 × 2 B × 2 directions = 192 kB/s` | continuous full-duplex with zero unexplained DMA loss; audio gaps counted |
| microSD | admitted aggregate record ≤1.5 MB/s | ≥4.0 MB/s sustained on qualified card; survive a measured 250 ms write stall with bounded ≥512 KiB queue |
| S3↔C5 1-bit SDIO | `2.5 MB/s` raw at 20 MHz, not claimed as application rate | ≥1.5 MB/s framed payload; control/event priority; ≤2 ms control RTT; link loss visible and TX leases expire |
| S3↔RP SPI (`3A`) | `2.5 MB/s` raw at 20 MHz, not claimed as application rate | ≥1.5 MB/s framed payload; alert-to-read ≤250 µs; malformed/stalled peer cannot hold TX lease |
| Unit GPS | documented 115200 bit/s default, up to 10 Hz navigation | negligible in bulk budget; epoch age/removal integrity remains mandatory |

At the 70% payload-occupancy policy, either 1.5 MB/s qualified IPC link admits up to `1.05 MB/s`, above the 600 kB/s nRF guarantee plus metadata. `SYN-2B` and `SYN-3A` therefore pass the arithmetic IPC gate; only HIL latency/liveness remains. `SYN-2A` sends lower-duty U214/GNSS traffic over C5 SDIO and retains its packet payload locally on S3.

The former display-sharing arithmetic is not a current pass: at the ST7796S
datasheet ceiling, a 1 KiB transfer alone takes about 541 µs and cannot bound a
250 µs U214 wait. `DEC-0043` therefore requires scenario HIL with a `≤256 B`
preemption quantum. `SYN-2A`'s historical dedicated display path receives no
score for capacity it does not need.

## Candidate result after arithmetic gates

| Gate | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| S3 PSRAM/flash | pass by same budget | pass | pass |
| C5 PSRAM/flash | pass by same budget | pass; largest local radio overlay | pass; largest margin |
| RP memory/update | n/a | n/a | pass on paper; third signed target required |
| nRF/CC bus arithmetic | pass admitted / fail absolute-lossless screen | same | same |
| local radio deadline risk | S3 native radio/UI/audio/SD stress HIL | highest: single-core C5 native+IR+packet HIL | lowest scheduling risk; still HIL-required |
| bulk IPC arithmetic | low-duty pass | pass at admitted 600 kB/s | pass at admitted 600 kB/s |
| display/U214 sharing | historical dedicated path | task HIL required | task HIL required |

No candidate is removed by memory or admitted-throughput arithmetic. The calculation does, however, prohibit a false claim common to all three: a single 10 Mbit/s bus cannot be advertised as guaranteed lossless capture of the simultaneous theoretical maxima of 3×nRF24 plus CC1101 while retaining 30% service headroom.

## Qualification matrix and closure

| Test ID | Required evidence | Candidate affected |
|---|---|---|
| `HIL-BUD-01` | S3 usable/resident/overlay/internal-DMA high-water measurements | all |
| `HIL-BUD-02` | C5 PSRAM/internal-memory and fault-storm high-water measurements | all; strongest load in `2B` |
| `HIL-BUD-03` | 30-minute three-radio PRX service, per-source latency/loss/overflow | all |
| `HIL-BUD-04` | CC mixed-load FIFO deadlines and nRF coexistence | all |
| `HIL-BUD-05` | SDIO throughput/control RTT/link-loss/lease expiry | all; bulk load in `2B` |
| `HIL-BUD-06` | critical/menu/waterfall scenario load + U214 IRQ arbitration at `≤256 B` display quantum; publish full-redraw result | `2B/3A` |
| `HIL-BUD-07` | microSD 1.5 MB/s record with injected 250 ms stalls and audio | all |
| `HIL-BUD-08` | RP SRAM/flash A/B/update/recovery/IPC high-water and fault injection | `3A` |

The equations, admission boundaries and test thresholds receive **«Проведено ревью»**. This status reviews the architecture budget; it does not fabricate measurements for unbuilt hardware. Power, RF qualification, dated cost and the atomic winner remain separate next inputs.
