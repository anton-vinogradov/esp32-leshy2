#!/usr/bin/env python3
"""Run native DRC with schematic parity and bind its repository input snapshot.

Installed KiCad standard libraries/global tables and the CLI executable are an
explicit external-environment boundary, not implicitly covered by repo hashes.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
CLI_CANDIDATES = (
    Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
    Path("/usr/bin/kicad-cli"),
    Path("/usr/local/bin/kicad-cli"),
)
RECEIPT_SCHEMA = 2
REPORT_LIST_FIELDS = ("violations", "unconnected_items", "schematic_parity")
DRC_ARGUMENTS = ("pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o")
COMMAND_WORKING_DIRECTORY = "repository_root"
EXTERNAL_ENVIRONMENT = {
    "standard_libraries": "Installed KiCad standard footprint/symbol libraries are resolved by KiCad and are not content-hashed by this repository receipt.",
    "global_library_tables_and_variables": "User/global library tables and KiCad path variables remain external environment inputs; project fp-lib-table and sym-lib-table are hashed.",
    "cli": "The exact executed CLI path and its report kicad_version are recorded; the executable and external libraries are not fingerprinted or claimed reproducible across hosts.",
}
SHEET_FILE = re.compile(r'\(property\s+"Sheetfile"\s+("(?:\\.|[^"\\])*")')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def provenance_path(report: Path) -> Path:
    return report.with_name(report.name + ".provenance.json")


def relative_repository_path(value: str, root: Path, label: str) -> PurePosixPath:
    """Require a canonical repo-relative path; do not redact an executed command."""
    if (not isinstance(value, str) or not value or "\\" in value
            or any(ord(char) < 32 for char in value)):
        raise ValueError(f"{label}: expected a canonical repository-relative path")
    path = PurePosixPath(value)
    if (path.is_absolute() or str(path) != value or value == "."
            or any(part in (".", "..") for part in path.parts)):
        raise ValueError(f"{label}: expected a canonical repository-relative path")
    resolved = (root.resolve() / value).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"{label}: path resolves outside the repository")
    return path


def input_hashes(project: str, root: Path = ROOT) -> dict[str, str]:
    if project not in PROJECTS:
        raise ValueError(f"unknown H6 project: {project}")
    root = root.resolve()
    directory = root / "hardware/ecad/kicad" / project
    paths = {directory / f"{project}{suffix}" for suffix in (".kicad_pcb", ".kicad_pro", ".kicad_dru")}
    paths.update(directory / name for name in ("fp-lib-table", "sym-lib-table"))
    # Include all project sheets conservatively, and follow actual Sheetfile
    # references so a missing or moved child cannot silently leave the receipt.
    pending = {directory / f"{project}.kicad_sch", *directory.rglob("*.kicad_sch")}
    seen = set()
    while pending:
        path = pending.pop().resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"{project}: schematic input lies outside the repository: {path}")
        if path in seen:
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        for match in SHEET_FILE.finditer(text):
            child = json.loads(match.group(1))
            if not child or "${" in child:
                raise ValueError(f"{project}: unsupported schematic child path: {child!r}")
            pending.add(path.parent / child)
    paths.update(seen)
    # Over-inclusive by design: additions/deletions and either local footprint
    # library changing invalidate DRC, even when not used by this particular PCB.
    library = root / "hardware/ecad/libraries"
    local_footprints = set(library.rglob("*.kicad_mod"))
    if not local_footprints:
        raise ValueError(f"{project}: repository-controlled footprint inputs are missing")
    paths.update(local_footprints)
    paths.update(library.rglob("*.kicad_sym"))
    paths.add(library / "leshy2_r2.kicad_sym")
    resolved = {path.resolve() for path in paths}
    if any(not path.is_relative_to(root) for path in resolved):
        raise ValueError(f"{project}: controlled DRC input lies outside the repository")
    return {str(path.relative_to(root)): sha256(path) for path in sorted(resolved)}


def validate_report(report: dict, project: str) -> None:
    if not isinstance(report, dict) or report.get("source") != f"{project}.kicad_pcb":
        raise ValueError(f"{project}: KiCad DRC source does not match the board")
    if not all(isinstance(report.get(key), list) for key in REPORT_LIST_FIELDS):
        raise ValueError(f"{project}: incomplete KiCad DRC report; schematic_parity and other finding lists are required")
    if not isinstance(report.get("kicad_version"), str) or not report["kicad_version"].strip():
        raise ValueError(f"{project}: KiCad DRC report has no version evidence")


def validate_receipt(receipt: dict, project: str, report_sha256: str, root: Path = ROOT) -> None:
    if not isinstance(receipt, dict) or receipt.get("schema_version") != RECEIPT_SCHEMA or receipt.get("project") != project:
        raise ValueError(f"{project}: DRC provenance does not match the project/schema")
    if type(receipt.get("exit_code")) is not int or receipt["exit_code"] != 0:
        raise ValueError(f"{project}: DRC command did not complete successfully")
    board = Path("hardware/ecad/kicad") / project / f"{project}.kicad_pcb"
    command = receipt.get("command")
    if (receipt.get("schematic_parity_requested") is not True
            or receipt.get("command_working_directory") != COMMAND_WORKING_DIRECTORY
            or not isinstance(command, list) or len(command) != len(DRC_ARGUMENTS) + 3
            or not all(isinstance(item, str) and item for item in command)
            or command[1:-2] != list(DRC_ARGUMENTS) or command[-1] != str(board)):
        raise ValueError(f"{project}: DRC provenance lacks the exact schematic-parity command")
    staged = relative_repository_path(command[-2], root, "DRC command output")
    published = relative_repository_path(receipt.get("published_report_path"), root, "DRC published report")
    # The command records the actual temporary output, not the later promotion.
    # Bind both locations so a receipt cannot silently describe another output.
    if (staged.parent.parent != published.parent or staged.name != published.name
            or not re.fullmatch(r"\.h6-drc-[A-Za-z0-9_-]+", staged.parent.name)):
        raise ValueError(f"{project}: DRC staged output does not match the published report")
    counts = receipt.get("report_list_counts")
    if (receipt.get("required_report_fields") != list(REPORT_LIST_FIELDS)
            or not isinstance(counts, dict) or set(counts) != set(REPORT_LIST_FIELDS)
            or any(type(value) is not int or value < 0 for value in counts.values())):
        raise ValueError(f"{project}: DRC provenance lacks complete schematic-parity observation")
    if receipt.get("external_environment") != EXTERNAL_ENVIRONMENT:
        raise ValueError(f"{project}: DRC provenance has no explicit external-library boundary")
    if not isinstance(receipt.get("kicad_version"), str) or not receipt["kicad_version"].strip():
        raise ValueError(f"{project}: DRC provenance has no KiCad version")
    if receipt.get("inputs_sha256") != input_hashes(project, root):
        raise ValueError(f"{project}: board, rules, schematics or controlled libraries changed since the DRC run")
    if receipt.get("report_sha256") != report_sha256:
        raise ValueError(f"{project}: DRC report differs from its provenance receipt")


def validate_provenance(report_path: Path, project: str, root: Path = ROOT) -> dict:
    root = root.resolve()
    report_path = (root / report_path).resolve()
    if not report_path.is_relative_to(root):
        raise ValueError(f"{project}: DRC report must be inside the repository")
    receipt_path = provenance_path(report_path)
    if not receipt_path.is_file():
        raise ValueError(f"{project}: missing DRC provenance; rerun hardware/layout/h6_r2_drc.py")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    validate_receipt(receipt, project, sha256(report_path), root)
    if receipt["published_report_path"] != report_path.relative_to(root).as_posix():
        raise ValueError(f"{project}: DRC receipt names a different published report")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    validate_report(report, project)
    if (receipt["report_list_counts"] != {key: len(report[key]) for key in REPORT_LIST_FIELDS}
            or receipt["kicad_version"] != report["kicad_version"]):
        raise ValueError(f"{project}: DRC report observations differ from the provenance receipt")
    return receipt


def run_drc(project: str, output: Path, *, root: Path = ROOT, cli: Path | None = None) -> dict:
    root = root.resolve()
    before = input_hashes(project, root)
    output = (root / output).resolve()
    if not output.is_relative_to(root):
        raise ValueError("DRC output must be inside the repository; external output paths are unsupported")
    if output in {root / path for path in before} or provenance_path(output) in {root / path for path in before}:
        raise ValueError("DRC output must not overwrite a board, rule, schematic or controlled-library input")
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
        command = [str(cli), *DRC_ARGUMENTS, staged.relative_to(root).as_posix(), board.relative_to(root).as_posix()]
        result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            raise ValueError(f"{project}: KiCad DRC failed ({result.returncode}): {result.stdout.strip()}")
        if input_hashes(project, root) != before:
            raise ValueError(f"{project}: board, rules, schematics or controlled libraries changed during the DRC run")
        if not staged.is_file():
            raise ValueError(f"{project}: KiCad DRC produced no report")
        report = json.loads(staged.read_text(encoding="utf-8"))
        validate_report(report, project)
        receipt = {
            "schema_version": RECEIPT_SCHEMA,
            "project": project,
            "started_at_utc": started,
            "completed_at_utc": utc_now(),
            "inputs_sha256": before,
            "report_sha256": sha256(staged),
            "command": command,
            "command_working_directory": COMMAND_WORKING_DIRECTORY,
            "published_report_path": output.relative_to(root).as_posix(),
            "schematic_parity_requested": True,
            "required_report_fields": list(REPORT_LIST_FIELDS),
            "report_list_counts": {key: len(report[key]) for key in REPORT_LIST_FIELDS},
            "external_environment": dict(EXTERNAL_ENVIRONMENT),
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
    print(f"{args.project}: captured {len(report['violations'])} DRC violations, {len(report['unconnected_items'])} unconnected items and {len(report['schematic_parity'])} schematic-parity findings with repository input provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
