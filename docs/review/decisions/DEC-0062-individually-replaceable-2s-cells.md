# DEC-0062 — two individually replaceable 18650 cells retained

- Статус: **Частично superseded `DEC-0064`: два слота и safety intent сохранены; series-specific mechanics reopened**
- Owner choice: `IMP-0052/B`
- Дата: 2026-08-18
- Context: [`PWR-0002`](../architecture/PWR-0002-i3-power-prerequisite-audit.md)
- Propagation review: [`REV-0005Q`](../reviews/REV-0005Q-battery-format-decision-propagation.md)

## Decision

1. ~~Leshy2 keeps two physical 18650 slots in a 2S electrical arrangement.~~
   The mandatory electrical arrangement is reopened by `DEC-0064`; the two
   physical slots remain required.
2. Each cell is individually accessible and replaceable; the product does not
   require a welded/sealed pack assembly.
3. This is a retained product capability, not permission to accept an arbitrary
   pair. Every supported cell has an exact profile; unknown geometry/chemistry/
   voltage remains disconnected and visible as unsupported.
4. Correct-polarity contact must be established mechanically before electrical
   admission. Reverse insertion must remain open-circuit before the battery
   manager's absolute-maximum pins; software detection after connection is not
   sufficient.
5. Both cell voltages/presence and temperature are observed before pack CHG/DSG
   FETs close. A large voltage/SOC/impedance/profile mismatch is refused, not
   repaired by force charging or called normal balancing.
   Under a controlled-1S choice this means each cell is observed before its
   own path closes, and a second cell is checked for safe sharing before it
   joins the bus; the first admitted slot need not be disconnected merely
   because the other is absent.
6. Replacing only one cell is allowed only when the resulting pair passes the
   same admission envelope. Otherwise the UI requires replacing/conditioning
   the pair and keeps the power path open.
7. Removal of either cell, contact bounce and reconnect cannot create reverse
   charging, uncontrolled inrush, TX restart or accessory backfeed. Data-loss
   handling and early-removal detection/hold-up are mandatory I3/I4 proofs.
8. At least one cell-independent fuse/protection layer, a pack manager with
   per-cell protection/balancing/current/temperature evidence and a keyed or
   recessed retained battery compartment are required. Exact cells, contacts,
   holder/door and manager/FETs remain I3/I8 selections.
   `DEC-0064` generalizes this to a topology-appropriate manager: series
   balancing for 2S, or per-slot isolation, bounded precharge and cross-charge
   prevention for controlled 1S.

## Consequences

- The legacy open plastic holder is not accepted merely because the cells stay
  separate. Its geometry becomes a reference for volume only.
- `BQ25887 + S-8252A` is not restored. It still lacks the selected power path,
  real SOC gauge and pre-connect/reverse/mismatch boundary.
- The rear U214 dock remains accepted; later mechanics must preserve safe cell
  access without making installed-cap removal a live-cell short/tool hazard.
- The selected charger must support safe instant-on/battery supplement and
  must never energize a reversed/absent slot through its BAT path.

## Reopen rule

If exact mechanically polarity-safe individual-cell contacts cannot be sourced
or verified inside the product envelope, the decision returns to the owner;
the implementation must not silently fall back to an ordinary open holder.
