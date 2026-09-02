# R2 parameters and models

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](parameter-model-register.ru.md)

`H3-R2.0.2` is reviewed. This is the exact future-calculation input register for the accepted R2 circuit, not the old R1 topology: every component type is bound to its MPN, instances, sheets, parameter source, model class and verification owner.

## Coverage

- `251` component groups: `245` on-board and `6` explicitly external/final-installed.
- `1208` fitted positions; all `251` groups have an H3 owner.
- `75` groups already contain structured parameters; `176` are in an explicit extraction queue rather than receiving invented values.
- `251` method candidates are assigned; exact methods, tolerances and applicability are frozen next in `H3-R2.0.3`.

## Model classes

| Class | Groups | With structured seed | Need extraction |
|---|---:|---:|---:|
| `analog_peripheral` | 6 | 3 | 3 |
| `connector_interconnect` | 12 | 6 | 6 |
| `digital_interface` | 34 | 19 | 15 |
| `electromechanical_or_load` | 8 | 0 | 8 |
| `general_component` | 39 | 17 | 22 |
| `passive_corner` | 124 | 19 | 105 |
| `power_safety_active` | 13 | 3 | 10 |
| `programmable_controller` | 2 | 0 | 2 |
| `radio_rf` | 13 | 8 | 5 |

## Bounded source findings

No factory-catalog-only parameter source remains. Exact `3225-27.00-10-10-10/A` (`C518151`) is bound to TX3 ESR, drive and temperature limits; former `CS0805-R27J-S` is replaced by factory-stocked `RS-06L2R70FT` (`C323265`) after the H3-R2.3 backlight calculation.

> Placement, routing, purchasing and fabrication remain forbidden. The next step reproducibly freezes methods, tolerances and pass/fail rules.

[251-row machine register](../hardware/verification/generated/H3-R2-parameter-provenance.json). The historical R1 `H3-VRF02` register remains archived evidence and is not R2 authority.
