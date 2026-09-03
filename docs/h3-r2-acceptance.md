# H3-R2 result · virtual electrical verification

[Русский](h3-r2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Physical evidence register](physical-evidence-register-r2.md)

`H3-R2.7` closes the global H3 phase for the current R2 hardware. All `20` current evidence artifacts and `129` recorded source hashes cross-check with zero mismatch and zero open analytical finding.

| Workstream | Reviewed scope | Result |
|---|---|---|
| `H3-R2.0` | Inputs, provenance and methods | 2 projects · 22 sheets · 1,208 schematic instances · 789 nets · 251 exact groups · 9 methods |
| `H3-R2.1` | DC, rails, sources and charge | 2,266 legal states · 224 rail corners · 30.560% minimum reserve · 3.516 A maximum pack current |
| `H3-R2.2` | Transitions and faults | 14 ordered scenarios · 7,316 handover cases · 5 starts · 4 load steps · 10 watchdog/fault cases |
| `H3-R2.3` | Analog corners | display, audio, IR, battery and Airband calculations pass; routed Airband tuning remains measured |
| `H3-R2.4` | Digital interfaces | direct i8080-8 at exact 20 MHz · M1 80/80 parity · explicit USB/service ownership |
| `H3-R2.5` | RF and coexistence | 71 checks · 10 permanent antenna paths · 13 quiet contracts · all 3×nRF24 role/identity mixes |
| `H3-R2.6` | Thermal and single fault | 56 thermal profiles · 30 single faults · 25 checks · no unattended-runtime claim |

## What is complete

- Every electrical claim calculable before layout has a reproducible result on the exact H1-R2.38 / H2-R2.1.5 boundary.
- All legal power states, transitions, analog corners, digital interfaces, permanent RF paths, thermal profiles and single-fault cases pass their frozen paper rules.
- Every correction is already present in the current source and all dependent evidence has been regenerated.

## What remains physical

The [physical evidence register](physical-evidence-register-r2.md) contains `51` still-open rows with explicit H5/H6/H8 owners and pass rules. This is expected: routed impedance/parasitics, received-part identity and measurements on the one assembled prototype cannot be honestly closed on paper. The separate F5/F6 i8080 implementation obligation remains firmware work, not a disguised physical residual.

## Boundary and next stage

H3 approval does **not** authorize purchasing, PCB placement/routing, fabrication, final RF/thermal performance or unattended-runtime claims. The exact next marker is `H4-R2.0.1`: freeze and join the current mechanics, ECAD, H3 result and firmware-R2 evidence before H5.

[Machine cross-check](../hardware/verification/generated/H3-R2-crosscheck.json) · [Machine acceptance package](../hardware/verification/generated/H3-R2-acceptance-package.json)
