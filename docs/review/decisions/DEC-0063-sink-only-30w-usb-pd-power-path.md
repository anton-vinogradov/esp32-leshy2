# DEC-0063 — sink-only USB-PD up to 30 W

> Later allocation: this decision itself consumes no direct GPIO, but
> `DEC-0086` subsequently uses GPIO47 for encoder phase B.

- Статус: **Принято владельцем; распространено; frontend проведён ревью**
- Owner choice: `IMP-0053/B`
- Дата: 2026-08-18
- Context: [`PWR-0003`](../architecture/PWR-0003-charge-power-path-options.md)
- Exact fit: [`PWR-0004`](../architecture/PWR-0004-accepted-usb-pd-front-end.md)
- Propagation review: [`REV-0005R`](../reviews/REV-0005R-usb-pd-decision-propagation.md)

## Decision

1. Product USB-C is a power consumer only. It accepts 5-V fallback, 9 V at
   3 A and 15 V at 2 A, for a maximum negotiated input of 30 W.
2. Source, power-bank, 20-V PDO, PPS and charger OTG modes are not product
   capabilities and remain disabled.
3. The first exact active path is `TPS25751DREFR` plus `BQ25798RQMR`.
   The D variant is selected because its protected 20-V/5-A path is integrated;
   the S variant would add external path FETs and their gate-drive proof.
4. `CAT24C512WI-GT3` is a mandatory dedicated address-0x50 configuration
   EEPROM. `TVS2200DRVR` is the exact first-target VBUS shunt clamp.
5. Product USB D-/D+ stay directly connected to S3 GPIO19/20. TPS USB/LD pins
   are tied low and BQ DP/DM is disconnected; neither IC taps the data pair.
6. S3 controls TPS over existing `SYS_I2C0`. TPS IRQ shares the existing
   pull-up active-low system IRQ; GPIO47 remains free. TPS locally owns the
   charger and configuration EEPROM.
7. Reset defaults fail closed: EEPROM WP is pulled high and charger CE is
   pulled high. A valid policy explicitly opens a signed update window and
   actively enables charging.
8. Initial charge current is capped at 2 A. Increasing it requires exact cell,
   admission/protection, thermal and HIL evidence; the 5-A charger rating is
   not a product charge-rate promise.

## Cost and product consequence

At the checked 100-piece public price tier, the four selected active/protection
parts total approximately USD 6.52 before passives, connector, PCB, tax and
assembly. The accepted path is estimated at roughly USD 2–3 more per device
than the complete 5-V-only alternative. The owner accepts that premium for
source headroom and faster bounded charging; it does not authorize extra
source-mode hardware.

## Remaining I3 boundary

This decision closes the USB-PD frontend, not all of `I3`. Exact USB-C
receptacle/USB2 ESD, inductor/passives, cell admission/protection/gauge/
balancing, downstream rails/load switches, AON source/hold-up and calculated
loss/thermal/fault/HIL evidence remain open.

## Reopen rule

Reopen if the exact image tool/firmware becomes unavailable, sink-only behavior
cannot be independently recovered from a blank/corrupt EEPROM, the shared IRQ
cannot meet its latency proof, or the installed cost/thermal/area exceeds the
accepted product envelope.
