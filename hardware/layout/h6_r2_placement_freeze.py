#!/usr/bin/env python3
"""Capture or verify the exact post-H6.0.1 footprint anchors.

The automatic seed placer is useful before routing, but after placement review
one local correction must not repack unrelated parts.  This manifest stores the
accepted anchor in KiCad nanometres for every footprint.  Run with KiCad's
bundled Python runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    import pcbnew  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("run with KiCad's bundled Python 3.9 runtime") from exc


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
FREEZE_PATH = ROOT / "hardware/layout/h6-r2-placement-freeze.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
MECHANICAL_REFERENCES = {"MH1", "MH2", "MH3", "MH4"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def board_path(project: str) -> Path:
    return ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"


def board_state(project: str) -> dict[str, tuple[int, int, float, str]]:
    board = pcbnew.LoadBoard(str(board_path(project)))
    return {
        footprint.GetReference(): (
            footprint.GetPosition().x,
            footprint.GetPosition().y,
            round(footprint.GetOrientationDegrees(), 3),
            "B.Cu" if footprint.IsFlipped() else "F.Cu",
        )
        for footprint in board.GetFootprints()
    }


def capture() -> dict:
    artifact = load(AUDIT_PATH)
    # The placement audit consumes this freeze and therefore hashes it.  Do not
    # copy that self-reference (or the reciprocal audit hash) back into the
    # freeze: either would create an impossible circular hash dependency.
    artifact["sources"].pop("placement_freeze", None)
    artifact["sources"].pop("placement_freeze_sha256", None)
    states = {project: board_state(project) for project in PROJECTS}
    errors = []
    count = 0
    for board in artifact["boards"]:
        project = board["project"]
        rows = {row["reference"]: row for row in board["placements"]}
        actual_references = set(states[project]) - MECHANICAL_REFERENCES
        if set(rows) != actual_references:
            errors.append(f"{project}: footprint-reference coverage mismatch")
            continue
        for reference, row in rows.items():
            x, y, rotation, side = states[project][reference]
            if row["side"] != side or row["rotation_deg"] != rotation:
                errors.append(f"{project}:{reference}: side/rotation mismatch")
            row["footprint_anchor_nm"] = [x, y]
            count += 1
    if errors:
        raise SystemExit("; ".join(errors))
    artifact["schema_version"] = 3
    artifact["artifact"] = "H6-R2 exact-placement freeze"
    artifact["freeze"] = {
        "status": "pass",
        "footprint_count": count,
        "coordinate_unit": "KiCad integer nanometres",
        "source_audit": str(AUDIT_PATH.relative_to(ROOT)),
        "rule": "all later seed generations restore these anchors unless an explicit reviewed placement_override replaces one",
    }
    return artifact


def verify() -> list[str]:
    artifact = load(FREEZE_PATH)
    errors = []
    count = 0
    for board in artifact["boards"]:
        project = board["project"]
        expected = {
            row["reference"]: (
                *row["footprint_anchor_nm"],
                row["rotation_deg"],
                row["side"],
            )
            for row in board["placements"]
        }
        actual = board_state(project)
        actual = {
            reference: state
            for reference, state in actual.items()
            if reference not in MECHANICAL_REFERENCES
        }
        if set(expected) != set(actual):
            errors.append(f"{project}: footprint-reference coverage mismatch")
            continue
        for reference in expected:
            if expected[reference] != actual[reference]:
                errors.append(
                    f"{project}:{reference}: actual={actual[reference]} expected={expected[reference]}"
                )
        count += len(expected)
    if count != artifact["freeze"]["footprint_count"]:
        errors.append(f"footprint count {count} does not match freeze summary")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    if args.write:
        artifact = capture()
        FREEZE_PATH.write_text(
            json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"H6-R2 placement freeze written: {artifact['freeze']['footprint_count']} exact anchors"
        )
        return 0
    errors = verify()
    if errors:
        raise SystemExit("stale H6 placement freeze: " + "; ".join(errors[:10]))
    print(f"H6-R2 placement freeze pass: {load(FREEZE_PATH)['freeze']['footprint_count']} exact anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
