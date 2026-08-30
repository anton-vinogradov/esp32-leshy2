# H2-R2 electrical prerequisites

[Русский](h2-r2-electrical-prerequisites.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This is the live prerequisite ledger for the new six-domain, dual-RP R2
production schematic. It records verified results, not the decision history.
Native R2 ECAD/KiCad starts only after all three rows close.

| Marker | Status | Production result |
|---|---|---|
| `H2-R2.0.1` | ✅ Reviewed | Exact onsemi `FSUSB42MUX` / JLCPCB `C11355`, MSOP-10, Extended SMT, Economic and Standard PCBA, JLCPCB source, MSL 1. Live 2026-08-30 snapshot: stock 66,698; available 66,045; MOQ 1; USD 0.3179 at quantity 1. The existing package and pin topology remain unchanged. |
| `H2-R2.0.2` | ▶ Current | Select and prove the exact factory-placeable always-on service-VBUS detector/latch. It must seize C5 service ownership asynchronously without powering the board from service VBUS or depending on firmware. |
| `H2-R2.0.3` | ⏳ Waiting | Close the Pack/Safety I²C powered-off-Ioff boundary and separate `3V3_MAIN`/AON pull-ups on Hub GPIO42/43. |

## Current point · H2-R2.0.2

The mux factory route is no longer a blocker. The next source artifact is the
exact detector/latch circuit, including MPNs, defaults, legal transitions,
power-off leakage, factory route, MOQ and price. Quote, purchase, fabrication
and native R2 ECAD remain blocked.

## Evidence and recheck rule

- Live factory card: [onsemi FSUSB42MUX / C11355](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355).
- Electrical authority: [onsemi FSUSB42 datasheet](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf).
- Machine source: [`c5-sdio-service-mux-contract.json`](../hardware/architecture/c5-sdio-service-mux-contract.json).
- Generated audit: [`H0-R2-c5-sdio-service-mux.json`](../hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json).

The live stock snapshot proves the selection-time route only. The exact MPN,
JLC number, assembly class, stock/explicit sourcing route, MOQ and price are
rechecked at architecture freeze and immediately before the exact-one order.
