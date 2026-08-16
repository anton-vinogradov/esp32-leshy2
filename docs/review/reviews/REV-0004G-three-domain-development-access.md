# REV-0004G — permanent three-domain development access

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Решение: [`DEC-0031`](../decisions/DEC-0031-permanent-three-domain-development-access.md)
- Artifacts: [`IMP-0026`](../improvements/IMP-0026-connectorless-owner-recovery-fixture.md), [`SVC-0001`](../components/SVC-0001-three-domain-development-access.md)

## Acceptance and propagation

| Check | Result |
|---|---|
| owner chose B with explicit prototype-debug rationale | yes |
| every MCU has independent USB | yes; no mux |
| every MCU exposes physical reset and boot control | yes; dedicated buttons plus DBG10 |
| S3/C5 diagnostics retain UART0 | yes |
| RP diagnostics retain SWDIO/SWCLK and RUN | yes |
| common fixture can identify domain before driving | yes; passive two-bit ID and high-Z-first contract |
| C5 uses corrected GPIO28/CHIP_PU recovery | yes; GPIO27 high, GPIO26 not BOOT |
| service USB VBUS can partially power a peer | no; C5/RP data-only and common rail powered normally |
| debug access bypasses TX safety/legal gates | no |
| production can silently DNP access hardware | no; separate owner decision required |
| permanent C5 UART still counted as generic reserve | no; `FND-0038` corrects seven generic free to five generic + two service-reserved |
| hardware/firmware target and current-state propagation | complete |
| C-006 final Q incorrectly granted | no; CAD/AVL/mechanics/HIL open |

## Cost consequence

The selected architecture intentionally gives up the per-board connector saving
of option A. Current manufacturer/distributor observations support the first
targets, but are not a consolidated quote: USB4105 is a cost-oriented USB 2.0
receptacle and FTSH is a higher-reliability permanent debug header. Zero-loss
cost work may qualify alternates, but it may not remove any domain's access.

`IMP-0026/B` becomes `DEC-0031`. The decision, exact access contract and
cross-repository propagation receive **«Проведено ревью»**; implementation
evidence remains open exactly as listed in SVC-0001.

## Corrected mismatch ledger

| Mismatch | Correction | Status |
|---|---|---|
| stage-3 C5 ledger called GPIO11/12 generic free while permanent UART0 diagnostics requires them | reclassified as service-reserved; five generic GPIO2/4/5/23/24 remain | corrected and closed in `FND-0038` |
