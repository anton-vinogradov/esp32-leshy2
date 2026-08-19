# REV-0005AQ — local-controls propagation review

> Amended by `DEC-0088/REV-0005AS`: exact ST77922 address/active-low polarity
> are now paper inputs; only fixed `SN74LVC1G07DCKR` remains.

- Status: **Проведено ревью**
- Decision: [`DEC-0086`](../decisions/DEC-0086-complete-local-controls-and-direct-encoder.md)
- Finding: [`FND-0090`](../findings/FND-0090-required-local-controls-were-dropped.md)

## Propagation checked

| Consumer | Result |
|---|---|
| old mockup evidence | confirms nine ordinary buttons, encoder, PTT and STOP as separate physical items; old GPIO placement is not inherited |
| machine device registry | exact TCA9534A, fixed active-low touch normalizer, first encoder and matrix diode expose real package contacts; S3 declares PCNT0 |
| address provenance | `FND-0091` checks the TI address byte and fixes all-high UI straps to `0x3F` and all-low RP evidence straps to `0x38` |
| G2F-3I allocation | GPIO39/47 are dedicated encoder phases, touch joins GPIO37 wired-low IRQ and S3 becomes `33/3/0` |
| slow-plane routes | dedicated TCA9534A P0…P6 implements interrupt-capable 4×3 selection with exact pulls/diodes; P7 is reserved and main TCA6424 P00…P05 are free |
| safety and PTT | RP GPIO21 remains direct PTT; normally-closed STOP and recessed RE-ARM remain outside MCU/I²C/UI paths |
| product diagrams | vertical hardware diagrams show every control role, UI expander, encoder, diode and touch adapter with MPN or explicit MPN TBD |
| hardware target pages | English and Russian start pages publish the complete local inventory and current pin/resource result without review IDs |
| firmware target/runtime | both target pages and `ARC-0002/ARC-0003` define matrix scan, PCNT detent semantics, shared IRQ service and distinct PTT/STOP/RE-ARM behavior |
| regression tests | machine validation, generated-artifact check, hardware tests and firmware target-page tests pass |

## Review boundary

Source, generated atlas, target pages and runtime inputs agree. This review
does not claim that switch mechanics, encoder location/feel, matrix debounce
or concurrent-load HIL have passed. `REV-0005AS` separately closes touch
identity/address/polarity on paper while retaining IRQ/reset HIL. Neither
review authorizes KiCad.
