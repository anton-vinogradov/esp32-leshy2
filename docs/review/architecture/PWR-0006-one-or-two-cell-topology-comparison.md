# PWR-0006 — one- or two-cell electrical-topology comparison

- Статус: **Проведено ревью вариантов; owner gate IMP-0055 открыт**
- Дата: 2026-08-18
- Reopen decision: [`DEC-0064`](../decisions/DEC-0064-reopen-battery-electrical-topology.md)
- Load source: [`PWR-0002`](PWR-0002-i3-power-prerequisite-audit.md)
- USB-PD/NVDC device: [`PWR-0004`](PWR-0004-accepted-usb-pd-front-end.md)
- Finding: [`FND-0076`](../findings/FND-0076-parallel-cells-shift-admission-risk.md)

## Preserved boundary

The comparison keeps the accepted two physical replaceable slots, mechanical
reverse blocking, cell-specific observation, default-open unsafe states,
owner-visible faults, independent programming/recovery for configurable
controllers and the `12 W` continuous / `15 W` bounded-transient load
envelope. A one-slot variant is included only to expose the true cost/runtime
trade; it is not allowed to replace the two-slot product without a new owner
decision.

`BQ25798RQMR` is not the differentiator: TI specifies the same exact device as
a 1–4-cell buck-boost charger/NVDC path. The downstream rails and removable-
cell admission boundary are the differentiators.

## Energy, current and loss arithmetic

Two identical cells store the same watt-hours in series and parallel. At
`90%` downstream conversion efficiency and minimum allowed cell voltage:

| Topology | Battery minimum | 12-W bus current | 15-W bus current | Ideal current per cell with two cells |
|---|---:|---:|---:|---:|
| supervised `2S` | 6.0 V | 2.22 A | 2.78 A | 2.22 / 2.78 A |
| controlled two-slot `1S` | 3.0 V | 4.44 A | 5.56 A | 2.22 / 2.78 A when balanced |
| one-slot `1S` | 3.0 V | 4.44 A | 5.56 A | 4.44 / 5.56 A |

The two-cell branches do not differ ideally at the cell. The controlled `1S`
branch doubles current through every shared contact, FET, shunt, trace and
converter input. For equal common resistance, that produces four times the
shared-path conduction loss. One-cell full-feature operation requires the
selected cell, contact and protection path to qualify at least the calculated
`5.56 A` transient plus tolerance, aging, temperature and converter-ripple
margin; an `8 A` design class is a reasonable next sizing target, not yet an
accepted limit.

## Complete candidate classes

| Property | A — supervised `2S` | B — controlled two-slot `1S` | C — one-slot `1S` |
|---|---|---|---|
| two installed cells | series after pair admission | independently isolated, then shared on one bus | not applicable |
| operation with one cell | no | yes, after that slot passes admission | yes |
| direct cell-to-cell current | no parallel path | blocked until controlled convergence; never uncontrolled | none |
| stored energy with same two cells | full | full | about half |
| common battery-path current | lowest | about 2× A | about 2× A |
| 3.3-V main rail | high-current buck class | high-current buck-boost class | high-current buck-boost class |
| 4.0-V voice rail | buck class | boost/buck-boost class | boost/buck-boost class |
| 5-V AUX/EXT | buck class | boost class | boost class |
| removal behavior | either cell opens product; hold-up/orderly shutdown required | remaining admitted slot can continue; insertion/removal is a fresh admission event | ordinary power loss on removal |
| manager complexity | one 2S gauge/protector + admission controller | two slot protectors/power paths + admission controller + common or per-slot gauging | one protector + one gauge |
| principal value | best shared-path efficiency and simplest rail tree | graceful one-cell operation and live removal of the other slot | minimum size/parts |
| principal cost | both cells required | more power-path circuitry | half runtime and one slot lost |

### A — supervised 2S

`PWR-0005` remains the reviewed branch. Its current high-integrity candidate is
`MAX17320G20+T + MSPM0C1104SDGS20R`, about `$4.47` at the previously checked
100-piece active-pair snapshot before FETs, fuses, shunt, NTCs, contacts and
diagnostic load. The 3.3-V, 4-V and 5-V outputs can all use ordinary bucks.
TI `TPS62135` is a representative active 3–17-V/4-A 3.3-V class, not a selected
BOM row.

### B — controlled two-slot 1S

Both slots require mechanical reverse blocking, their own fuse/secondary
layer, voltage and temperature observation, a default-open reverse-safe
back-to-back FET path and bounded precharge. The admission controller may join
a second slot only after cell profile, voltage, temperature, contact and
loaded-droop checks pass. Reset, watchdog, stale host state or an unplugged
slot returns the affected path to open; a healthy already-admitted slot may
keep the product alive.

Two implementation tiers remain electrically plausible:

1. two exact `MAX17300G+T` 1S gauge/protectors plus an always-on controller;
   their documented parallel mode helps sequence charge/discharge blocking,
   but the controller must still declare charger presence and manage >400-mV
   cross-charge cases. This is the strongest telemetry path and the most
   expensive active-manager tier;
2. one `BQ2980/BQ2982`-family high-side primary protector per slot, exact order
   code **MPN TBD** until the cell charge/UV/current/temperature envelope is
   selected; one exact `BQ27426YZFR` system-side 1S gauge; and the existing
   `MSPM0C1104SDGS20R` controller class. This is lower cost but reports combined
   bus SOC. Insertion/removal invalidates the estimate and the UI must show
   `estimating/unknown` until a fresh learning state is credible. The gauge's
   8000-mAh configuration ceiling must also cover the selected two-cell total.

The feasibility check uses actual exposed packages rather than family-only
signals:

| Device/class | Real package contacts relevant here | Consequence |
|---|---|---|
| exact `MAX17300G+T` | 3×3-mm TDFN-14-EP: `TH 1`, `CP 2`, `BATT 3`, `PFAIL 4`, `CSP 5`, `CSN 6`, `REG 7`, `SDA 8`, `SCL 9`, `ALRT 10`, `PCKP 11`, `DIS 12`, `ZVC 13`, `CHG 14`, EP→CSP | every required sense/FET/temperature/alert function is physically exposed; two I2C devices share fixed addresses and therefore need an exact mux, or the 1-Wire MAX17310 alternative and its own resource review |
| `BQ2980/BQ2982` family, exact threshold MPN TBD | 1.5×1.5-mm X2QFN-8: `BAT 1`, `VDD 2`, `VSS 3`, `CS 4`, `CTR 5`, `PACK 6`, `DSG 7`, `CHG 8` | high-side FET control and current protection are real; there is no telemetry bus, so the admission controller still needs separate pre-connect voltage/temperature observation |
| exact `BQ27426YZFR` | 1.62×1.58-mm DSBGA-9: `GPOUT A1`, `SDA A2`, `SCL A3`, `BIN B1`, `VSS B2`, `VDD B3`, `SRP C1`, `SRN C2`, `BAT C3` | all system-gauge contacts exist, including external 10-mΩ shunt sense; DSBGA assembly/inspection and gauge reset/relearning remain explicit manufacturing/runtime gates |

The public `BQ2980/BQ2982` table proves the family and real X2QFN-8 contacts,
not an order code: its fixed thresholds differ materially. For example,
`BQ298009` trips overvoltage at 4.500 V and is not a safe default for a normal
4.2-V cell; `BQ298218` uses 4.200 V and cannot be accepted until charger
accuracy and the exact cell limit prove adequate margin.

The downstream rail classes change. ADI `MAX77816` demonstrates a real
2.3–5.5-V buck-boost with at least 3 A at 3.0-V input/3.3-V output, while TI
`TPS61088` demonstrates a real 2.7–12-V, 10-A-switch boost class for a 5-V
rail. They are feasibility references, not selected MPNs or proof of the final
inductor, thermal or EMI fit.

### C — one-slot 1S

This removes the second holder, its protection, admission path, NTC and
contact network. It still needs the same high-current 1S converters as B and
the one installed cell carries the full `4.44/5.56 A` calculated load. It is
the only branch with a credible path to a lower active/connector BOM, but it
roughly halves runtime and deletes the accepted two-slot service behavior.

## Cost direction at equivalent safety

These are architecture ranges, not an RFQ or selected BOM:

| Delta relative to A | Active/circuit direction | Honest conclusion |
|---|---|---|
| B, lower-cost protector/common-gauge tier | manager silicon can save roughly `$1–2`, but two isolated slot paths and higher-current buck-boost/boost rails add roughly `$2–4` | likely **`+$1…3`**, not a cost reduction |
| B, two MAX17300 tier | duplicate gauge/protection plus controller and the same 1S rail penalty | likely **`+$5…8`** |
| C | one slot path removed, but 1S rail penalty remains | potentially neutral to modestly cheaper, paid for by about half runtime and deleted second slot |

The ranges intentionally exclude cells, taxes, factory quote, thermal copper
and qualification yield. Exact cost becomes valid only after topology, cell
MPN, protector thresholds and converter MPNs are selected.

## Decision result

- A is the best fit for the stated **cost reduction without feature loss**:
  lowest shared current, simplest rail tree and full two-cell energy, at the
  cost of requiring both cells.
- B is a real product improvement only if one-cell operation/graceful removal
  is worth extra circuit and validation cost.
- C is a separate reduced-runtime product variant, not a no-loss optimization.

## Primary sources

- [TI BQ25798 datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf)
- [ADI MAX17300/MAX17310 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17300-MAX17313.pdf)
- [TI BQ2980/BQ2982 datasheet](https://www.ti.com/lit/ds/symlink/bq2980.pdf)
- [TI BQ2980 8-A evaluation module](https://www.ti.com/tool/BQ2980EVM-883)
- [TI BQ27426YZFR exact device](https://www.ti.com/product/BQ27426/part-details/BQ27426YZFR)
- [TI TPS62135](https://www.ti.com/product/TPS62135)
- [ADI MAX77816](https://www.analog.com/en/products/MAX77816.html)
- [TI TPS61088](https://www.ti.com/product/TPS61088)
