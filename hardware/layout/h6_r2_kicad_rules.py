#!/usr/bin/env python3
"""Generate the checked KiCad custom rules for the two R2 boards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
OUTPUTS = {
    "LESHY2-UI-R2": ROOT / "hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_dru",
    "LESHY2-RF-R2": ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_dru",
}


BASE_RULES = {
    "LESHY2-UI-R2": """# These named parts are deliberately mounted on a routed board edge.  Their
# manufacturer land patterns cross Edge.Cuts; all other copper keeps the normal
# 0.20 mm project clearance.
(rule "UI named edge-mount copper"
  (condition "A.Reference == 'D11' || A.Reference == 'J3' || A.Reference == 'J5' || A.Reference == 'J7' || A.Reference == 'J9' || A.Reference == 'J11' || A.Reference == 'J12' || A.Reference == 'J14' || A.Reference == 'J16' || A.Reference == 'SW18' || A.Reference == 'SW19'")
  (constraint edge_clearance (min -3mm)))

# Locator and retention holes are part of these manufacturer footprints.  Only
# same-footprint hole-to-pad checks receive the package-specific minimum.
(rule "UI USB and side-switch internal hole geometry"
  (condition "(A.Reference == 'J9' && B.Reference == 'J9') || (A.Reference == 'J11' && B.Reference == 'J11') || (A.Reference == 'SW1' && B.Reference == 'SW1') || (A.Reference == 'SW2' && B.Reference == 'SW2') || (A.Reference == 'SW18' && B.Reference == 'SW18') || (A.Reference == 'SW19' && B.Reference == 'SW19') || (A.Reference == 'SW20' && B.Reference == 'SW20') || (A.Reference == 'SW21' && B.Reference == 'SW21')")
  (constraint hole_clearance (min 0.09mm)))

(rule "UI edge-component assembly silk"
  (severity ignore)
  (condition "A.Reference == 'J5' || A.Reference == 'SW18' || A.Reference == 'SW19'")
  (constraint silk_clearance))
""",
    "LESHY2-RF-R2": """# Named edge components intentionally cross Edge.Cuts.  Ordinary copper retains
# the 0.20 mm board rule; this exception is not available to routed tracks.
(rule "RF named edge-mount copper"
  (condition "A.Reference == 'J1' || A.Reference == 'J4' || A.Reference == 'J5' || A.Reference == 'J6' || A.Reference == 'J7' || A.Reference == 'J8' || A.Reference == 'J9' || A.Reference == 'J11' || A.Reference == 'SW1' || A.Reference == 'SW2'")
  (constraint edge_clearance (min -3mm)))

(rule "RF USB and side-switch internal hole geometry"
  (condition "(A.Reference == 'J4' && B.Reference == 'J4') || (A.Reference == 'SW1' && B.Reference == 'SW1') || (A.Reference == 'SW2' && B.Reference == 'SW2')")
  (constraint hole_clearance (min 0.09mm)))

# TI's REF0038A recommended land pattern has a 0.125 mm local gap between the
# two exposed power lands.  The exception is restricted to the single package.
(rule "TPS25751 REF0038A internal exposed-pad gap"
  (condition "A.Reference == 'U3' && B.Reference == 'U3'")
  (constraint clearance (min 0.12mm)))

(rule "RF edge-switch assembly silk"
  (severity ignore)
  (condition "A.Reference == 'SW1' || A.Reference == 'SW2'")
  (constraint silk_clearance))

# The interboard connector is on the inner face and the SMT battery holder is
# on the outer face.  J12's two empty locator holes pass through the board under
# the holder body without a protruding pin.
(rule "J12 locator holes under opposite-face battery holder"
  (condition "(A.Reference == 'J12' && B.Reference == 'BT1') || (A.Reference == 'BT1' && B.Reference == 'J12')")
  (constraint courtyard_clearance (min -1mm)))
""",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def net_condition(names: list[str], *, track_only: bool = False) -> str:
    clauses = " || ".join(f"A.NetName == '{name}'" for name in names)
    prefix = "A.Type == 'Track' && " if track_only else ""
    return prefix + f"({clauses})"


def render(project: str, policy: dict, audit: dict) -> str:
    rows = [row for row in audit["rows"] if row["project"] == project]
    rf = sorted(row["kicad_net"] for row in rows if row["routing_class"] == "RF_CONTROLLED")
    usb = sorted(row["kicad_net"] for row in rows if row["routing_class"] == "USB_DIFFERENTIAL")
    geometries = policy["stackup_binding"]["outer_layer_geometries"]
    rf_geometry = geometries["RF_50R_CPWG"]
    usb_geometry = geometries["USB_90R_DIFFERENTIAL"]
    all_controlled = sorted(rf + usb)
    return (
        "(version 1)\n\n"
        + BASE_RULES[project].rstrip()
        + "\n\n# Generated H6 controlled-impedance rules.  Values are the exact current\n"
        + "# JLC06161H-3313 calculator result; recheck immediately before ordering.\n"
        + f"(rule \"H6 outer RF 50R CPWG {rf_geometry['trace_width_mil']:.2f}mil width {rf_geometry['coplanar_gap_mil']:.2f}mil gap\"\n"
        + "  (layer outer)\n"
        + f"  (condition \"{net_condition(rf, track_only=True)}\")\n"
        + f"  (constraint track_width (min {rf_geometry['trace_width_mil']:.2f}mil) (opt {rf_geometry['trace_width_mil']:.2f}mil) (max {rf_geometry['trace_width_mil']:.2f}mil))\n"
        + f"  (constraint clearance (min {rf_geometry['coplanar_gap_mil']:.2f}mil)))\n\n"
        + f"(rule \"H6 outer USB 90R {usb_geometry['trace_width_mil']:.2f}mil width {usb_geometry['pair_gap_mil']:.2f}mil gap\"\n"
        + "  (layer outer)\n"
        + f"  (condition \"{net_condition(usb, track_only=True)}\")\n"
        + f"  (constraint track_width (min {usb_geometry['trace_width_mil']:.2f}mil) (opt {usb_geometry['trace_width_mil']:.2f}mil) (max {usb_geometry['trace_width_mil']:.2f}mil))\n"
        + f"  (constraint diff_pair_gap (min {usb_geometry['pair_gap_mil']:.2f}mil) (opt {usb_geometry['pair_gap_mil']:.2f}mil) (max {usb_geometry['pair_gap_mil']:.2f}mil)))\n\n"
        + "(rule \"H6 controlled impedance stays on outer layers\"\n"
        + "  (layer inner)\n"
        + f"  (condition \"{net_condition(all_controlled)}\")\n"
        + "  (constraint disallow track via))\n"
    )


def build() -> dict[Path, str]:
    policy = load(POLICY)
    audit = load(AUDIT)
    if audit.get("status") != "pass":
        raise ValueError("routing-policy audit is not passing")
    return {path: render(project, policy, audit) for project, path in OUTPUTS.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build()
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale KiCad rules: " + ", ".join(stale))
            return 1
    print("H6-R2 KiCad rules pass: exact RF/USB outer-layer geometry on both boards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
