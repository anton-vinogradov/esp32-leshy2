# CST-0001 — dated candidate cost and implementation burden

- Статус: **Проведено ревью сопоставимого snapshot; production quotes/AVL открыты**
- Дата/валюта: 2026-08-16, USD, без НДС/доставки/пошлин
- Этап: 3, шаг 5e
- Входы: reviewed `SYN/PIN/BUD/PWR/RFQ`, `DEC-0005` zero-loss cost rule
- Сравнение: candidate-specific delta only; одинаковый product BOM сокращён как общий

## Метод

Одинаковые S3/C5 modules, 3×nRF, CC1101, Si4732, ES8311/audio, SA518, display/touch, microSD, battery/charger/power rails, USB, antennas, U214/GPS/NFC connectors, hard STOP и enclosure не влияют на разницу candidates и здесь не суммируются.

Recurring delta считается в одном supplier/quantity snapshot:

- LCSC public prices at quantity 500 where available;
- current stock записан отдельно от price tier: опубликованная цена 500+ не означает, что 500 деталей можно купить сегодня;
- assembly, PCB-area и passives without exact schematic сохраняются диапазоном, а не ложной точностью;
- firmware/update/manufacturing/HIL burden не прячется в BOM.

Это comparison input этапа 3, не полный production COGS.

## Датированные supplier facts

| Part / role | Source | Qty-500 unit price | Observed stock note |
|---|---|---:|---|
| RP2354A LCSC SKU `C41378174` | [LCSC](https://www.lcsc.com/product-image/C41378174.html) | $1.2674 | one-card observation only; not valid as a global allocation conclusion |
| SN74HC595DR `C10092` | [LCSC](https://www.lcsc.com/product-detail/Shift-Registers_Texas-Instruments-SN74HC595DR_C10092.html) | $0.1296 | tens of thousands shown in stock |
| TS5A23157DGSR `C11133` | [LCSC](https://www.lcsc.com/product-detail/Analog-Switches_Texas-Instruments-TS5A23157DGSR_C11133.html) | $0.2721 | about 4,984 shown in stock |
| TCA9534PWR `C783615` | [LCSC](https://www.lcsc.com/product-detail/I-O-Expanders_Texas-Instruments-TCA9534PWR_C783615.html) | $0.4017 | about 1,620 shown in stock |
| 12 MHz crystal comparison `C7206294` | [LCSC](https://www.lcsc.com/product-detail/C7206294.html) | $0.0464 | about 2,185 shown; exact load/ESR/ppm still schematic qualification |

[Raspberry Pi](https://www.raspberrypi.com/products/rp2350/) states RP2350 production through at least January 2045 and documents the RP2354A stacked-flash option.

**Correction `FND-0035`:** exact orderable identities are `SC1511-A4` (7-inch/500) and packaging-equivalent `SC1511(13)-A4` (13-inch/3400). The 2026-08-16 authorised-distributor check found public exact-A4 stock above 500 at [Mouser](https://www.mouser.com/ProductDetail/Raspberry-Pi/SC1511-A4) and [DigiKey](https://www.digikey.com/en/products/detail/raspberry-pi/SC1511-13-A4/28172169). Therefore the former «immediate stock below 500» conclusion is withdrawn. Written quotes, lot/stepping traceability and assembly/yield evidence remain open. The historical single-supplier arithmetic below is not retroactively mixed with different currencies, exact-crystal pricing or assembly scope; stage-4 exact COGS will supersede it.

## Candidate-specific recurring delta at 500 units

### `SYN-2A`

| Item | Unit cost |
|---|---:|
| SN74HC595 radio-control latch | $0.1296 |
| second local C5 TCA9534-class slow control | $0.4017 |
| protected IRQ aggregation, OE/STOP interface, safe pulls/passives | $0.10…0.25 allowance |
| GNSS UART mux | $0; two C5 UARTs are direct |
| **Candidate delta** | **$0.6313…0.7813** |

### `SYN-2B`

| Item | Unit cost |
|---|---:|
| SN74HC595 radio-control latch | $0.1296 |
| dual-SPDT selected-GNSS UART switch | $0.2721 |
| protected IRQ aggregation, OE/STOP interface, safe pulls/passives | $0.10…0.25 allowance |
| second local slow-control expander | $0; common S3 controller covers non-deadline controls |
| **Candidate delta** | **$0.5017…0.6517** |

### `SYN-3A`

| Item | Unit cost |
|---|---:|
| RP2354A A4 with 2 MiB stacked flash | $1.2674 |
| 12 MHz crystal | $0.0464 |
| selected-GNSS UART switch | $0.2721 |
| load capacitors/decoupling/reset/USB-SWD-RUN access allowance | $0.15…0.30 |
| radio latch and IRQ aggregation | $0; direct RP pins |
| **Candidate delta** | **$1.7359…1.8859** |

Midpoint comparison is `$0.7063 / $0.5767 / $1.8109` for `2A / 2B / 3A`. Thus:

- `2B` is about `$0.13` cheaper than `2A` in recurring candidate delta;
- `3A` costs about `$1.10…1.38` more than `2B`;
- `3A` costs about `$0.95…1.25` more than `2A`.

The ranges intentionally overlap unquoted glue/assembly effects. A production quote must include feeder/setup, QFN60 assembly/yield, PCB area and test time before these values become COGS.

## What the premium actually buys

| Value/cost surface | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| programmable targets | 2 | 2 | 3 |
| safe generic MCU GPIO reserve | 0 | 0 | 7 on C5 |
| direct nRF CE/CSN/IRQ | no; latch/aggregate | no; latch/aggregate | yes |
| radio/voice deadline isolation | medium | weakest under C5 native/IR load | strongest |
| paper RF route prior | medium/high risk | highest concentration | lowest, plus new oscillator gate |
| recurring delta | middle | lowest | highest |
| current qty-500 sourcing | quoted parts adequate | quoted parts adequate | public exact-A4 stock clears 500; quotes/traceability still required |

The RP premium is therefore not justified as a parts-count saving. At stage 3 it bought deterministic isolation, direct controls, seven C5 reserve pins and cleaner partitioning. `DEC-0031/FND-0038` later dedicates GPIO11/12 to permanent UART0 diagnostics, so the current result is five generic C5 reserve pins plus two service-reserved pins. The two-domain variants buy lower recurring cost and one fewer signed target, but have zero GPIO reserve and greater scheduling/RF proof risk.

## Firmware, update, manufacturing and HIL burden

Common work—S3/C5 signed A/B update, SDIO link, product UI/security policy and common radio application semantics—cancels. Candidate-specific proof packages are counted below; a package is not an engineer-week or dollar quote.

| Candidate | Additional work packages | Relative burden |
|---|---|---|
| `2A` | S3 latch/IRQ packet service; S3 native/UI/audio/SD contention HIL; C5 U214+two-GNSS service; cross-domain accessory adaptation | 4 |
| `2B` | C5 latch/IRQ packet service; high-rate C5→S3 capture framing; C5 native/IR/radio latency HIL; S3 GNSS mux/accessory service; failure recovery under bulk SDIO | 5 |
| `3A` | RP BSP/linker; first-stage verifier + signed A/B/rollback; RP↔S3 protocol; nRF/CC/voice drivers; third-target orchestrator; USB/SWD/manufacturing flow; RP fault/latency/RF HIL; S3 service integration | 8 |

For a volume `V`, effective per-unit comparison is:

`candidate recurring delta + candidate-specific engineering/test NRE ÷ V + measured yield/test-time delta`.

No dollar NRE is invented without team rates and schedule. Because `3A` is higher in both recurring delta and work-package count, it can win only on product risk/margin, not on accounting break-even.

## Screened cost substitutions

| Substitution | Result |
|---|---|
| RP2350A + external flash | current distributor snapshot lists RP2350A above RP2354A before flash; no recurring saving and more PCB/AVL parts |
| RP2040 + external flash | [RP2040](https://www.raspberrypi.com/products/rp2040/specifications/) has 264 KiB SRAM versus the reviewed 416 KiB RP active ceiling/104 KiB guard and lacks RP2350's optional ROM-enforced signed-boot architecture; not a zero-loss drop-in |
| cheaper unqualified I/O expander/mux | may be reconsidered in stage 4 only with reset state, voltage, timing, AVL and fault equivalence; catalog price alone is not accepted saving |
| remove latch/IRQ protection/slow control | loses independent full-function radio state or reset/STOP/fault behavior; rejected by `DEC-0005` |
| make one radio receive-only or share one antenna switch | loses accepted nRF symmetry/simultaneous PRX; rejected |

There is no new zero-loss part substitution ready for owner acceptance at this step. Cost optimization remains active on common component qualification, PCB area and supply-chain quotes after architecture selection.

## Decision-facing result

| Rank axis | 1st | 2nd | 3rd |
|---|---|---|---|
| recurring candidate BOM | `2B` | `2A` (+≈$0.13) | `3A` (+≈$1.23 vs `2B` midpoint) |
| implementation burden | `2A` | `2B` | `3A` |
| GPIO/scheduling/RF safety margin | `3A` | `2A` | `2B` |
| immediate qty-500 candidate-part availability | `2A/2B/3A` | — | `3A` still requires two quotes/traceability, not an allocation-shortage claim |

This table is not a weighted winner. `PKG-0001` later accepted `3A`; `FND-0035` subsequently corrected the stock conclusion while leaving exact quotes/traceability, QFN60 assembly and third-target work as real gates. The approximately $1.10 midpoint is a conservative historical comparison, not a current production quote.

The supplier snapshot, recurring ranges and non-recurring burden model receive **«Проведено ревью»**. Prices remain dated evidence, not permanent facts.
