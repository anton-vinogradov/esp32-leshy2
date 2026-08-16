> Архивировано решением DEC-0027: этот документ оптимизировал legacy-derived раскладку и не является входом новой архитектуры. Сохранён только как источник идей и отрицательных результатов.

# CMP-0001 — static comparison of `LAY-S3`, `LAY-C5` and `LAY-BAL`

- Статус: **Проведено ревью static comparison; сравнительный вход единого package (`DEC-0026`)**
- Дата: 2026-08-16
- Inputs: `DM-0001`, `BUD-0001`, `PIN-0001`, `SC-0001`, `LAY-S3-0001`, `LAY-C5-0001`, `LAY-BAL-0001`
- Rule: no weighted score before required measurements/quotes; structural facts may choose test order but cannot be mislabelled measured performance/cost

## Comparable architecture summary

| Axis | `LAY-S3` | `LAY-C5` | `LAY-BAL` |
|---|---|---|---|
| Single owner of all 3×nRF | S3 | C5 | RP2040 RF controller |
| nRF service path | shared S3 SPI2 | dedicated C5 SPI2 | dedicated RP2040 SPI1 |
| Inter-MCU/host path | dedicated S3 SPI3↔C5 SPI2 | 1-bit C5 SDIO | shared S3 SPI3 endpoints for C5 and RF controller |
| S3 memory part | N8R2, measured floor required | N8R8 | N8R2, measured floor required |
| C5 direct margin | six unrestricted candidates after allocation | zero unrestricted GPIO | six unrestricted candidates after allocation |
| S3 direct margin | GPIO3 strap reserve only | GPIO3 strap reserve; GPIO35..37 unavailable | GPIO3 strap reserve only |
| New architecture devices | CE latch + reset/strap isolation | CE latch + 2→4 CS decoder + SDIO support network | RP2040 + 8 MiB flash + crystal/passives + internal module/connector |
| New firmware/trust domain | no | no | yes, signed/update/recovery/SBOM required |
| Raw nRF frames over IPC | no | yes | typed controller IPC |
| Independent C5 native USB | yes | yes in 1-bit only | yes |
| Relative rerouting/NRE | lowest | highest two-MCU reroute | new RF module plus host protocol |

## Static hard-gate result

None of the three has an unavoidable pin/controller contradiction after the exact maps were written. None has yet passed all hard gates, because memory, bus latency/loss, exact nRF module power/RF, STOP/actual-TX, recovery and cost evidence require later fixtures.

| Candidate | Strongest static argument | Decisive open gates |
|---|---|---|
| `LAY-S3` | fewest new parts, preserves current nRF side, no raw-frame IPC, C5 retains GPIO/recovery margin | N8R2 usable memory; shared SPI2 nRF IRQ/loss under display+SD+U214; strap-safe CC/nRF IRQ inputs |
| `LAY-C5` | N8R8 S3 and nRF isolated from main display/storage SPI | exact SDIO revision/goodput; zero C5 GPIO margin; nRF+IR+integrated-radio ISR coexistence; full reroute |
| `LAY-BAL` | best local nRF real-time isolation and direct per-radio CS/CE/IRQ | third-MCU BOM/power/trust/update/test; shared auxiliary link; N8R2 memory; service-module mechanics |

## Cost-without-loss review

- `LAY-S3` cannot yet claim an exact currency saving, but structurally has the smallest irreducible new BOM and reuses the most current routing.
- `LAY-C5` does not add a third MCU, but adds SDIO qualification and moves every nRF control/data trace to the pin-dense C5 side. A cheaper unit price is not assumed.
- `LAY-BAL` necessarily adds an active controller, external flash, clock/support network, recovery/test and module interconnect. It is a performance fallback, not a zero-loss cost candidate while a two-MCU layout passes.
- UI matrix versus retained U14 is orthogonal and must use the same choice/quote in all three score sheets.

## Recommended synthesis sequence

1. Use `LAY-S3` as the first synthesis candidate, not as an independently accepted target or fabricated proof.
2. Run three kill gates before schematic commitment:
   - usable S3 N8R2 PSRAM ≥1,920 KiB in `SCN-02`;
   - shared SPI2 meets all display/nRF/CC/U214/SD throughput and IRQ/loss bounds;
   - independent C5 USB/BOOT/RESET recovery works after removal of the UART bridge.
3. If memory fails, prefer `LAY-C5` with N8R8; if only shared-bus real-time fails, compare `LAY-C5` against the RF-controller fallback with measured total cost and power.
4. Never reduce three nRF paths, full native features, IR or safety gates to rescue the preferred layout.

## ⚠️ Предложение — только вход общего package

Use `IMP-0021/A` / `LAY-S3-0001` as the first integrated synthesis candidate because it has the smallest structural BOM/reroute and avoids raw nRF IPC. By `DEC-0026`, owner/transport cannot be accepted separately: the proposal is valid only if the same final package also converges memory, UI, exact pins, recovery, safety, coexistence and cost.

