#!/usr/bin/env python3
"""Capture and classify the native KiCad ERC result for every H2 project."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
OUTPUT = ECAD / "generated/H2-REV61-native-erc.json"
PROJECTS = {
    "LESHY2-UI": ECAD / "kicad/LESHY2-UI/LESHY2-UI.kicad_sch",
    "LESHY2-RF": ECAD / "kicad/LESHY2-RF/LESHY2-RF.kicad_sch",
    "LESHY2-LORA-CAP-01": ECAD / "kicad/LESHY2-LORA-CAP-01/LESHY2-LORA-CAP-01.kicad_sch",
    "L2-DISP-ADP-001-A": ECAD / "kicad/L2-DISP-ADP-001-A/L2-DISP-ADP-001-A.kicad_sch",
}
SUPPRESSED_COUNTS = {
    "LESHY2-UI": 390,
    "LESHY2-RF": 682,
    "LESHY2-LORA-CAP-01": 27,
    "L2-DISP-ADP-001-A": 2,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found")


def validate_project_policy(root: Path) -> Path:
    project = root.with_suffix(".kicad_pro")
    settings = json.loads(project.read_text(encoding="utf-8"))
    severities = settings.get("erc", {}).get("rule_severities", {})
    if severities != {"lib_symbol_mismatch": "ignore"}:
        raise ValueError(f"{project.name} must suppress exactly lib_symbol_mismatch, got {severities}")
    return project


def native_snapshot() -> tuple[list[dict], str, dict[str, str]]:
    cli = find_kicad_cli()
    version = subprocess.run([cli, "version"], text=True, capture_output=True, check=True).stdout.strip()
    rows = []
    sources: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h261-") as temp:
        for project_id, root in PROJECTS.items():
            project_file = validate_project_policy(root)
            report = Path(temp) / f"{project_id}.json"
            result = subprocess.run(
                [cli, "sch", "erc", "--format", "json", "--severity-all", "-o", str(report), str(root)],
                text=True, capture_output=True,
            )
            if result.returncode or not report.is_file():
                raise RuntimeError(f"KiCad ERC failed for {project_id}:\n{result.stdout}{result.stderr}")
            data = json.loads(report.read_text(encoding="utf-8"))
            violations = [item for sheet in data.get("sheets", []) for item in sheet.get("violations", [])]
            classes = Counter((item.get("severity", "unknown"), item.get("type", "unknown")) for item in violations)
            rows.append({
                "project": project_id,
                "root": str(root.relative_to(REPO)),
                "native_violation_count": len(violations),
                "classification": [
                    {"severity": severity, "type": kind, "count": count}
                    for (severity, kind), count in sorted(classes.items())
                ],
                "scoped_suppression": {
                    "rule": "lib_symbol_mismatch",
                    "reason": "all symbols are repository-generated and the shared library is independently checked against the exact union of embedded definitions",
                    "covered_local_symbols": SUPPRESSED_COUNTS[project_id],
                },
            })
            sources[str(project_file.relative_to(REPO))] = sha256(project_file)
            for schematic in sorted(root.parent.glob("*.kicad_sch")):
                sources[str(schematic.relative_to(REPO))] = sha256(schematic)
    return rows, version, sources


def build() -> tuple[str, dict]:
    rows, version, sources = native_snapshot()
    total = sum(row["native_violation_count"] for row in rows)
    if total:
        raise ValueError(f"native ERC is not empty: {total} violations")
    manifest = {
        "schema_version": 1,
        "stage": "H2.6.1",
        "status": "reviewed_native_erc_snapshot",
        "tool": {"name": "kicad-cli", "version": version},
        "method": "fresh sequential native ERC for every complete root hierarchy with one narrowly scoped generated-library rule suppression",
        "source_hashes": {
            **sources,
            str((ECAD / "libraries/leshy2.kicad_sym").relative_to(REPO)): sha256(ECAD / "libraries/leshy2.kicad_sym"),
        },
        "projects": rows,
        "summary": {
            "project_count": len(rows),
            "native_error_or_warning_count": total,
            "suppressed_generated_library_comparisons": sum(SUPPRESSED_COUNTS.values()),
            "other_suppressed_rules": 0,
        },
        "corrected_findings": [{
            "id": "H2.6.1-F01",
            "finding": "raw ERC was obscured by one lib_symbol_mismatch warning per locally generated component",
            "correction": "all four projects now suppress only that rule while h2_symbol_library.py independently proves exact shared/embedded symbol equality",
        }],
        "open_findings": [],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content, manifest = build()
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
    elif not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
        print(f"stale: {OUTPUT.relative_to(REPO)}")
        return 1
    else:
        print(f"ok: H2.6.1 native ERC snapshot is current; {manifest['summary']['native_error_or_warning_count']} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
