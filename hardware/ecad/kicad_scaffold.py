#!/usr/bin/env python3
"""Generate and verify the reviewed H2.1 KiCad project scaffold.

The scaffold deliberately contains no circuit symbols yet.  H2.1 establishes
project/PCB boundaries, sheet files and repository-owned library resolution;
functional circuit population starts at H2.2.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CONTRACT = ECAD / "H2-sheet-contract.json"
PROJECTS_ROOT = ECAD / "kicad"
LIBRARIES = ECAD / "libraries"
MANIFEST = ECAD / "generated/H2-kicad-scaffold.json"
NAMESPACE = uuid.UUID("71522917-8c72-42b6-b650-13be42c428fc")


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def schematic(sheet_id: str) -> str:
    return f'''(kicad_sch
\t(version 20250114)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{stable_uuid(f'sheet:{sheet_id}')}")
\t(paper "A4")
\t(lib_symbols)
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''


def project_file(project_id: str) -> str:
    data = {
        "board": {},
        "boards": [],
        "cvpcb": {},
        "erc": {
            "rule_severities": {
                "lib_symbol_mismatch": "ignore",
            }
        },
        "libraries": {},
        "meta": {"filename": f"{project_id}.kicad_pro", "version": 1},
        "net_settings": {"classes": [], "meta": {"version": 3}},
        "pcbnew": {},
        "schematic": {},
        "sheets": [],
        "text_variables": {
            "LESHY2_STAGE": "H2.1",
            "LESHY2_PCB_PROJECT": project_id,
        },
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def symbol_library() -> str:
    return '''(kicad_symbol_lib
\t(version 20251024)
\t(generator "kicad_symbol_editor")
\t(generator_version "10.0")
)
'''


def sym_table() -> str:
    return '''(sym_lib_table
  (version 7)
  (lib (name "Leshy2") (type "KiCad") (uri "${KIPRJMOD}/../../libraries/leshy2.kicad_sym") (options "") (descr "Repository-controlled Leshy2 exact symbols"))
)
'''


def fp_table() -> str:
    return '''(fp_lib_table
  (version 7)
  (lib (name "Leshy2") (type "KiCad") (uri "${KIPRJMOD}/../../libraries/Leshy2.pretty") (options "") (descr "Repository-controlled Leshy2 exact footprints"))
)
'''


def expected_files(contract: dict) -> dict[Path, str]:
    controlled_symbol_library = LIBRARIES / "leshy2.kicad_sym"
    populated_ui10 = ECAD / "generated/H2-UI10-S3-core.json"
    outputs: dict[Path, str] = {
        controlled_symbol_library: (
            controlled_symbol_library.read_text(encoding="utf-8")
            if populated_ui10.is_file() and controlled_symbol_library.is_file()
            else symbol_library()
        ),
        LIBRARIES / "Leshy2.pretty/README.md": (
            "# Leshy2 controlled footprints\n\n"
            "Exact manufacturer-derived footprints are added and reviewed with "
            "their first circuit sheet in H2.2–H2.4.\n"
        ),
    }
    for project in contract["projects"]:
        project_id = project["id"]
        project_dir = PROJECTS_ROOT / project_id
        outputs[project_dir / f"{project_id}.kicad_pro"] = project_file(project_id)
        outputs[project_dir / "sym-lib-table"] = sym_table()
        outputs[project_dir / "fp-lib-table"] = fp_table()
        for sheet_id in project["sheets"]:
            filename = f"{project_id}.kicad_sch" if sheet_id == project["root"] else f"{sheet_id}.kicad_sch"
            outputs[project_dir / filename] = schematic(sheet_id)
    return outputs


def build_manifest(contract: dict, outputs: dict[Path, str]) -> dict:
    projects = []
    for project in contract["projects"]:
        project_id = project["id"]
        root_file = f"{project_id}.kicad_sch"
        child_files = [f"{sheet}.kicad_sch" for sheet in project["sheets"] if sheet != project["root"]]
        projects.append(
            {
                "id": project_id,
                "physical_board": project["board"],
                "root_sheet_id": project["root"],
                "root_file": root_file,
                "child_sheet_files": child_files,
                "sheet_count": len(project["sheets"]),
                "project_file": f"{project_id}.kicad_pro",
                "symbol_table": "sym-lib-table",
                "footprint_table": "fp-lib-table",
            }
        )
    return {
        "schema_version": 1,
        "stage": "H2.1",
        "status": "reviewed_scaffold",
        "authority": {"baseline": "R1", "lifecycle": "historical_pre_r2_sheet_scaffold", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "source": str(CONTRACT.relative_to(REPO)),
        "project_model": contract["project_model"],
        "projects": projects,
        "summary": {
            "project_count": len(projects),
            "physical_board_count": len(projects),
            "sheet_file_count": sum(project["sheet_count"] for project in projects),
            "repository_symbol_libraries": ["hardware/ecad/libraries/leshy2.kicad_sym"],
            "repository_footprint_libraries": ["hardware/ecad/libraries/Leshy2.pretty"],
            "pcb_files_created": 0,
            "circuit_symbols_placed": 0,
        },
        "scope": {
            "complete": [
                "one independent KiCad project per reviewed physical PCB",
                "all reviewed sheet files exist",
                "all projects resolve the same repository-controlled symbol and footprint libraries",
                "every schematic file parses and passes empty-sheet ERC in KiCad 10",
            ],
            "deferred": [
                "sheet hierarchy symbols and circuit population (H2.2-H2.4)",
                "exact manufacturer symbols and footprints as each circuit is populated",
                "full populated-project ERC closure (H2.6)",
                "all PCB placement, routing, fabrication and purchasing",
            ],
        },
        "generated_files": sorted(str(path.relative_to(REPO)) for path in outputs),
    }


def load() -> tuple[dict, dict[Path, str], str]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("stage") != "H2.0.2" or contract.get("status") != "reviewed":
        raise ValueError("H2.1 requires the reviewed H2.0.2 sheet contract")
    outputs = expected_files(contract)
    manifest = build_manifest(contract, outputs)
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return contract, outputs, manifest_text


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found; H2.1 native-format validation cannot run")


def kicad_check(outputs: dict[Path, str]) -> None:
    cli = find_kicad_cli()
    schematic_paths = sorted(path for path in outputs if path.suffix == ".kicad_sch")
    ui_root_review = ECAD / "generated/H2-UI-root-interface.json"
    ui_project_dir = PROJECTS_ROOT / "LESHY2-UI"
    reviewed_ui_paths = {
        path for path in schematic_paths
        if path.parent == ui_project_dir
    } if ui_root_review.is_file() else set()
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-kicad-") as temp:
        temp_dir = Path(temp)
        staged: dict[Path, Path] = {}
        for path, content in outputs.items():
            staged_path = temp_dir / path.relative_to(REPO)
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_text(
                path.read_text(encoding="utf-8") if path.suffix == ".kicad_sch" else content,
                encoding="utf-8",
            )
            staged[path] = staged_path
        reports = temp_dir / "reports"
        reports.mkdir()
        for index, path in enumerate(schematic_paths):
            if path in reviewed_ui_paths:
                continue
            report = reports / f"{index:02d}.json"
            result = subprocess.run(
                [cli, "sch", "erc", "--format", "json", "--severity-all", "--exit-code-violations", "-o", str(report), str(staged[path])],
                text=True,
                capture_output=True,
            )
            if result.returncode:
                raise RuntimeError(f"KiCad ERC/parser rejected {path.relative_to(REPO)}:\n{result.stdout}{result.stderr}")
        with tempfile.TemporaryDirectory(prefix="leshy2-h2-sym-") as sym_temp:
            result = subprocess.run(
                [cli, "sym", "upgrade", "--force", "--output", sym_temp, str(staged[LIBRARIES / "leshy2.kicad_sym"])],
                text=True,
                capture_output=True,
            )
            if result.returncode:
                raise RuntimeError(f"KiCad rejected controlled symbol library:\n{result.stdout}{result.stderr}")
        if reviewed_ui_paths:
            result = subprocess.run(
                [sys.executable, str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            if result.returncode:
                raise RuntimeError(
                    "KiCad rejected reviewed H2.2.1 UI hierarchy:\n"
                    f"{result.stdout}{result.stderr}"
                )
    print(f"ok: KiCad parsed {len(schematic_paths)} schematics and the controlled symbol library")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--kicad-check", action="store_true")
    args = parser.parse_args()
    _, outputs, manifest_text = load()
    if args.write:
        for path, content in outputs.items():
            if path.suffix == ".kicad_sch" and path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(manifest_text, encoding="utf-8")
        print(f"wrote {len(outputs)} H2.1 KiCad scaffold files and {MANIFEST.relative_to(REPO)}")
    else:
        stale = [
            path
            for path, content in outputs.items()
            if not path.is_file()
            or (path.suffix != ".kicad_sch" and path.read_text(encoding="utf-8") != content)
        ]
        if not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8") != manifest_text:
            stale.append(MANIFEST)
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: {len(outputs)} H2.1 KiCad scaffold files are current")
    if args.kicad_check:
        kicad_check(outputs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
