# PHY-0001 — U214 rear dock above the batteries

- Статус: **Проведено ревью; D принято `DEC-0057`, exact dock/HIL открыты**
- Дата: 2026-08-17
- Finding: [`FND-0068`](../findings/FND-0068-u214-envelope-missing-from-legacy-layout.md)
- Proposal: [`IMP-0048`](../improvements/IMP-0048-u214-dock-versus-sma-placement.md)
- Decision: [`DEC-0057`](../decisions/DEC-0057-u214-rear-dock-above-batteries.md)
- Mechanical facts: [`MEC-0001`](MEC-0001-u214-cap-bus-mechanical-interface.md)
- Exact battery update: [`PWR-0016`](../architecture/PWR-0016-keystone-1048p-holder-and-ntc-coupling.md)
- Generator: [`u214_rear_fit.py`](../../../hardware/product-design/u214_rear_fit.py)
- Render: [`PHY-0001-u214-rear-fit.svg`](img/PHY-0001-u214-rear-fit.svg)

## Проверенный результат

Official U214 and Cardputer-Adv STL use compatible product coordinates. В
assembled-position components получены следующие paper dimensions:

- Cardputer body: `84 × 54 × 19.676 mm` overall model envelope;
- U214 assembled shell: width `84 mm`, rear strip/edge height `15.281 mm`;
- U214 extends from host rear datum approximately `15.11 mm`;
- the original bare-cell screen used `18.6 mm`; exact `Keystone 1048P` plus
  installed-cell reference envelope is now `20.7 mm`, leaving `5.59 mm` paper
  depth reserve;
- U214 is L-shaped and wraps the host edge: a flat board header is not
  mechanically equivalent.

## Наложение на legacy rear face

The scaled candidate places U214 transversely above the battery holder:

- `75-mm` base board remains unchanged;
- `84-mm` U214 overhangs symmetrically by `4.5 mm` on each side;
- rear projection starts at `y=15 mm`; five top-SMA keep-outs end at `y=9.5
  mm`, leaving `5.5 mm` planar gap;
- U214 projection ends at `y=30.281 mm`; battery holder starts at `y=40 mm`,
  leaving `9.719 mm` service gap;
- exact `1048P` projection is `39.8 × 86.0 mm` at `(17.6, 40.0)` and leaves a
  `24.0 mm` lower board margin;
- old rear encoder at `x=30…45, y=20…33` collides and must move;
- the diagram shows the five RF-board SMA paths; four separate UI-board SMA
  paths remain outside this face and are unaffected;
- U214's end RP-SMA, HY2.0-4P and both screw accesses must remain outside case
  obstruction.

## Неплоское крепление

Rear placement is feasible only as a Cardputer-like raised dock rail:

1. recessed 2×7 female Cap-Bus header on the correct mating plane;
2. two screw bosses matching official structure geometry;
3. local rear-shell step/rail that the L-shaped U214 housing wraps around;
4. no metal/battery over the U214 GNSS ceramic antenna sky-view;
5. protected but reachable own RP-SMA and downstream Port A.

The exact header MPN, boss pitch/height and enclosure wall values are not
invented here. Official drawings now close the M2 `56-mm` centre pitch and
`14-mm` symmetric offsets, while `MEC-0001/FND-0069` keep connector MPN,
mating depth, rail height, screw length and tolerances at the specimen gate.

## Вывод

Rear-above-battery D is the accepted active working placement. It preserves all
all nine SMA paths, avoids increasing base width, and stays inside the exact
holder/cell depth envelope on paper. It requires relocating the legacy encoder and cannot reach
enclosure sign-off before the exact connector/rail/specimen gate.

## Sources

- [M5Stack U214 official documentation](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [M5Stack official U214/Cardputer-Adv STL files](https://github.com/m5stack/M5_Hardware)
