# FND-0076 — parallel removable cells shift, not remove, admission risk

- Статус: **Подтверждено; correction предложена в IMP-0055**
- Дата: 2026-08-18
- Decision: [`DEC-0064`](../decisions/DEC-0064-reopen-battery-electrical-topology.md)
- Analysis: [`PWR-0006`](../architecture/PWR-0006-one-or-two-cell-topology-comparison.md)

## Finding

Changing two equal cells from series to parallel does not create energy or
cell power. For two nominal `3.6 V, C Ah` cells:

- series: `7.2 V × C Ah = 7.2C Wh`;
- parallel: `3.6 V × 2C Ah = 7.2C Wh`.

At the same ideal system power, a series pair carries system current through
both cells, while a balanced parallel pair divides twice the bus current
between the two cells. The ideal current per cell is therefore the same. The
real differences are common-path current, conversion direction, contact loss,
cell sharing and behavior with one cell absent.

Direct parallel connection is unsafe for removable cells. Different terminal
voltages can drive uncontrolled equalization current from one cell into the
other. A safe implementation needs a reverse-safe, normally-open path per
slot, independent cell voltage/temperature/protection, bounded precharge and a
controller that decides when charge and discharge may be shared. The
MAX17300/MAX17310 parallel-battery mode demonstrates the necessary class but
its datasheet still assigns charger-presence and cross-charge decisions to the
host; the IC is not a host-free cure.

## Power-path consequence

Using the accepted `12 W` continuous and `15 W` transient envelopes at a
conservative minimum cell voltage and `90%` conversion efficiency:

| Battery bus | 12 W input current | 15 W input current |
|---|---:|---:|
| `1S`, 3.0 V | `4.44 A` | `5.56 A` |
| `2S`, 6.0 V | `2.22 A` | `2.78 A` |

The `1S` common path therefore needs roughly twice the current rating and has
roughly four times the `I²R` loss for the same shared resistance. It also turns
the 3.3-V rail into a buck-boost and the 4-V/5-V rails into boost or
buck-boost paths. `BQ25798` can charge `1S`, but its ordinary battery-only SYS
path does not replace those downstream boost converters.

## Correction

- Reject unisolated removable-cell `1S2P`.
- Compare controlled `1S` slots only at equivalent safety and full-load
  behavior.
- Treat one-cell operation as the genuine benefit of the controlled `1S`
  branch; do not claim lower cost, greater stored energy or greater cell power
  without a complete BOM/loss proof.

## Primary sources

- [ADI MAX17300/MAX17310 parallel-battery management and host responsibilities](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17300-MAX17313.pdf)
- [ADI discussion of dangerous uncontrolled current between directly paralleled batteries](https://www.analog.com/en/resources/technical-articles/monolithic-dual-battery-power-manager-increases-runtime-decreases-charge-time.html)
- [TI BQ25798 1–4-cell charger datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf)

