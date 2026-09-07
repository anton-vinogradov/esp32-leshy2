#!/usr/bin/env python3
"""Reproduce only the CURRENT R2 B3S nominal body/actuator footprint.

The historical h2_ui_controls_indicators generator writes Leshy2.pretty and
must retain its immutable R1 basis. This module owns only the separate
Leshy2_R2:B3S-1100P file: no symbols, PCB, placement, net or report writes.
Physical pad records remain byte-identical to the pre-datum R2 pattern.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/B3S-1100P.kicad_mod"
SOURCE_URL = "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3s.pdf"
ACTUATOR_AXIS_LOCAL_MM = (0.0, -0.92)
BODY_SIZE_MM = (6.0, 6.6)


def footprint_text():
    # Omron p2 TOP pad view fixes the symmetric 4.5-mm signal-row midpoint.
    # Keep the legacy manufacturing origin; it is not the visible actuator.
    return '''(footprint "B3S-1100P"
	(version 20260206)
	(generator "pcbnew")
	(layer "F.Cu")
	(descr "OMRON B3S p2 With Ground Terminal / TOP view: nominal body X6.0 Y6.6; 3.3-mm actuator at legacy local [0,-0.92]. Exact current R2 pads and courtyard retained; manufacturer numbering4/3 upper,2/1 lower,ground5. Nominal datum correction only, not full assembly qualification. https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3s.pdf")
	(property "Reference" "REF**" (at 0 -4 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "B3S-1100P" (at 0 4 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
	(property "Leshy2ActuatorAxisLocalMm" "0,-0.92" (at 0 -0.92 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08)) (hide yes)))
	(attr smd)
	(fp_rect (start -3.000 -4.220) (end 3.000 2.380) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
	(fp_circle (center 0.000 -0.920) (end 1.650 -0.920) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
	(fp_line (start -0.400 -0.920) (end 0.400 -0.920) (stroke (width 0.08) (type default)) (layer "F.Fab"))
	(fp_line (start 0.000 -1.320) (end 0.000 -0.520) (stroke (width 0.08) (type default)) (layer "F.Fab"))
	(fp_rect (start -5.000 -4.620) (end 5.000 4.280) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
	(pad "4" smd rect (at -3.980 -3.170) (size 1.550 1.300) (layers "F.Cu" "F.Paste" "F.Mask"))
	(pad "3" smd rect (at 3.980 -3.170) (size 1.550 1.300) (layers "F.Cu" "F.Paste" "F.Mask"))
	(pad "2" smd rect (at -3.980 1.330) (size 1.550 1.300) (layers "F.Cu" "F.Paste" "F.Mask"))
	(pad "1" smd rect (at 3.980 1.330) (size 1.550 1.300) (layers "F.Cu" "F.Paste" "F.Mask"))
	(pad "5" smd rect (at 0.000 3.170) (size 1.300 1.700) (layers "F.Cu" "F.Paste" "F.Mask"))
)
'''


def build():
    return {OUTPUT: footprint_text()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--check", action="store_true")
    operation.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for path, text in build().items():
        if args.write:
            path.write_text(text, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"stale current R2 B3S footprint: {path}")
    print("CURRENT R2 B3S nominal body/actuator footprint: PASS (one file; no PCB writes)")


if __name__ == "__main__":
    main()
