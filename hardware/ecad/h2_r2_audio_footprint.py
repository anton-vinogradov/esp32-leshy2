#!/usr/bin/env python3
"""Current R2-only ordinary SMT TRRS footprint; never regenerate historical R1.

Same Sky SJ-4351X-SMT 2024-09-12 p2 manufacturer recommended PCB TOP VIEW.
The TS variant has no terminal 6. Origin is Connector Edge at the plug axis;
it is deliberately not courtyard centre. Exact drawing facts are independently
asserted in test_h6_r2_sj43515ts.py. This generator writes only one library file,
never a native board, schematic, symbol or manufacturing approval.
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/SJ-43515TS-SMT-TR.kicad_mod"
SOURCE_URL = "https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf"
SOURCE_SHA256 = "b0284d377faf3e8fea7fe46acd0980c7cb952e215da7c5a1258e4070376d45ed"
FOOTPRINT = '''(footprint "SJ-43515TS-SMT-TR"
  (version 20240108)
  (generator "h2_r2_audio_footprint")
  (layer "F.Cu")
  (descr "Same Sky SJ-43515TS-SMT-TR; SJ-4351X-SMT 2024-09-12 page 2 PCB TOP VIEW, manufacturer-derived Leshy2 R2 definition. Origin Connector Edge on plug axis, NOT courtyard centre; mouth X=-1.50, insertion +X. Five SMT contacts, two unnumbered NPTH locators, no board-body cutout. Conservative nominal body envelope, not STEP or final enclosure proof. https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf")
  (tags "Same-Sky SJ-43515TS-SMT-TR top-mount TRRS tip-switch")
  (property "Reference" "REF**" (at 8.5 -6.2) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "SJ-43515TS-SMT-TR" (at 8.5 6.2) (layer "F.Fab") (effects (font (size 0.7 0.7) (thickness 0.10))))
  (attr smd)
  (fp_rect (start 0 -3) (end 15.5 3.8) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -1.5 -2.5) (end 0 2.5) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
  (fp_line (start -3 0) (end -1.5 0) (stroke (width 0.10) (type default)) (layer "F.Fab"))
  (fp_line (start -2 -0.3) (end -1.5 0) (stroke (width 0.10) (type default)) (layer "F.Fab"))
  (fp_line (start -2 0.3) (end -1.5 0) (stroke (width 0.10) (type default)) (layer "F.Fab"))
  (fp_rect (start -1.75 -5.25) (end 18.75 5.25) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
  (fp_text user "INSERT +X" (at 7 0) (layer "F.Fab") (effects (font (size 0.65 0.65) (thickness 0.10))))
  (pad "1" smd rect (at 0.6 3.5) (size 2 3) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "2" smd rect (at 13 3.5) (size 2 3) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "3" smd rect (at 5.3 -3.5) (size 2 3) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "4" smd rect (at 3.5 3.5) (size 2 3) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "5" smd rect (at 17 -0.8) (size 3 2) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "" np_thru_hole circle (at 4.5 0) (size 1.9 1.9) (drill 1.9) (layers "*.Cu" "*.Mask"))
  (pad "" np_thru_hole circle (at 11.5 0) (size 1.9 1.9) (drill 1.9) (layers "*.Cu" "*.Mask"))
)
'''


def build() -> str:
    return FOOTPRINT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build()
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}; R2 footprint only")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    print("ok: current SJ-43515TS five-contact SMT footprint reproduces exact source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
