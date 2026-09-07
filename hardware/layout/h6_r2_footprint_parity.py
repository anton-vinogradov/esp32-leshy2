#!/usr/bin/env python3
"""Audit native pad geometry against the actual selected footprint libraries.

Read-only for PCB/library files. --write updates only the JSON audit. Library
edits are not automatically applied to routed boards. This checks pads, not
body/cutout correctness, electrical semantics or physical part qualification.
Run with KiCad's bundled Python.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    import pcbnew
except ImportError:
    pcbnew = None

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-footprint-pad-parity.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
STANDARD = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_pad_rows(actual, expected):
    """Keep multiplicities: four same-number shield tabs are four features."""
    encode = lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"))
    got, want = Counter(map(encode, actual)), Counter(map(encode, expected))
    return {"native_only": [json.loads(s) for s in sorted((got-want).elements())],
            "library_only": [json.loads(s) for s in sorted((want-got).elements())]}


def pad_rows(fp):
    def xy(v):
        # Canonical micrometres avoid sub-nm float conversion artifacts while
        # remaining much tighter than any PCB/assembly tolerance.
        return [round(pcbnew.ToMM(v.x), 3), round(pcbnew.ToMM(v.y), 3)]
    return [{"number": p.GetNumber(), "at_mm": xy(p.GetPosition()),
             "size_mm": xy(p.GetSize()), "drill_mm": xy(p.GetDrillSize()),
             "rotation_deg": round(p.GetOrientationDegrees() % 360, 3),
             "shape": int(p.GetShape()), "drill_shape": int(p.GetDrillShape()),
             "attribute": int(p.GetAttribute()), "layers": sorted(p.GetLayerSet().Seq()),
             "roundrect_ratio": round(p.GetRoundRectRadiusRatio(), 6)}
            for p in fp.Pads()]


def build():
    if pcbnew is None:
        raise RuntimeError("run with KiCad's bundled Python runtime")
    sources, boards, errors = {}, [], []
    for project in PROJECTS:
        path = ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
        board = pcbnew.LoadBoard(str(path))
        checked, deviations = [], []
        for native in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
            identity = native.GetFPID()
            nickname, name = str(identity.GetLibNickname()), str(identity.GetLibItemName())
            # add_mechanical_geometry() deliberately loads these eight holes
            # directly from this standard directory without a library nickname.
            # Resolve that exact controlled case only; do not guess other names.
            if (not nickname and native.GetReference() in {"MH1", "MH2", "MH3", "MH4"}
                    and name == "MountingHole_2.7mm_M2.5"):
                nickname = "MountingHole"
            if nickname in ("Leshy2", "Leshy2_R2"):
                directory = ROOT / f"hardware/ecad/libraries/{nickname}.pretty"
                source_label = str(directory.relative_to(ROOT) / (name + ".kicad_mod"))
            else:
                directory = STANDARD / (nickname + ".pretty")
                source_label = "kicad-standard/" + nickname + ".pretty/" + name + ".kicad_mod"
            library_path = directory / (name + ".kicad_mod")
            ref = native.GetReference()
            if not nickname or not name or not library_path.is_file():
                errors.append(f"{project}:{ref}: missing source {nickname}:{name}")
                continue
            sources[source_label] = sha(library_path)
            expected = pcbnew.FootprintLoad(str(directory), name)
            if expected is None:
                errors.append(f"{project}:{ref}: unreadable source {nickname}:{name}")
                continue
            # A separate scratch board owns the expected footprint. Never
            # mutate native, its nets, stored geometry or routed copper.
            scratch = pcbnew.BOARD()
            scratch.Add(expected)
            if native.IsFlipped():
                expected.Flip(pcbnew.VECTOR2I(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            expected.SetOrientationDegrees(native.GetOrientationDegrees())
            expected.SetPosition(native.GetPosition())
            delta = compare_pad_rows(pad_rows(native), pad_rows(expected))
            checked.append(ref)
            if delta["native_only"] or delta["library_only"]:
                deviations.append({"reference": ref, "footprint": f"{nickname}:{name}",
                                   "source": source_label, **delta})
        boards.append({"project": project, "board": str(path.relative_to(ROOT)),
                       "board_sha256": sha(path), "native_footprint_count": len(board.GetFootprints()),
                       "checked_references": checked, "deviations": deviations})
    count = sum(len(b["deviations"]) for b in boards)
    return {"schema_version": 1, "artifact": "H6-R2 native/library pad geometry parity",
            "status": "pass" if not errors and count == 0 else "open_native_library_drift",
            "fabrication_ready": False,
            "scope": "Pad number/multiplicity, transformed XY, size, angle, drill, layers, attribute, shape and roundrect ratio. Does not establish body fit, cutouts, sourcing, nets or complete fabrication readiness.",
            "coordinate_precision_mm": .001, "source_library_sha256": dict(sorted(sources.items())),
            "summary": {"native_footprints": sum(b["native_footprint_count"] for b in boards),
                        "checked_footprints": sum(len(b["checked_references"]) for b in boards),
                        "footprints_with_pad_geometry_drift": count, "lookup_errors": len(errors)},
            "errors": errors, "boards": boards}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    text = json.dumps(result, indent=2, sort_keys=False) + "\n"
    if args.write:
        OUTPUT.write_text(text)
    elif not OUTPUT.is_file() or OUTPUT.read_text() != text:
        raise SystemExit("stale native/library pad-parity audit; regenerate the read-only audit")
    print(json.dumps({"status": result["status"], **result["summary"]}))
    # --check means the report is reproducible, not that drift is cleared.
    # Always expose status; downstream release gates must require status=pass.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
