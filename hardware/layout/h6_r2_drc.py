#!/usr/bin/env python3
"""Run native DRC and bind its report to the exact board and rule inputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
CLI_CANDIDATES = (
    Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
    Path("/usr/bin/kicad-cli"),
    Path("/usr/local/bin/kicad-cli"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def provenance_path(report: Path) -> Path:
    return report.with_name(report.name + ".provenance.json")


def input_hashes(project: str, root: Path = ROOT) -> dict[str, str]:
    if project not in PROJECTS:
        raise ValueError(f"unknown H6 project: {project}")
    directory = root / "hardware/ecad/kicad" / project
    paths = [directory / f"{project}{suffix}" for suffix in (".kicad_pcb", ".kicad_pro", ".kicad_dru")]
    return {str(path.relative_to(root)): sha256(path) for path in paths}


def validate_receipt(receipt: dict, project: str, report_sha256: str, root: Path = ROOT) -> None:
    if receipt.get("schema_version") != 1 or receipt.get("project") != project:
        raise ValueError(f"{project}: DRC provenance does not match the project/schema")
    if receipt.get("exit_code") != 0:
        raise ValueError(f"{project}: DRC command did not complete successfully")
    if receipt.get("inputs_sha256") != input_hashes(project, root):
        raise ValueError(f"{project}: board or DRC rules changed since the DRC run")
    if receipt.get("report_sha256") != report_sha256:
        raise ValueError(f"{project}: DRC report differs from its provenance receipt")


def validate_provenance(report_path: Path, project: str, root: Path = ROOT) -> dict:
    receipt_path = provenance_path(report_path)
    if not receipt_path.is_file():
        raise ValueError(f"{project}: missing DRC provenance; rerun hardware/layout/h6_r2_drc.py")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    validate_receipt(receipt, project, sha256(report_path), root)
    return receipt


def run_drc(project: str, output: Path, *, root: Path = ROOT, cli: Path | None = None) -> dict:
    root = root.resolve()
    before = input_hashes(project, root)
    output = output.resolve()
    if output in {root / path for path in before} or provenance_path(output) in {root / path for path in before}:
        raise ValueError("DRC output must not overwrite a board or rule input")
    if cli is None:
        cli = next((path for path in CLI_CANDIDATES if path.is_file()), None)
    if cli is None:
        raise ValueError("KiCad CLI not found")
    board = root / "hardware/ecad/kicad" / project / f"{project}.kicad_pcb"
    output.parent.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    # A fresh temporary filename prevents a failed CLI run from reusing an old report.
    with tempfile.TemporaryDirectory(prefix=".h6-drc-", dir=output.parent) as directory:
        staged = Path(directory) / output.name
        command = [str(cli), "pcb", "drc", "--format", "json", "--severity-all", "-o", str(staged), str(board)]
        result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            raise ValueError(f"{project}: KiCad DRC failed ({result.returncode}): {result.stdout.strip()}")
        if input_hashes(project, root) != before:
            raise ValueError(f"{project}: board or DRC rules changed during the DRC run")
        if not staged.is_file():
            raise ValueError(f"{project}: KiCad DRC produced no report")
        report = json.loads(staged.read_text(encoding="utf-8"))
        if report.get("source") != board.name:
            raise ValueError(f"{project}: KiCad DRC source does not match the board")
        if not all(isinstance(report.get(key), list) for key in ("violations", "unconnected_items")):
            raise ValueError(f"{project}: incomplete KiCad DRC report")
        receipt = {
            "schema_version": 1,
            "project": project,
            "started_at_utc": started,
            "completed_at_utc": utc_now(),
            "inputs_sha256": before,
            "report_sha256": sha256(staged),
            "command": command,
            "exit_code": result.returncode,
            "kicad_version": report.get("kicad_version"),
        }
        staged_receipt = provenance_path(staged)
        staged_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        staged.replace(output)
        staged_receipt.replace(provenance_path(output))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", choices=PROJECTS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run_drc(args.project, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(f"{args.project}: captured {len(report['violations'])} DRC violations and {len(report['unconnected_items'])} unconnected items with exact input provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
