# MEC-0001 — U214 Cap-Bus mechanical interface facts

- Статус: **Проведено ревью official facts; exact host MPN/stack-up открыт**
- Дата: 2026-08-17
- Decision: [`DEC-0057`](../decisions/DEC-0057-u214-rear-dock-above-batteries.md)
- Finding: [`FND-0069`](../findings/FND-0069-u214-host-connector-mpn-and-stack-up-open.md)

## Проверенные official facts

| Item | Проверенный результат |
|---|---|
| electrical grid | `2×7`, `2.54 mm`; all 14 Cap-Bus contacts and polarity are published |
| schematic identity | U214 `P1` and Cardputer-Adv `P3` are both named only `HDR-SMD_14P-P2.54` |
| connector sex | official product photographs show exposed male square pins on U214 and a recessed female receptacle on Cardputer-Adv |
| retention | official U214 photographs label two `M2 HOLE` features; model-size drawing places their centres `56 mm` apart, `14 mm` from each 84-mm end |
| body | detailed drawing gives `84 × 24 × 15.287 mm`; product table rounds height to `15.2 mm` |
| non-flat envelope | end feet, pin field and M2 bosses protrude from the mating side; U214 cannot be represented as a flat PCB/header rectangle |

The `2×7` contact-centre span is `15.24 × 2.54 mm`; connector housing and PCB
land dimensions are part-specific and must not be derived from that grid.

## Missing official production data

Neither M5Stack schematic publishes a connector manufacturer/MPN. The official
model-size PDFs also do not specify the complete tolerance stack needed for a
new host:

- U214 exposed-pin length and allowed insertion depth;
- exact host-receptacle housing/entry-plane offset;
- loaded rail height and compression/clearance;
- M2 thread depth, screw length and allowable engagement;
- connector/rail positional tolerances.

Therefore `HDR-SMD_14P-P2.54` is an interface description, not an orderable BOM
line or safe footprint source.

## Exact reference candidate, not selected BOM

Harwin `M20-7810745` is a current exact prototype reference for the host side:

- female double-row `7+7`, `2.54 mm`, vertical SMT, dual entry;
- accepts `0.64-mm` square pins;
- `3.75-mm` height above PCB, `17.78 × 7.20 × 4.95 mm` body;
- gold contacts/terminations, `3 A/contact`, `-40…+105 °C`;
- manufacturer page reports distributor stock on 2026-08-17.

It is deliberately **not selected yet**: the U214 specimen must prove insertion
depth and installed rail height first. The active diagram consequently labels
the host connector `MPN TBD`.

## Closure experiment

1. Measure one production U214: pin size/exposed length, boss height, hole/thread
   depth, rail-contact planes and end-foot envelope.
2. Place `M20-7810745` or a dimensionally equivalent socket on a small dock
   coupon with adjustable spacers at the `56-mm` M2 pitch.
3. Verify full electrical contact without pin bottoming, housing preload or
   screw-induced bending over repeated install/remove cycles.
4. Freeze exact MPN, PCB footprint, rail height, screw MPN/length and tolerances
   only after the coupon pass.

## Sources

- [M5Stack U214 official product, schematic and model-size documents](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [M5Stack Cardputer-Adv official product, schematic and model-size documents](https://docs.m5stack.com/en/core/Cardputer-Adv)
- [Harwin M20-7810745 official product data](https://www.harwin.com/products/M20-7810745)
