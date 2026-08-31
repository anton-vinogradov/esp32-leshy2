# R2 power-load binding

[Home](../README.md) · [Roadmap](roadmap.md) · [States](power-state-register.md) · [Русский](power-load-binding.ru.md)

`H3-R2.1.2` passes structural review: all `613` fitted instances touching an accounted rail have exactly one explicit line. The register adds `6` external load contracts. Unbound lines: `0`; hidden miscellaneous allowances: `0`.

## Bound surface

| Disposition | Lines |
|---|---:|
| `active_consumer` | 121 |
| `connector_or_external_boundary` | 11 |
| `conversion_or_protection_path` | 22 |
| `effective_capacitance_and_dc_leakage` | 241 |
| `indirect_powered_consumer` | 16 |
| `resistive_dc_branch` | 191 |
| `series_dcr_and_saturation` | 9 |
| `series_protection` | 2 |

## What is not yet a pass

This reviews accounting completeness, not numeric DC margin. For every line without an applicable exact maximum, `H3-R2.1.3` must extract the parameter from its bound manufacturer source or return `unresolved_fail`. RP/codec/pack child rails are explicit and cannot be counted again on top of the owning device total.

**Downstream result:** [`H3-R2.1`](power-dc-source-result.md) is fully reviewed; the [roadmap](roadmap.md) carries the live marker.

[Complete machine line register](../hardware/verification/generated/H3-R2-load-binding.json).
