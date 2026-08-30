# H2-R2 exact symbols and footprints

[Русский](h2-r2-symbol-footprint-ledger.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

**`H2-R2.1.2` was fixed on 30 August 2026.** This is the exact component-definition
boundary for the native R2 schematic. It does not create schematic nets, KiCad
projects or PCB layout.

## Result

| Ledger item | Fixed result |
|---|---|
| Exact product component groups | 213 |
| Board component groups | 208, each with one `Leshy2_R2` symbol identity and one exact footprint identity |
| Explicit non-PCBA groups | 5: display assembly, U214, two-cell kit, encoder knob and five removable RF jumpers |
| Logical contacts | 1,561, copied and hash-bound from current manufacturer contact evidence |
| Standard KiCad package identities | 175 |
| Existing manufacturer-derived local definitions | 32 |
| New local geometry to materialize | 1: exact serial `FH34SRJ-50S-0.5SH(50)` panel connector |
| Native schematic symbols/files/nets created | 0 / 0 / 0 |
| Unresolved groups | 0 |

Every row keeps the exact MPN, schematic value, complete contact map, contact
roles, native R2 sheet affinity, manufacturer evidence and JLCPCB number where
one is accepted. Historical R1 package names are hints only: they are accepted
only after exact-MPN and current-contact reconciliation and never contribute an
old designator, net or sheet owner.

## Corrections found by the ledger

Five TE Connectivity `2118651-2` parts are removable 30-mm U.FL-to-U.FL cable
assemblies. They are no longer misrepresented as PCB components. The native
schematic represents the board and module receptacle endpoints; the cable has
no symbol or PCB footprint.

Five conflicting historical package hints were resolved from the current exact
manufacturer identity rather than inherited blindly:

- the 22-µF Murata part remains an 0805 capacitor, not a resistor;
- the TDK thermistor remains a 0603 resistor-style NTC body, not a capacitor;
- the Nexperia `74LVC1G32GV,125` uses its TSOP5/SC-74A package;
- TI DCK logic/comparator bodies use the manufacturer-specific DCK five-land
  mapping where the old evidence disagreed.

The accepted `AD8314ARMZ-REEL`, the new Pack/Safety passives and
`TCA9803DGKR` are also assigned their exact current packages. No production MPN
was changed by this step.

## Machine evidence

- [Exact ledger contract](../hardware/ecad/h2-r2-symbol-footprint-contract.json)
- [Generated 213-group ledger](../hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json)
- [Current native project inventory](h2-r2-native-inventory.md)

## Current boundary

The current point is **`H2-R2.1.3`**: materialize the controlled symbols and the
single new FH34 geometry, then join rails, M1 contacts, domain transports and
explicit NCs in the three native projects. Placement, routing, fabrication and
ordering remain blocked.
