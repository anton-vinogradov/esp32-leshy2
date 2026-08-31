# R2 parameters and models

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](parameter-model-register.ru.md)

`H3-R2.0.2` is reviewed. This is the exact future-calculation input register for the accepted R2 circuit, not the old R1 topology: every component type is bound to its MPN, instances, sheets, parameter source, model class and verification owner.

## Coverage

- `242` component groups: `237` on-board and `5` explicitly external/final-installed.
- `1187` fitted positions; all `242` groups have an H3 owner.
- `70` groups already contain structured parameters; `172` are in an explicit extraction queue rather than receiving invented values.
- `242` method candidates are assigned; exact methods, tolerances and applicability are frozen next in `H3-R2.0.3`.

## Model classes

| Class | Groups | With structured seed | Need extraction |
|---|---:|---:|---:|
| `analog_peripheral` | 6 | 3 | 3 |
| `connector_interconnect` | 14 | 6 | 8 |
| `digital_interface` | 33 | 18 | 15 |
| `electromechanical_or_load` | 7 | 0 | 7 |
| `general_component` | 38 | 15 | 23 |
| `passive_corner` | 118 | 17 | 101 |
| `power_safety_active` | 11 | 3 | 8 |
| `programmable_controller` | 2 | 0 | 2 |
| `radio_rf` | 13 | 8 | 5 |

## Bounded source findings

For `CS0805-R27J-S` (`C108271`) and `3225-27.00-10-10-10/A` (`C518151`), JLCPCB proves exact identity and the factory route, but a complete manufacturer-controlled corner model is not yet bound. They remain `H3-R2.3` inputs; missing parameters may not be silently assumed. This is not a component-replacement request.

> Placement, routing, purchasing and fabrication remain forbidden. The next step reproducibly freezes methods, tolerances and pass/fail rules.

[242-row machine register](../hardware/verification/generated/H3-R2-parameter-provenance.json). The historical R1 `H3-VRF02` register remains archived evidence and is not R2 authority.
