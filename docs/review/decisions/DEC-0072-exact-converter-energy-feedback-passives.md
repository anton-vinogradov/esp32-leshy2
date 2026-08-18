# DEC-0072 — exact converter energy and feedback passives

- Статус: **Принято автоматически в пределах делегированного выбора компонентов; распространено**
- Дата: 2026-08-18
- Analysis: [`PWR-0011`](../architecture/PWR-0011-application-converter-passive-profile.md)
- Parent rail decision: [`DEC-0068`](DEC-0068-separate-fixed-downstream-rails.md)
- Propagation review: [`REV-0005AC`](../reviews/REV-0005AC-application-converter-passive-profile.md)

## Context

The active rail topology was accepted, but all four converters still depended
on abstract feedback and energy-storage networks. Exact parts are required to
prove fixed voltages, real package count, DC-bias margin, cost and the physical
one-component-per-box product diagram.

## Decision

1. `TPS629203DRLR` uses open `FB/VSET` for fixed 3.3 V and exact
   `RC0402FR-0742K2L` on `MODE/S-CONF` for auto-PFM/PWM AEE up to 2.5 MHz with
   output discharge disabled.
2. Its exact input/output capacitors are `CGA5L1X7R1E475K160AC` 4.7 uF/25 V
   and `GRM31CR71A226KE15L` 22 uF/10 V.
3. Each `TPS564252DRLR` receives one `GRM32ER71E226KE15L` bulk input, one
   `C1005X7R1H104K050BB` HF input, two separate
   `GRM32ER71E226KE15L` outputs and one `C0402C330J5GACTU` 33-pF feed-forward
   capacitor.
4. Fixed 1% dividers are 45.3/10 kOhm main, 68/12 kOhm voice and
   220/30 kOhm external. Their nominal voltages are 3.318, 4.000 and 5.000 V.
5. Obsolete 45.0-kOhm `RC0402FR-0745KL` is rejected; active
   `RC0402FR-0745K3L` is the exact main top resistor.
6. All 24 fitted passives are independent physical machine/diagram instances.

## Consequence

The fixed-rail architecture is now electrically instantiated through its
energy and feedback parts without adding a voltage selector or GPIO. Full
paper limits remain compatible with the loads and external eFuse OVLO.
EN/PG pulls, layout and specimen HIL remain explicit later gates; no KiCad
authorization is implied.

