# Leshy2 — schematic as code (tscircuit)

The schematic sheets are captured as [tscircuit](https://tscircuit.com) code (`.tsx`)
transcribed from the transcribe-ready net-lists in [`hardware/`](../). From one
source file tscircuit generates the **schematic image**, a **PCB**, a **netlist**,
and a **KiCad export** — so nothing is drawn by hand.

## Sheets

| File | Sheet | Source doc |
|------|-------|------------|
| `power.tsx` | 1 · Power | [hardware/power/power.md](../power/power.md) |

*(RF, MCU + buses, audio, expansion, indicators to follow.)*

## Render / export

Needs Node + [Bun](https://bun.sh) (the tscircuit CLI runs on Bun):

```bash
npm install           # once, installs @tscircuit/cli locally (runs on Bun)
npx tsci export power.tsx -f schematic-svg -o power-schematic.svg  # schematic image (of record)
npx tsci export power.tsx -f kicad_pcb     -o power.kicad_pcb      # KiCad PCB — full net connectivity, layout target
# also: pcb-svg, gerbers, kicad_zip, readable-netlist, STEP, glTF …
```

**Verify connectivity** with KiCad's own checker on the PCB / netlist, e.g.
`kicad-cli pcb drc power.kicad_pcb`.

## Notes

- **ICs/connectors** are generic `<chip>` with our logical pinout; 2-pin
  passive-ish parts (PPTC fuse, master switch, NTC) are resistor proxies.
  Real footprints / part numbers are assigned before the PCB.
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
