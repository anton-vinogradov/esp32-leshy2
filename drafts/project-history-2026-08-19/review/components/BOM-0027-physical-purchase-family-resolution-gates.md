# BOM-0027 — physical purchase-family resolution gates

- Статус: **проведено ревью gate coverage; exact MPN/physical HIL remain open**
- Дата: 2026-08-19
- Основание: [`FND-0109`](../findings/FND-0109-machine-map-was-not-a-complete-physical-bom.md)
- Review: [`REV-0005CB`](../reviews/REV-0005CB-physical-purchase-gate-propagation.md)

## Результат

Все четыре ранее prose-only physical purchase families теперь имеют
machine-readable `resolution_gate`. Gate не заменяет MPN и не добавляет строку
в subtotal: он фиксирует, почему выбор сейчас был бы выдумкой, кто владеет
закрытием, какие входы обязательны и какой результат можно принять.

| Family | Qty | Gate | Владелец закрытия |
|---|---:|---|---|
| `external_sma_bodies` | 9 | `g3_connector_plane_and_mount_coupon_required` | G3 connector plane, mount/torque coupon and per-path VNA |
| `rf_cable_assemblies` | 5 | `received_mate_and_routed_length_coupon_required` | received module mate, G3 routing and harness coupon |
| `m5_connector_bodies` | 2 | `received_mate_identification_and_retention_coupon_required` | received U214/Unit cable, dock stack and retention coupon |
| `external_antenna_kit` | 12 | `profile_variant_bom_and_hil_required` | G3 ground/connector environment plus variant/profile HIL |

Итого gate contract покрывает **4/4 families / 28 physical items**: 16
base-product connector/cable bodies и 12 costed-variant antenna items.

## Что запрещено до gate pass

- generic `SMA`, `IPEX`, `HY2.0-4P` или `HDR-SMD_14P-P2.54` не является MPN;
- сетку контактов нельзя превращать в footprint или insertion stack;
- длину microcoax нельзя выбрать до placement, bend/strain and service path;
- shortlist antenna нельзя выдать за frozen kit без AM/LW identity, assembled
  VNA/sensitivity/EIRP/coexistence и current variant quote;
- open gate нельзя считать zero-cost line или qualified alternate.

## Current I8 boundary

- cost snapshot remains **175/187 lines / 829/857 placements / USD 157.3727**;
- all twelve unpriced used lines retain explicit price/RFQ gates;
- the four physical families are no longer anonymous gaps: each has a complete
  resolution contract, but no physical result is claimed before its gate pass;
- standalone display RFQ, gate execution, specific alternate qualification and
  full factory COGS remain open.

No device, owner, GPIO, net, rail, RF path, antenna count, connector polarity
or target-page diagram node changed.

`FND-0115/BOM-0028/REV-0005CC` subsequently classify these open executions as
downstream G3/G8 gates and complete the internal I8 paper-feasibility review.
