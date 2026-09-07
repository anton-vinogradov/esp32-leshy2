#!/usr/bin/env python3
"""Reproduce the project-local JAE edge-silkscreen variant; never edit KiCad.

The KiCad 10.0.5 source below is content-pinned, not fetched implicitly. Supply
that exact standard-library file with --source on other installations. A changed
upstream definition needs an explicit geometry review, not automatic acceptance.

Only the footprint identifier/description and three F.SilkS lines change. Pads,
drills, mask/paste settings, Fab, courtyard, properties and 3D model are retained.
JAE SJ121836 Rev.3 p2 puts PCB edge at local Y=3.10 (locator -1.95 + 5.05).
Ending the 0.12-mm strokes at Y=2.88 leaves 0.16 mm of ink-to-edge clearance.
This is a board-placement-specific graphic adaptation, not a new production MPN.

Upstream: KiCad libraries, CC-BY-SA 4.0 with the KiCad Libraries Exception:
https://www.kicad.org/libraries/license/
https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_USB.pretty/USB_C_Receptacle_JAE_DX07S016JA1R1500.kicad_mod
"""

import argparse
import hashlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
BASE_NAME = "USB_C_Receptacle_JAE_DX07S016JA1R1500"
VARIANT_NAME = BASE_NAME + "_EdgeSilk"
SOURCE_SHA256 = "6f6c1ac1efdec9479814ac5d8ea8a4453387b58099cae99fb835fc09e2a6dd00"
DEFAULT_SOURCE = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_USB.pretty") / (BASE_NAME + ".kicad_mod")
OUTPUT = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty" / (VARIANT_NAME + ".kicad_mod")
ATTRIBUTION = (
    "Leshy2 R2 edge-silk variant of KiCad " + BASE_NAME + "; "
    "original pads/drills/Fab/courtyard/mask/paste/3D unchanged; "
    "only front F.Silk removed and two side ends shortened to Y=2.88 for PCB edge Y=3.10; "
    "JAE SJ121836 Rev.3 p2; checked 2026-09-07; "
    "KiCad CC-BY-SA 4.0 with Libraries Exception https://www.kicad.org/libraries/license/; "
    "source SHA256 " + SOURCE_SHA256
)


def build(source: bytes) -> str:
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("unreviewed JAE source SHA256; do not accept an upstream geometry change implicitly")
    text = source.decode("utf-8")
    header = '(footprint "' + BASE_NAME + '"'
    if not text.startswith(header):
        raise ValueError("unexpected standard footprint identity")
    text = text.replace(header, '(footprint "' + VARIANT_NAME + '"', 1)
    descriptions = list(re.finditer(r'^\t\(descr "([^"\\]*)"\)$', text, re.MULTILINE))
    if len(descriptions) != 1:
        raise ValueError("expected one standard footprint description")
    match = descriptions[0]
    text = text[:match.start()] + '\t(descr "' + match.group(1) + '; ' + ATTRIBUTION + '")' + text[match.end():]

    edits = []
    for match in re.finditer(r'^\t\(fp_line\n.*?^\t\)\n', text, re.MULTILINE | re.DOTALL):
        block = match.group(0)
        if '(layer "F.SilkS")' not in block:
            continue
        if '(start -4.58 3.71)\n\t\t(end 4.58 3.71)' in block:
            edits.append((match.start(), match.end(), "", "front"))
        for side in ("-4.58", "4.58"):
            old = f'(start {side} 2.76)\n\t\t(end {side} 3.71)'
            if old in block:
                new = f'(start {side} 2.76)\n\t\t(end {side} 2.88)'
                edits.append((match.start(), match.end(), block.replace(old, new, 1), side))
    if {row[3] for row in edits} != {"front", "-4.58", "4.58"} or len(edits) != 3:
        raise ValueError("expected exactly three reviewed JAE edge-silk strokes")
    for start, end, replacement, _ in reversed(edits):
        text = text[:start] + replacement + text[end:]
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = build(args.source.read_bytes())
    except (OSError, ValueError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}; only reviewed edge-silk variant")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    print("ok: JAE local edge-silk reproduces pinned KiCad source with exactly three graphic edits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
