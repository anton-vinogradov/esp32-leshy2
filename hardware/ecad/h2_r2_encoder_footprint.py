#!/usr/bin/env python3
"""Reproduce the CURRENT R2 EC11E18244AU engineering mounting candidate.

Exact Alps Drawing No.2 fixes terminal/body axes. Rounded PTH holes and
annuli are our declared standard-JLC engineering choice, not an Alps land
pattern approval or measured solder-joint qualification. No R1/native writes.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "EC11E18244AU-ENGINEERING-PTH"
OUTPUT = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty" / (NAME + ".kicad_mod")
SOURCE_URL = "https://tech.alpsalpine.com/cms.media/product_catalog_ec_01_ec11e_en_611f078659.pdf"
SIGNAL_CENTRES = {"A": (-2.5, 7.5), "C": (0, 7.5), "B": (2.5, 7.5),
                  "D": (-2.5, -7), "E": (2.5, -7)}
MOUNT_CENTRES = ((-6.25, 0), (6.25, 0))
SHAFT_AXIS = (0, 0)
SLOT_NOMINAL = (2.0, 4.0)
MOUNT_COPPER = (2.8, 4.8)
SIGNAL_DRILL_NOMINAL = 1.1
SIGNAL_COPPER = 2.0


def footprint_text():
    lines = [f'''(footprint "{NAME}"
  (version 20260206)
  (generator "pcbnew")
  (layer "F.Cu")
  (descr "Alps EC11E18244AU Drawing No.2 exact 12.5mm mounting pitch, 5 terminal axes and nominal body11.7x12.0; origin=shaft. Engineering standard-PTH profile: MP oval2.0x4.0/Cu2.8x4.8, signals drill1.1/Cu2.0. MP conditional aperture containment; signals only coaxial aperture comparison, not lead/position proof. NOT manufacturer-approved rounded holes or production solder-strength acceptance; see h6-r2-encoder-fit-candidate.json. Solder BOTH metal mounting lugs despite empty nets, seat body flush and level, do not wash. No undocumented locating holes or borrowed STEP. {SOURCE_URL}")
  (tags "Alps EC11E18244AU exact-axes engineering-standard-PTH")
  (property "Reference" "REF**" (at 0 -9.25) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "EC11E18244AU" (at 0 9.75) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Leshy2ActuatorAxisLocalMm" "0,0" (at 0 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08)) (hide yes)))
  (attr through_hole)
  (fp_rect (start -5.85 -6) (end 5.85 6) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
  (fp_circle (center 0 0) (end 3 0) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
  (fp_line (start -0.4 0) (end 0.4 0) (stroke (width 0.08) (type default)) (layer "F.Fab"))
  (fp_line (start 0 -0.4) (end 0 0.4) (stroke (width 0.08) (type default)) (layer "F.Fab"))
  (fp_rect (start -7.9 -8.25) (end 7.9 8.75) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))''']
    for name, (x, y) in SIGNAL_CENTRES.items():
        lines.append(f'  (pad "{name}" thru_hole circle (at {x:g} {y:g}) (size 2 2) (drill 1.1) (layers "*.Cu" "*.Mask"))')
    for x, y in MOUNT_CENTRES:
        lines.append(f'  (pad "MP" thru_hole oval (at {x:g} {y:g}) (size 2.8 4.8) (drill oval 2 4) (layers "*.Cu" "*.Mask"))')
    return "\n".join([*lines, ")", ""])


def build():
    return {OUTPUT: footprint_text()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for path, text in build().items():
        if args.write:
            path.write_text(text, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"stale current R2 encoder footprint: {path}")
    print("current R2 EC11 engineering footprint reproduces source; fabrication acceptance remains separate")


if __name__ == "__main__":
    main()
