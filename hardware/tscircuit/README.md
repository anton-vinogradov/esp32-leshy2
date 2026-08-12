# Leshy2 — schematic as code (tscircuit)

The schematic sheets are captured as [tscircuit](https://tscircuit.com) code (`.tsx`)
transcribed from the transcribe-ready net-lists in [`hardware/`](../). From one
source file tscircuit generates the **schematic image**, a **PCB**, a **netlist**,
and a **KiCad export** — so nothing is drawn by hand.

## Sheets

| File | Sheet | Source doc |
|------|-------|------------|
| `power.tsx` | 1 · Power | [power.md](../power/power.md) |
| `c5-buses.tsx` | 2 · MCU + buses | [c5-buses.md](../c5-buses/c5-buses.md) |
| `rf.tsx` | 3 · RF chains | [rf.md](../rf/rf.md) |
| `audio.tsx` | 4 · Audio | [audio.md](../audio/audio.md) |
| `expansion.tsx` | 5 · Expansion + GPS | [expansion.md](../expansion/expansion.md) |
| `indicators.tsx` | 6 · Indicators / IO | [indicators.md](../indicators/indicators.md) |

All six sheets are captured **and merged into one board** — see below.

## Combined board — fab-drafted

All six sheets are realized with **real parts**: every IC/module/connector pulls its
manufacturer-verified footprint + pinout from the LCSC/JLCPCB database
(`footprint="jlcpcb:C…"`); only mechanical/placeholder parts stay geometric.
`board.tsx` merges them into one `<board>` — the sheets stitch by shared `net.NAME`
(the whole SPI/I²C bus, the power rails, the chip-selects, the interrupts, the C5 link,
the SP4T select). Colliding refdes are renamed on merge (`U20`→`m_U20`/`rf_U20`,
`Y1`→`rf_Y1`/`a_Y1`, `Rbias`→`rf_Rbias`/`a_Rbias`). **174 components.**

| File | What |
|------|------|
| `board.tsx` | the whole device in one board — edit the sheets, then re-merge |
| `board-sch.svg` | whole-board schematic image |
| `board.kicad_pcb` | **KiCad PCB — the layout target (connectivity carried; not yet routed)** |

Next: **place & route in KiCad** (RF feeds / ground / antenna keep-outs by hand), then gerbers.

## Render / export

Needs Node + [Bun](https://bun.sh) (the tscircuit CLI runs on Bun):

```bash
npm install           # once, installs @tscircuit/cli locally (runs on Bun)
# Sheets use footprint="jlcpcb:C…" -> the parts engine (network) must be ON.
# Do NOT pass --disable-parts-engine, or the real footprints won't resolve:
npx tsci export board.tsx -f kicad_pcb     -o board.kicad_pcb      # whole-board PCB (layout target)
npx tsci export board.tsx -f schematic-svg -o board-sch.svg       # whole-board schematic
# also: pcb-svg, gerbers, kicad_zip, readable-netlist, STEP, glTF …
```

**Verify connectivity** with KiCad's DRC. On the *un-placed / un-routed* merged board the
connectivity signal is **`schematic_parity` = 0** (the PCB netlist matches the schematic — no
accidental merges or breaks). Its `unconnected_items` (ratsnest) and `shorting_items` (pads of
different nets physically overlapping because nothing is placed yet) are **both artifacts of the
pre-layout board**, not real defects — they clear once parts are placed and routed:
`kicad-cli pcb drc --format json -o board.drc.json board.kicad_pcb`.

## Notes

- **Real footprints** are engine-pulled by LCSC part number (the parts engine /
  network must be on to export). Remaining **placeholders** to swap before fab: the
  18650 holder, 3.5 mm jack, electret mic, speaker, buzzer, RESET/BOOT/PTT buttons,
  the nRF24 / SA868 module lands and the CC1101 balun; LEDs are plain 0603 (pick the
  real amber part at BOM time). Each sheet's header comment lists its exact parts + `⚠`.
- **Still to draw before the PCB** — endpoints intentionally off-sheet today:
  the 7 RF envelope detectors that feed the TX-live LEDs (`TXDET_*`), the
  external display-module connector (`LCD_*`), the antenna feeds (`ANT_*`),
  and the C5 USB VBUS ESD stub (`VBUS_C5`).
- **RF PCB layout** (impedance-controlled feeds, ground planes, antenna
  keep-outs) is done in **KiCad** on the exported project — the auto-router is
  not used for the RF chains.
- Connectivity is by **net name** (`net.BAT`, `net.GND`, …), matching the
  "Key nets" sections of each sheet doc.
- **Schematic of record = the `.tsx` + `*-schematic.svg`** (connectivity is
  correct there). tscircuit's `kicad_sch` export currently drops the wires
  (dangling labels — fails KiCad ERC), so it is **not** committed; the
  KiCad **`.kicad_pcb`** carries the real net connectivity and is the layout
  target.

*Part of [Leshy2](../../README.md) · MIT.*
