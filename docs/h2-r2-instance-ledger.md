# H2-R2 native instance allocation

[Русский](h2-r2-instance-ledger.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

**The `H2-R2.1.3` instance checkpoint passed on 30 August 2026.** It fixes
which exact fitted component belongs to which current R2 project and sheet.
It does not create or approve schematic nets, PCB placement or fabrication.

## Result

| Item | Checked result |
|---|---:|
| Fitted board instances | 1,096 |
| Exact board component groups | 208 |
| Native projects | 3 |
| Project graph | 23 sheets; hierarchy-only root sheets intentionally contain no parts |
| Independent RP2354B domains | 2: front Hub RP and rear RF RP |
| Native nets created | 0 |
| Allocation errors or duplicate project-local names | 0 |

The old single-RP instance ledger was used only as a name and former-sheet
hint after current MPN, quantity, footprint, contacts and R2 sheet affinity
were reconciled. It supplied no reference designator, net or ownership rule.
Obsolete R1-only detector, identity, local-regulator and timing bodies were not
carried forward. Current AD8314, 50-contact display, dual-RP service paths and
the TCA9803 Pack/Safety boundary are present.

## Machine evidence

- [Allocation contract](../hardware/ecad/h2-r2-instance-ledger-contract.json)
- [Generated 1,096-instance ledger](../hardware/ecad/generated/H2-R2-native-instance-ledger.json)
- [Generator](../hardware/ecad/h2_r2_instance_ledger.py)

The current point remains **`H2-R2.1.3`**: join reviewed rails, M1 contacts,
domain transports and explicit NCs in the three native projects. Placement,
routing, fabrication and ordering remain blocked.
