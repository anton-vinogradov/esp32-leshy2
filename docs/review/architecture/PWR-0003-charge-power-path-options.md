# PWR-0003 — I3 charge and system-power-path options

- Статус: **Проведено ревью вариантов; `IMP-0053` owner decision открыт**
- Дата: 2026-08-18
- Battery behavior: [`DEC-0062`](../decisions/DEC-0062-individually-replaceable-2s-cells.md)
- Prerequisites: [`PWR-0002`](PWR-0002-i3-power-prerequisite-audit.md)
- Proposal: [`IMP-0053`](../improvements/IMP-0053-5v-typec-versus-pd-charge-path.md)

## Required result independent of option

- only the S3 product USB-C is a normal power input; S3 USB2 data remains;
- C5 and RP service USB VBUS are protected high-impedance sense only and cannot
  power/backfeed the board;
- no-battery/deeply-discharged recovery can power a bounded target safely;
- source capability is known before input-current limit rises above default;
- the battery supplements a weak source without collapsing system rails;
- application rails can be hardware-off while charging and pack supervision
  continue;
- charger loss, connector temperature and pack temperature reduce charging
  before unsafe operation;
- two loose-cell slots remain behind the separately selected admission/
  protector/gauge FET boundary from `DEC-0062`.

## Option C5V — current-limited 5-V Type-C/BC1.2 — recommended

Reference class: `TUSB320LAI` Type-C CC logic plus `BQ25883` 2S NVDC boost
charger/power path and a separate real 1–2S gauge/protector.

- accepts ordinary 5-V phone/USB sources;
- CC detects `Default/1.5 A/3 A`; charger DP/DM can detect legacy SDP/CDP/DCP;
- charger provides instant-on, 17-mΩ battery FET and battery supplement;
- maximum charge current is 2 A, but system admission always subtracts the
  active load and never promises full-rate charge during voice/TX stress;
- TI `PMP40496` is a directly relevant 2S reference using the same charger,
  CC logic and a BQ28Z610-class gauge/protector;
- no PD firmware/configuration image, high-voltage VBUS path or PD compliance
  surface is added.

The exact order codes and distributor availability are checked only after owner
acceptance, per project policy.

## Option CPD — USB-C PD plus wide-input buck-boost charger

Reference class: `TPS25751` PD controller plus `BQ25798` 1–4S NVDC buck-boost
charger and separate gauge/protector.

- negotiates higher-voltage/higher-power PD and reduces charging time/headroom
  pressure during simultaneous system use;
- adds a second 4×4-mm power IC, PD configuration image/provisioning, more
  protection/layout/compliance work and high-voltage connector fault cases;
- electrical capability substantially exceeds the accepted 12-W continuous /
  15-W transient handheld envelope and no current product scenario requires
  fast charge or power-source mode;
- remains a premium/future option, not a no-loss cost optimization.

## Option CLEG — repaired BQ25887 legacy

Adding CC detection, external system power path, real gauge/protector and
off-state charging around BQ25887 removes its apparent simplicity. It keeps no
accepted behavior unavailable in C5V and is rejected as dominated.

## Comparison

| Criterion | `C5V` | `CPD` | `CLEG` |
|---|---|---|---|
| ordinary 5-V source | pass | pass/fallback | pass |
| source-current protocol proof | pass with CC + BC1.2 | pass with PD/Type-C | requires added CC logic |
| no-battery instant-on | pass | pass | added external path |
| battery supplement | pass | pass, highest headroom | added external path |
| exact 2S reference | TI PMP40496 | TI USB-PD-CHG-EVM-01 | legacy only |
| configuration burden | charger registers + CC state | PD image + charger + compliance | fragmented custom logic |
| power/BOM/area | lowest complete option | highest | no longer lowest after repairs |
| current requirement fit | exact | over-capable | dominated |

## Recommendation

Choose `C5V`. It closes every accepted functional/safety gap at lower cost and
complexity; `CPD` buys charging speed/headroom that is not presently a product
requirement. This is a charge-input choice only: exact cell admission,
protection/gauge, downstream rails and HIL remain mandatory.

Primary sources:

- [TI BQ25883](https://www.ti.com/product/BQ25883)
- [TI TUSB320LAI](https://www.ti.com/product/TUSB320LAI)
- [TI PMP40496](https://www.ti.com/tool/PMP40496)
- [TI BQ25798](https://www.ti.com/product/BQ25798)
- [TI TPS25751](https://www.ti.com/product/TPS25751)
- [TI USB-PD-CHG-EVM-01](https://www.ti.com/product/USB-PD-CHG-EVM-01/part-details/USB-PD-CHG-EVM-01)

