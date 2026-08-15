# Leshy2 — layout render spec

*Read this in: **English** · [Русский](layout-spec.ru.md)*

The fixed spec for (re)drawing the two-board clamshell layout render ([`layout-clamshell.en.svg`](img/layout-clamshell.en.svg) / [`.ru.svg`](img/layout-clamshell.ru.svg)). It is a **stage-5 artifact on par with the render itself**: the render must always be reproducible from this spec, and when the two disagree, **this spec wins and the render is regenerated**. Footprints are the real datasheet bodies of the parts chosen in the [tscircuit sheets](../hardware/tscircuit/).

## 1. Canvas & structure

- **Portrait, three rows.** Row 1 = main board (**outer front** | **inner**); Row 2 = C5 board (**inner** | **outer back**); Row 3 = side **cross-section** + antenna table + legend.
- **Bilingual** — one SVG for EN, one for RU, same geometry.
- **To scale** — both boards **~75 × 150 mm**, drawn at one fixed px/mm; every part is drawn at its real footprint (§6–§7).

## 2. The two boards

- **Board size: ~75 × 150 mm each; ~34 mm total clamshell thickness.**
- **Clamshell.** Inner faces face each other — components live in the gap, protected. Outer faces carry only the display + controls (front) and the battery (back), **plus the antenna SMA across the top of each**.
- **Mezzanine gap.** The standoff height is **≥ the tallest inner-face component**, so the two boards' inner parts clear each other: `h_A(x,y) + h_B(x,y) ≤ gap` everywhere. The **nRF24 modules are the tallest inner parts** — mounted **low** (soldered / short pins, DIV-style, **not** on tall 2×4 sockets) they stand only **~5–7 mm**, so the gap follows the **DIV-measured 11 mm gap** (a tall socket would add ~8 mm and blow the thickness budget — don't use one).
- **Mounting.** Four **M2.5** corner holes, aligned on both boards; **every part and antenna is kept clear of them**.

## 3. Views & the mirror rule

- Four faces are drawn: main outer, main inner, C5 inner, C5 outer, plus the cross-section.
- **Inner faces are true back views — mirrored left↔right.** An inner face is the front flipped about the vertical axis: **top / bottom stay, left and right swap**. A part on the device's **left** edge is therefore drawn on the **right** of the inner view (and vice versa) — the two views describe the same physical board, not an X-ray *through* it.
- **Cross-section** is the thickness stack front→back (display · main board · gap · C5 board · battery), with the gap ≥ the tallest inner part (§2).

## 4. Interface vs component (colour)

- **Interface — blue frame.** Anything a human contacts: **screws an antenna, plugs a cable, presses, inserts a card, slides, speaks / listens, touches the screen.** The **battery holder** is an interface (you load the cells) — green fill + blue frame.
- **Component — grey frame.** Internal, never touched: MCUs, radios, ICs, decoders, `BT1`, the mezzanine.
- **Indicators** are their own marks, not framed boxes: TX-live LEDs = small amber dots, RGB status = an R/G/B pie.

## 5. Placement rules

- **Outer front — only what you look at or press:** display, D-pad, BACK / OPTIONS, encoder + F1 / F2 (left edge), PTT + STOP (right edge), speaker + mic (lower), the LED row. Antennas across the top.
- **Outer back:** the battery holder (centred) + antennas across the top.
- **All connectors / switches / service buttons go on the INNER faces**, each **at the board edge it exits** (a part mid-board can't reach a case slot), reached through slots in the case edge.
- **Direction arrow on every external port** — a small red arrow **pointing out from the part into the margin, never onto a label** (checked). Bottom-edge ports → arrow down; side-edge ports → arrow out to that side.

## 6. Proportions — real footprints

Every box ≈ its **real PCB footprint** (§7), to the one common scale — **a connector is never drawn larger than a module**. Shapes:

| Shape | Drawn as | Examples |
|---|---|---|
| `module` | rounded rectangle (RF-shield hint) | WROOM, nRF24, SA868, LoRa, GPS |
| `IC` | small rectangle | CC1101, Si4732, PCA9555, chargers, LDOs |
| `connector-rect` | small rectangle at an edge | USB-C, microSD, jack, Grove, slide |
| `connector-round` | circle (hex hint) | SMA |
| `cylinder` | rounded capsule | 18650 cell |
| `holder` | large rounded rectangle | 2× 18650 holder |
| `button-square` | small square | D-pad, encoder, tact buttons |
| `led` | small dot / pie | TX-live, RGB |
| `display` | large rectangle (active-area inset) | ST7796 |

## 7. Component placement table

Footprints are the **real datasheet body / footprint W × H in mm** (length is the larger dimension). `main` = S3 main board, `C5` = C5 board; `F` = outer face, `I` = inner face.

| Component / group | Footprint mm | Shape | Board · face | Position | Dir. |
|---|---|---|---|---|:--:|
| **ST7796 4.0″ display + touch** | 62 × 99 *(active 56 × 84)* | display | main · F | upper, centred | — |
| **5-way D-pad** | 12 × 12 | button | main · F | lower-centre | — |
| **BACK / OPTIONS** | 6 × 6 ea | button | main · F | flank the D-pad | — |
| **Encoder (EC11)** | 12 × 13.4 | button | main · F | left edge | — |
| **F1 / F2** | 6 × 6 | button | main · F | left edge, below encoder | — |
| **PTT / panic STOP** | 6 × 6 | button | main · F | right edge | — |
| **Speaker (mylar)** | 14 × 20 | grille | main · F | lower-left | out |
| **Mic (MEMS)** | 2.95 × 3.76 | port | main · F | lower-right | out |
| **TX-live LEDs ×7** | ~1.6 (0603) | led | main · F | row below the display | — |
| **RGB status (WS2812B)** | 5 × 5 | led | main · F | end of the LED row | — |
| **5× SMA** (Wi-Fi, CC1101, SA868, LoRa, Si4732) | 6.35 ⌀ | conn-round | main · F | top edge | up |
| **GPS patch** | ~15 × 15 | patch | main · F | top edge | up |
| **ESP32-S3-WROOM-1U** | 18 × 19.2 | module | main · I | interior | — |
| **CC1101 + SP4T** | 4 × 4 (+ switch) | IC grp | main · I | interior | — |
| **SA868-U** | 19 × 35.6 | module | main · I | interior (long) | — |
| **SX1262 / E22 (LoRa)** | 14 × 20 | module | main · I | interior | — |
| **Si4732 + PAM8302** | 5.3 × 8.2 + 3 × 4.9 | IC grp | main · I | interior | — |
| **GPS (ATGM336H)** | 15.7 × 13.1 | module | main · I | interior | — |
| **Buses** (74HC138 + 2× PCA9555) | ~10 × 4, ~8 × 4.4 | IC grp | main · I | interior | — |
| **Backlight driver** | small IC | IC | main · I | interior | — |
| **3.5 mm jack (PJ-320)** | 6 × 12.5 | conn-rect | main · I | side edge *(mirrored)* | out |
| **2× Grove** | 8.6 × 5.9 | conn-rect | main · I | opposite side edge *(mirrored)* | out |
| **microSD (push-push)** | 15 × 14.6 | conn-rect | main · I | bottom edge | down |
| **RESET / BOOT** | 6 × 6 | button | main · I | bottom edge | down |
| **u.FL ×5 → outer SMA** | 2.6 × 2.6 | — | main · I | interior (to the top SMA) | — |
| **ESP32-C5-WROOM-1U** | 18 × 21.2 | module | C5 · I | interior | — |
| **3× nRF24 + PA/LNA** | 15.5 × 29 *(~5–7 mm mounted low — tallest inner part)* | module | C5 · I | interior, spread | — |
| **IR driver** | small IC | IC | C5 · I | interior | — |
| **74HC139** (nRF CS) | ~10 × 4 | IC | C5 · I | interior | — |
| **PCA9555** | ~8 × 4.4 | IC | C5 · I | interior | — |
| **BQ25887 charger** | 4 × 4 | IC | C5 · I | interior | — |
| **Power** (2× MP2315, TPS7A2033, S-8252A) | 2.8 × 2.9 ea | IC grp | C5 · I | interior | — |
| **USB-C ×2 (J1, J2)** | 8.94 × 7.35 | conn-rect | C5 · I | bottom edge | down |
| **Master slide (MSK-12C02)** | 9 × 4 | conn-rect | C5 · I | bottom edge | down |
| **C5 RESET / C5 BOOT** | 6 × 6 | button | C5 · I | bottom edge | down |
| **2× 18650 holder** | 40 × 78 *(cells 18.6 × 65)* | holder | C5 · F | centred | — |
| **BT1 (battery conn.)** | small | conn-rect | C5 · I | by the holder | — |
| **4× SMA** (3× nRF24, C5 5 GHz) | 6.35 ⌀ | conn-round | C5 · F | top edge | up |
| **IR TX / RX** | ~3 × 4 / 5 × 5 | emitter | C5 · F | top edge (with the antennas) | up |
| **Mezzanine connector** | ~ | mez | both · I | interior | — |
| **4× M2.5 mounting holes** | ⌀ 2.7 | hole | both | four corners | — |

*Rules of thumb baked into the table: modules dominate the inner faces; the display and the 2× 18650 dominate the outer faces; connectors and ICs are small; the nRF-on-header height drives the mezzanine gap.*

## 8. Automated checks — all must read 0 before the render is used

The generator parses its own finished SVG and refuses to ship a render that fails any of these (never checked by eye):

1. **Overlap** — no rectangle / text collisions.
2. **Accessibility** — every **interface** (blue) on an **inner** face sits at a board edge (a buried connector / switch / button can't reach the case).
3. **Arrow-on-label** — no direction arrow lands on any label.
4. **Mezzanine gap** — the cross-section gap ≥ the tallest inner-face part.

---

*Part of [Leshy2](../README.md) · stage 5 (see [§5](../README.md#5-external-design--controls)) · MIT.*
