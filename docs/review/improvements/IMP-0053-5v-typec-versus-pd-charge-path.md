# IMP-0053 — 5-V Type-C power path versus USB-PD

- Статус: **Открыто — требуется решение владельца**
- Дата: 2026-08-18
- Context: [`PWR-0003`](../architecture/PWR-0003-charge-power-path-options.md)
- Battery behavior: [`DEC-0062`](../decisions/DEC-0062-individually-replaceable-2s-cells.md)

## Decision options

- **A / `C5V` — recommended:** ordinary 5-V Type-C/legacy input with explicit
  source-current detection, 2S NVDC boost charger/power path and separate real
  gauge/protector. Lowest complete BOM and complexity; charging is load-aware
  and may slow/pause during high-power use.
- **B / `CPD`:** USB-C PD controller plus wide-input 1–4S buck-boost charger.
  Faster/more headroom, but adds cost, area, PD image/provisioning, compliance
  and high-voltage fault work without a current product requirement.
- **C / `CLEG`:** repair the old BQ25887 design with external missing blocks.
  Rejected as dominated after its apparent part-count advantage disappears.

## Recommendation

Accept **A / C5V**. It preserves ordinary charger compatibility, USB-only
recovery and battery supplement without paying for unrequested fast charging.

