#!/usr/bin/env python3
"""One serial H6 validation/derived-refresh command; never regenerate a PCB.

Run with KiCad Python. --refresh updates derived audits and existing pictures,
not native boards. --check checks their freshness. Detailed process logs stay
under ignored work/, not in public documentation. Neither mode releases boards.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")


def commands(refresh: bool, directory: Path, tests: bool, python: str = sys.executable):
    """Dependency order is explicit; no shell and no native-writing seed mode."""
    mode = "--write" if refresh else "--check"
    def command(script, *args):
        return [python, "hardware/layout/" + script + ".py", *args]
    result = []
    if refresh:
        # Schematic endpoint edits invalidate the canonical/native name map.
        # Export before placement consumes it; no PCB update-from-schematic.
        cli = shutil.which("kicad-cli")
        if cli is None:
            bundled = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
            cli = str(bundled) if bundled.is_file() else "kicad-cli"
        for project, name in zip(PROJECTS, ("ui-netlist.xml", "rf-netlist.xml")):
            result.append([cli, "sch", "export", "netlist", "--format", "kicadxml",
                           "-o", str(directory/name), f"hardware/ecad/kicad/{project}/{project}.kicad_sch"])
        result.append(command("h6_r2_kicad_net_bindings", "--write",
                              "--ui-netlist", str(directory/"ui-netlist.xml"),
                              "--rf-netlist", str(directory/"rf-netlist.xml")))
        result += [command("h6_r2_placement", "--refresh-derived"),
                   command("h6_r2_placement_freeze", "--write"),
                   command("h6_r2_placement", "--refresh-derived")]
    else:
        result += [command("h6_r2_kicad_net_bindings", "--check"),
                   command("h6_r2_placement", "--check"),
                   command("h6_r2_placement_freeze", "--check")]
    result += [command("h6_r2_routing_policy", mode),
               command("h6_r2_manual_copper", "--refresh-derived" if refresh else "--check"),
               command("h6_r2_footprint_parity", mode),
               command("h6_r2_silkscreen_audit", mode),
               command("h6_r2_sma_solder_access", mode),
               command("h6_r2_mechanical_stack", *([] if refresh else ["--check"])),
               command("h6_r2_microcoax_service", *([] if refresh else ["--check"]))]
    if refresh:
        for project, name in zip(PROJECTS, ("ui-drc.json", "rf-drc.json")):
            result.append(command("h6_r2_drc", "--project", project, "--output", str(directory/name)))
        result.append(command("h6_r2_current_routing", "--write", "--ui-drc", str(directory/"ui-drc.json"),
                              "--rf-drc", str(directory/"rf-drc.json")))
    else:
        result.append(command("h6_r2_current_routing", "--check"))
    result.append(command("h6_r2_routing_render", mode))
    if tests:
        result.append([shutil.which("python3") or python, "-m", "unittest", "discover", "-s", "hardware/architecture/tests", "-q"])
        result.append([python, "-m", "unittest", "discover", "-s", "hardware/architecture/tests", "-p", "test_h6*.py", "-q"])
    return result


def board_hashes(root=ROOT):
    return {p: hashlib.sha256((root/f"hardware/ecad/kicad/{p}/{p}.kicad_pcb").read_bytes()).hexdigest()
            for p in PROJECTS}


def run_one(command, log, expected_boards):
    with log.open("x") as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    if board_hashes() != expected_boards:
        raise RuntimeError("A validation command changed a native PCB; stop and inspect the diff. No automatic rollback.")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}); see {log}")
    if "hardware/layout/h6_r2_drc.py" in command:
        report = json.loads(Path(command[command.index("--output")+1]).read_text())
        if report["violations"] or report["schematic_parity"]:
            raise RuntimeError(f"DRC/parity findings remain; see {log.parent}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--refresh", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--tests", action="store_true", help="Also run system architecture and native H6 tests")
    args = parser.parse_args()
    # A shared lock serializes this pipeline's KiCad CLI calls across invocations.
    work = ROOT/"work"
    work.mkdir(exist_ok=True)
    with (work/"h6-validation.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(1, "Another H6 validation is running; do not run KiCad CLI concurrently.\n")
        directory = Path(tempfile.mkdtemp(prefix="h6-validation-", dir=work))
        before = board_hashes()
        steps = commands(args.refresh, directory, args.tests)
        print(f"Logs: {directory}", flush=True)
        for index, command in enumerate(steps, 1):
            label = Path(command[1]).stem if command[1] != "-m" else "tests"
            print(f"[{index}/{len(steps)}] {label}", flush=True)
            try:
                run_one(command, directory/f"{index:02d}-{label}.log", before)
            except (OSError, RuntimeError) as error:
                parser.exit(1, str(error)+"\n")
        print("PASS: derived checks complete; both native PCB hashes unchanged. No fabrication release.")


if __name__ == "__main__":
    main()
