# H2-R2 electrical prerequisites

[Русский](h2-r2-electrical-prerequisites.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This is the live prerequisite ledger for the new six-domain, dual-RP R2
production schematic. It records verified results, not the decision history.
All three prerequisite rows are closed. The native R2 inventory passed
`H2-R2.1.1`; exact symbol/contact/footprint reconciliation passed
`H2-R2.1.2`; the 4,243-endpoint native net reconciliation and generation of
the [two native KiCad projects](h2-r2-native-kicad.md) have also passed at
`H2-R2.1.3`, including zero-finding ERC. Cross-sheet and HW↔FW reconciliation
passed in reviewed `H2-R2.1.5`. Fabrication and ordering remain blocked.

| Marker | Status | Production result |
|---|---|---|
| `H2-R2.0.1` | ✅ Reviewed | Exact onsemi `FSUSB42MUX` / JLCPCB `C11355`, MSOP-10, Extended SMT, Economic and Standard PCBA, JLCPCB source, MSL 1. Live 2026-08-30 snapshot: stock 66,698; available 66,045; MOQ 1; USD 0.3179 at quantity 1. The existing package and pin topology remain unchanged. |
| `H2-R2.0.2` | ✅ Reviewed | The exact always-on path is accepted: `DMN2056U-7` / `C332302` detects VBUS only through a 1-Mohm + 1-Mohm insulated-gate divider; `SN74LVC1G74DCUR` / `C70285` latches service ownership asynchronously; `74HC20PW,118` / `C546719` permits clear only with VBUS absent, C5 EN low, Hub SDIO high-Z and an explicit AON release request. All three are live-stock Standard-PCBA parts with MOQ 1. Exact-one component burden including five reused passives is USD 0.5857. |
| `H2-R2.0.3` | ✅ Reviewed | Exact TI `TCA9803DGKR` / JLCPCB `C2687966`, VSSOP-8, Extended SMT, Economic and Standard PCBA. Live 2026-08-30 snapshot: stock 1,864; available 1,818; MOQ 1; USD 0.3525 at quantity 1. The MAIN A-side has two `2.2 kΩ` pull-ups; the AON B-side uses only the buffer's 3.3-mA current sources because TI forbids external B-side pull-ups. Two exact Basic 1-uF `C52923` and two Basic 100-nF `C1525` capacitors complete both rail-local decoupling groups. Exact-one component burden is USD 0.3953. |

## Result · all three prerequisites reviewed

The three pre-ECAD electrical circuits are now exact and factory-placeable. In
the asymmetric `MAIN=off, AON=on` state the TCA9803 A-side is powered-off
high-Z, so the always-on mailboxes cannot back-power the Hub. In the opposite
fault state its powered-off bus protection prevents reverse power into AON.
The buffer imposes no VCCA/VCCB ordering rule, supports 400 kHz and starts in at
most 350 us. A stuck mailbox can remove diagnostics but cannot inhibit the
independent `FAULT_KILL` path or local Safety watchdog.

The H2 result is reviewed at **`H2-R2.1.5`**; H3 now freezes its exact inputs
and hashes. Quote, purchase and fabrication remain blocked.

## Evidence and recheck rule

- Live factory cards: [onsemi FSUSB42MUX / C11355](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355), [Diodes DMN2056U-7 / C332302](https://jlcpcb.com/partdetail/DiodesIncorporated-DMN2056U7/C332302), [TI SN74LVC1G74DCUR / C70285](https://jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G74DCUR/C70285), [Nexperia 74HC20PW,118 / C546719](https://jlcpcb.com/partdetail/Nexperia-74HC20PW118/C546719), [TI TCA9803DGKR / C2687966](https://jlcpcb.com/partdetail/TexasInstruments-TCA9803DGKR/C2687966), [Samsung 1 uF / C52923](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05A105KA5NQNC/C52923), [Samsung 100 nF / C1525](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05B104KO5NNNC/C1525).
- Electrical authority: [onsemi FSUSB42 datasheet](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf), [DMN2056U datasheet](https://www.diodes.com/datasheet/download/DMN2056U.pdf), [SN74LVC1G74 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), [74HC20 datasheet](https://assets.nexperia.com/documents/data-sheet/74HC20.pdf), [TCA9803 datasheet](https://www.ti.com/lit/ds/symlink/tca9803.pdf), [MSPM0C1106 datasheet](https://www.ti.com/lit/ds/symlink/mspm0c1106.pdf).
- Machine sources: [`c5-sdio-service-mux-contract.json`](../hardware/architecture/c5-sdio-service-mux-contract.json) and [`pack-safety-i2c-boundary-contract.json`](../hardware/architecture/pack-safety-i2c-boundary-contract.json).
- Generated audits: [`H0-R2-c5-sdio-service-mux.json`](../hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json) and [`H2-R2-pack-safety-i2c-boundary.json`](../hardware/architecture/generated/H2-R2-pack-safety-i2c-boundary.json).

The live stock snapshot proves the selection-time route only. The exact MPN,
JLC number, assembly class, stock/explicit sourcing route, MOQ and price are
rechecked at architecture freeze and immediately before the exact-one order.
