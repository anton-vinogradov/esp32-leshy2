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

## Combined board

`board.tsx` merges all six sheets into a single `<board>`: the sheets stitch
together by shared `net.NAME` — the whole `SPI_MOSI`/`SPI_SCK`/`SPI_MISO` bus,
`I2C`, the power rails, the chip-selects and the interrupts all connect across
sheets automatically. Colliding refdes are renamed on merge
(`U20`→`m_U20`/`rf_U20`, `Y1`→`rf_Y1`/`a_Y1`). 133 components, 131 nets.

| File | What |
|------|------|
| `board.tsx` | the whole device in one board — edit the sheets, then re-merge |
| `board-sch.svg` | whole-board schematic image |
| `board.kicad_pcb` | **KiCad PCB with full net connectivity — the layout target** |

Next: assign real footprints/part numbers, then place & route in KiCad.

## Render / export

Needs Node + [Bun](https://bun.sh) (the tscircuit CLI runs on Bun):

```bash
npm install           # once, installs @tscircuit/cli locally (runs on Bun)
npx tsci export power.tsx -f schematic-svg -o power-schematic.svg  # schematic image (of record)
npx tsci export power.tsx -f kicad_pcb     -o power.kicad_pcb      # KiCad PCB — full net connectivity, layout target
npx tsci export board.tsx -f kicad_pcb     -o board.kicad_pcb      # the MERGED whole-board PCB (layout target)
# also: pcb-svg, gerbers, kicad_zip, readable-netlist, STEP, glTF …
```

**Verify connectivity** with KiCad's own checker on the PCB / netlist, e.g.
`kicad-cli pcb drc power.kicad_pcb`.

## Notes

- **ICs/connectors** are generic `<chip>` with our logical pinout; 2-pin
  passive-ish parts (PPTC fuse, master switch, NTC) are resistor proxies.
  Real footprints / part numbers are assigned before the PCB.
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
