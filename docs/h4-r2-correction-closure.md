# H4-R2.2 BSP correction closure

[Русский](h4-r2-correction-closure.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Diagnostic](h4-r2-contract-reconciliation.md)

The three owned firmware-generation corrections are closed without changing the hardware pinout. The generated BSP now represents all **173/173** reviewed H2 controller rows; every target rejects an incomplete mapping/count before normal work.

| Domain | H2 rows | BSP rows | Mapping | Result |
|---|---:|---:|---|---|
| `s3` | 33 | 33 | `exact_pins` | ✅ |
| `c5` | 14 | 14 | `exact_pins` | ✅ |
| `rf_rp` | 48 | 48 | `exact_pins` | ✅ |
| `hub_rp` | 48 | 48 | `exact_pins` | ✅ |
| `pack` | 13 | 13 | `exact_pins` | ✅ |
| `safety` | 17 | 17 | `exact_pins` | ✅ |

The corrected BSP was compiled and linked in all **12** locked debug/release configurations. The qualification verified **60 artifacts, 16 map files and 16 size gates**, with no build warnings. This proves source-level target integration and linking; it does not claim runtime boot or physical hardware.

The separate F5/F6 direct-i8080 implementation obligation and all 51 H5/H6/H8 physical residuals remain open. Purchase, placement, routing and fabrication remain unauthorized.

The [global H4-R2 joined gate](h4-r2-acceptance.md) is reviewed. **Current marker: `H5.0.3-R1`.**

[Machine closure](../hardware/verification/generated/H4-R2-correction-closure.json).
