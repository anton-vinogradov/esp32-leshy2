# FND-0077 — MAX17320 prequal is a linear CHG-FET mode

- Статус: **Открыто; требует owner choice `IMP-0056`**
- Дата: 2026-08-18
- Context: [`PWR-0007`](../architecture/PWR-0007-max17320-2s-surrounding-circuit.md)
- Proposal: [`IMP-0056`](../improvements/IMP-0056-deep-cell-recovery-boundary.md)
- Affects: `I3`, CHG/DIS MOSFET, thermal HIL, battery UX and Controlled Zone

## Finding

The exact `MAX17320G20+T` does not implement low-cell prequalification as an
ordinary fully-on switch state. ADI states that it modulates and reuses the
charge NFET to regulate prequal current. The configurable loop limits current
and protection-FET heating, and the current may take about one minute to begin
after a charge source is applied.

Therefore the CHG MOSFET cannot be selected from switching `RDS(on)`, headline
current and package temperature alone if in-product prequal is enabled. Its
linear-mode safe-operating area, pulse duration, PCB thermal path and the worst
charger-versus-stack voltage must all be qualified together.

## Consequence for the current candidates

| Candidate | Fully-on path | Prequal consequence |
|---|---|---|
| one `FDMC8030` dual 40-V N-FET | compact 3×3-mm package; maximum `14 mOhm` per channel at 4.5-V gate drive | attractive only after prequal is disabled or a source-backed linear SOA/thermal proof is produced; the switching ratings do not provide that proof |
| two `CSD17575Q3T` 30-V N-FETs | maximum `3.2 mOhm` each at 4.5-V gate drive; lower ordinary conduction loss | published transient SOA gives a better analysis start, but still does not by itself qualify the long configurable MAX17320 prequal interval |

This does **not** invalidate the selected gauge. It exposes a product-policy
fork that the old power sheet did not make visible: the product can reject a
deeply discharged cell and use compact switching FETs, or it can attempt
in-device recovery and pay for an explicitly linear-safe power path and its
thermal qualification.

## Primary evidence

- [ADI MAX17320 Rev.12 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf),
  General Description, Prequal Charging and `nChgCfg` sections;
- [onsemi `FDMC8030` datasheet](https://www.onsemi.com/download/data-sheet/pdf/fdmc8030-d.pdf);
- [TI `CSD17575Q3T` product and datasheet](https://www.ti.com/product/CSD17575Q3/part-details/CSD17575Q3T).

