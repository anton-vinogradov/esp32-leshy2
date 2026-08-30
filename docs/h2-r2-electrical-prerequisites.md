# H2-R2 electrical prerequisites

[Русский](h2-r2-electrical-prerequisites.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This is the live prerequisite ledger for the new six-domain, dual-RP R2
production schematic. It records verified results, not the decision history.
Native R2 ECAD/KiCad starts only after all three rows close.

| Marker | Status | Production result |
|---|---|---|
| `H2-R2.0.1` | ✅ Reviewed | Exact onsemi `FSUSB42MUX` / JLCPCB `C11355`, MSOP-10, Extended SMT, Economic and Standard PCBA, JLCPCB source, MSL 1. Live 2026-08-30 snapshot: stock 66,698; available 66,045; MOQ 1; USD 0.3179 at quantity 1. The existing package and pin topology remain unchanged. |
| `H2-R2.0.2` | ✅ Reviewed | The exact always-on path is accepted: `DMN2056U-7` / `C332302` detects VBUS only through a 1-Mohm + 1-Mohm insulated-gate divider; `SN74LVC1G74DCUR` / `C70285` latches service ownership asynchronously; `74HC20PW,118` / `C546719` permits clear only with VBUS absent, C5 EN low, Hub SDIO high-Z and an explicit AON release request. All three are live-stock Standard-PCBA parts with MOQ 1. Exact-one component burden including five reused passives is USD 0.5857. |
| `H2-R2.0.3` | ▶ Current | Close the Pack/Safety I²C powered-off-Ioff boundary and separate `3V3_MAIN`/AON pull-ups on Hub GPIO42/43. |

## Current point · H2-R2.0.3

The mux and service-ownership circuits are no longer blockers. The accepted
detector has no DC junction from service VBUS into a product rail: its nominal
load is 2.5 uA into a 2-Mohm divider to ground, and the MOSFET drain is pulled
up only from `AON_SAFE_3V3`. The latch's preset and clear cannot both be low,
because the same active-low VBUS evidence also enters the four-condition clear
NAND. The next source artifact is the exact powered-off-Ioff Pack/Safety I2C
boundary. Quote, purchase, fabrication and native R2 ECAD remain blocked.

## Evidence and recheck rule

- Live factory cards: [onsemi FSUSB42MUX / C11355](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355), [Diodes DMN2056U-7 / C332302](https://jlcpcb.com/partdetail/DiodesIncorporated-DMN2056U7/C332302), [TI SN74LVC1G74DCUR / C70285](https://jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G74DCUR/C70285), [Nexperia 74HC20PW,118 / C546719](https://jlcpcb.com/partdetail/Nexperia-74HC20PW118/C546719).
- Electrical authority: [onsemi FSUSB42 datasheet](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf), [DMN2056U datasheet](https://www.diodes.com/datasheet/download/DMN2056U.pdf), [SN74LVC1G74 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), [74HC20 datasheet](https://assets.nexperia.com/documents/data-sheet/74HC20.pdf).
- Machine source: [`c5-sdio-service-mux-contract.json`](../hardware/architecture/c5-sdio-service-mux-contract.json).
- Generated audit: [`H0-R2-c5-sdio-service-mux.json`](../hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json).

The live stock snapshot proves the selection-time route only. The exact MPN,
JLC number, assembly class, stock/explicit sourcing route, MOQ and price are
rechecked at architecture freeze and immediately before the exact-one order.
