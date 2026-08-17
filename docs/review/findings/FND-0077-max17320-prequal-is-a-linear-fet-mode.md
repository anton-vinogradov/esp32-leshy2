# FND-0077 — MAX17320 prequal is a linear CHG-FET mode

- Статус: **Закрыто решением `DEC-0067`; факт сохранён**
- Дата: 2026-08-18
- Context: [`PWR-0007`](../architecture/PWR-0007-max17320-2s-surrounding-circuit.md)
- Proposal: [`IMP-0056`](../improvements/IMP-0056-deep-cell-recovery-boundary.md)
- Decision: [`DEC-0067`](../decisions/DEC-0067-no-in-device-deep-cell-recovery.md)
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
| rejected `FDMC8030` paper candidate | electrically wireable as a back-to-back pair | onsemi now marks it `Last Shipments`, so it is not a target-BOM part |
| accepted `CSD87313DMST` common-drain pair | active-production 3.3×3.3-mm package; maximum 5.5 mOhm source-to-source at 4.5-V gate drive | accepted only for fully-switching operation after `DEC-0067` disables in-product zero-volt/prequal recovery |
| two `CSD17575Q3T` 30-V N-FETs | maximum `3.2 mOhm` each at 4.5-V gate drive; lower ordinary conduction loss | retained only as historical linear-SOA analysis input, not the accepted topology |

This does **not** invalidate the selected gauge. It exposes a product-policy
fork that the old power sheet did not make visible: the product can reject a
deeply discharged cell and use compact switching FETs, or it can attempt
in-device recovery and pay for an explicitly linear-safe power path and its
thermal qualification.

## Primary evidence

- [ADI MAX17320 Rev.12 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf),
  General Description, Prequal Charging and `nChgCfg` sections;
- [onsemi `FDMC8030` lifecycle page](https://www.onsemi.com/products/discrete-power-modules/mosfets/low-medium-voltage-mosfets/fdmc8030);
- [TI `CSD87313DMS` active product page](https://www.ti.com/product/CSD87313DMS).

`DEC-0067` closes the product-policy fork with no in-device recovery. The
linear-mode fact remains a regression guard for firmware/NVM and any later
proposal to reintroduce prequalification.
