# FND-0038 — permanent C5 UART reduces generic reserve from seven to five

- Статус: **Закрыто корректировкой resource ledger; проведено ревью**
- Дата: 2026-08-16
- Причина: owner clarification in `DEC-0031`
- Затрагивает: `PIN-0002/SYN-3A`, `PKG-0001`, cost/margin claims, firmware target contract

## Несоответствие

Stage 3 counted C5 GPIO11/12 among seven generic free pins. `REC-0001` already
required retaining C5 UART0 for manufacturer RF-test and fallback diagnostics,
and `DEC-0031` now makes that interface permanently accessible through DBG10.
A pin cannot be both an unconditional generic product reserve and a dedicated
always-available diagnostic signal.

## Correction

- GPIO11 becomes `C5_UART0_TX_SERVICE` / DBG10 `DBG0`.
- GPIO12 becomes `C5_UART0_RX_SERVICE` / DBG10 `DBG1`.
- Current `SYN-3A` ledger is `9 product-used + 2 service-reserved + 5
  strap/recovery-reserved + 5 generic free = 21`.
- Remaining generic free C5 pins are GPIO2/4/5/23/24.

No capability or controller collision is introduced. The RP choice still
provides substantially more C5 margin than two-domain candidates, but the
honest product claim is five generic pins plus two dedicated diagnostic pins,
not seven generic pins.

## Propagation

`PIN-0002`, `PKG-0001`, `DEC-0028` annotation, `CST-0001`, target/current-state
documents and firmware `ARC-0001` are corrected. `REV-0004G` records the
cross-repository result.
