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
npm install           # once, installs @tscircuit/cli locally
npx tsci export power.tsx -f schematic-svg -o power-schematic.svg
npx tsci export power.tsx -f pcb-svg        -o power-pcb.svg
# also supported: kicad-project, gerbers, STEP, glTF, netlist …
```

## Notes

- **ICs/connectors** are generic `<chip>` with our logical pinout; 2-pin
  passive-ish parts (PPTC fuse, master switch, NTC) are resistor proxies.
  Real footprints / part numbers are assigned before the PCB.
- **RF PCB layout** (impedance-controlled feeds, ground planes, antenna
  keep-outs) is done in **KiCad** on the exported project — the auto-router is
  not used for the RF chains.
- Connectivity is by **net name** (`net.BAT`, `net.GND`, …), matching the
  "Key nets" sections of each sheet doc.

*Part of [Leshy2](../../README.md) · MIT.*
