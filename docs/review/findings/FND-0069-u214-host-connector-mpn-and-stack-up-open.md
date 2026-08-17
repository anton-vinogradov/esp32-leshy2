# FND-0069 — U214 host connector MPN and mechanical stack-up are open

- Статус: **Несоответствие обнаружено; exact part/specimen closure открыт**
- Серьёзность: connector-footprint / retention / enclosure-fit blocker
- Обнаружено: 2026-08-17
- Decision: [`DEC-0057`](../decisions/DEC-0057-u214-rear-dock-above-batteries.md)
- Facts: [`MEC-0001`](../product-design/MEC-0001-u214-cap-bus-mechanical-interface.md)

## Несоответствие

M5Stack publishes `HDR-SMD_14P-P2.54` for both U214 and Cardputer-Adv, but that
generic label does not identify an orderable connector, footprint, connector
sex, body height or mating depth. Product photographs resolve the sex and M2
retention concept, not the missing production stack-up.

Selecting an arbitrary `2×7 2.54-mm` socket now could produce electrical pin
compatibility while still bottoming the U214 pins, holding the M2 bosses off the
rail or bending the boards when the screws are tightened.

## Corrected boundary

`DEC-0057` closes placement, not exact mechanics. Until the coupon/specimen gate
in `MEC-0001` passes:

- host receptacle remains `MPN TBD`;
- no production footprint, rail height or screw length is normative;
- the physical generator must draw the connector and M2 retention separately;
- KiCad and enclosure sign-off remain blocked on this interface.
