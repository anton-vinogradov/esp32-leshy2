# REV-0005AH — battery holder and three-NTC propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0077`](../decisions/DEC-0077-keystone-1048p-qualified-cell-profile.md)
- Analysis: [`PWR-0016`](../architecture/PWR-0016-keystone-1048p-holder-and-ntc-coupling.md)
- Corrected finding: [`FND-0081`](../findings/FND-0081-holder-contact-and-thermal-proof-gap.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Exact part | active/orderable `Keystone Electronics 1048P`, exact product/drawing sources and role recorded |
| Real contacts | four functional independent slot contacts; no fabricated pad numbers; specimen continuity gate explicit |
| Polarity | manufacturer mechanical polarization acts before electrical admission; software is not credited with reverse protection |
| Cell scope | qualified protected button-top exact MPNs only; arbitrary/raw flat-top cells explicitly unsupported |
| 2S path | midpoint exists only in PCB routing; two positive contacts retain separate fuses |
| MAX thermals | one physically independent insulated compliant mid-can contact per cell |
| Charger thermal | one independent BQ TS sensor, two indexed possible sites, exactly one populated on HIL-proven worst slot |
| Fit artifact | placeholder becomes exact `39.8 × 86.0 mm`; board margin `24.0 mm`, U214 gap `9.719 mm`, installed-depth reserve `5.59 mm` |
| Product diagrams | exact holder MPN/role appears as its own node; three NTCs remain three physical nodes |
| Firmware | cell identity is not inferred; NTC open/short/lift and contact events remain fail-closed inputs |
| Cost/logistics | approximately `$8.57/100`; cells remain a separate regional qualified kit; custom equivalent compartment only as later cost-down |

## Remaining gates

Exact cell MPN, thermal-interface stack and enclosure door; received-part
continuity/orientation; holder/door insertion life; NTC compression,
insulation, open/short/lift and thermal response; installed U214 hand/thermal
fit remain I8/HIL. The paper contract receives **«Проведено ревью»** and does
not authorize KiCad.
