#!/usr/bin/env python3
"""Bounded, copy-only KRT benchmark; never promotes copper to production.

Use normal Python for the controller; native KiCad checks run in its Python.
Engine runtimes must already be installed. Results and logs stay under work/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
LAYOUT = ROOT / "hardware/layout"
KICAD_PYTHON = Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3")
PROFILE = LAYOUT / "h6-r2-autorouter-profile.json"


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified_sources(case):
    changed = [name for name, digest in case["baseline_sha256"].items()
               if sha(ROOT / name) != digest]
    if changed:
        raise ValueError("Production inputs changed: " + ", ".join(changed))


def restore_dependencies(baseline, candidate, hashes, board_relative):
    """Discard changed/deleted engine dependencies; never replace copper."""
    changed = []
    for name, digest in hashes.items():
        if name == str(board_relative):
            continue
        target = candidate / name
        if not target.is_file() or sha(target) != digest:
            changed.append(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(baseline / name, target)
    return changed


def select_best(runs):
    """Only complete checked candidates compete; prefer fewer vias, then length."""
    valid = [row for row in runs if row.get("geometry_pass")]
    return min(valid, key=lambda row: (row["validation"]["new_vias"],
               row["validation"]["new_trace_length_mm"], row["end_to_end_seconds"])) if valid else None


def execute(command, log, timeout, env=None):
    start = time.monotonic()
    with Path(log).open("w") as stream:
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                   env=env, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            code = "timeout"
    return {"exit_code": code, "seconds": round(time.monotonic() - start, 3)}


def prepare_fixture(request_path):
    """Move one selected component in a disposable baseline, never production."""
    import pcbnew
    from collections import Counter
    from h6_r2_drc import input_hashes, run_drc
    from h6_r2_route_candidate import _item_uuid, _native_copper, _pads

    req = read(request_path)
    root = Path(req["baseline"]).resolve()
    if not root.is_relative_to((ROOT / "work").resolve()) or root.name != "baseline":
        raise ValueError("Fixture must be an isolated benchmark baseline under work/")
    case, project = read(req["case"]), req["project"]
    ref, dx, dy = req["move"]
    dx, dy = float(dx), float(dy)
    if not all(-1 <= value <= 1 for value in (dx, dy)) or (dx, dy) == (0, 0):
        raise ValueError("Fixture move must be nonzero and bounded to +/-1 mm per axis")
    if ref not in {pad.split(".")[0] for row in case["nets"] for pad in row["exact_ref_pads"]}:
        raise ValueError("Fixture component is outside selected endpoints")
    path = root / "hardware/ecad/kicad" / project / (project + ".kicad_pcb")
    if sha(path) != case["baseline_sha256"][str(path.relative_to(root))]:
        raise ValueError("Fixture source is not the expected original board")
    dependencies = input_hashes(project, root)
    old, board = pcbnew.LoadBoard(str(path)), pcbnew.LoadBoard(str(path))
    footprint = board.FindFootprintByReference(ref)
    before = footprint.GetPosition()
    delta = pcbnew.VECTOR2I(round(dx * 1e6), round(dy * 1e6))
    footprint.SetPosition(before + delta)
    pcbnew.SaveBoard(str(path), board)
    new = pcbnew.LoadBoard(str(path))
    def positions(b):
        return {_item_uuid(p): (fp.GetReference(), p.GetPosition().x, p.GetPosition().y)
                for fp in b.GetFootprints() for p in fp.Pads()}
    expected = {key: (r, x + (delta.x if r == ref else 0), y + (delta.y if r == ref else 0))
                for key, (r, x, y) in positions(old).items()}
    # KiCad SaveBoard renumbers numeric netcodes. Names/UUIDs/endpoints remain
    # the semantic identity here; candidate grading remains byte-strict later.
    pad_identity = lambda b: Counter(row[:-1] for row in _pads(b).elements())
    copper_identity = lambda b: {uid: sig[:2] + sig[3:]
                                 for uid, sig in _native_copper(b, pcbnew).items()}
    if (positions(new) != expected or pad_identity(old) != pad_identity(new)
            or copper_identity(old) != copper_identity(new)):
        raise ValueError("Fixture moved unexpected pads, nets or old copper")
    for name, digest in dependencies.items():
        if name != str(path.relative_to(root)) and sha(root / name) != digest:
            raise ValueError("Fixture changed dependency: " + name)
    report = run_drc(project, root / "work/fixture-drc.json", root=root)
    result = {"move": [ref, dx, dy], "original_board_sha256": case["baseline_sha256"][str(path.relative_to(root))],
              "fixture_board_sha256": sha(path), "drc_violations": len(report["violations"]),
              "schematic_parity_errors": len(report["schematic_parity"])}
    write(root / "fixture.json", result)
    if result["drc_violations"] or result["schematic_parity_errors"]:
        raise ValueError("Moved fixture fails pre-routing DRC/parity; do not route it")


def worker(request_path):
    # Kept in one subprocess so native API/CLI calls are serialized.
    import pcbnew
    from h6_r2_drc import input_hashes, run_drc, validate_provenance
    from h6_r2_manual_copper import item_uuid
    from h6_r2_route_candidate import grade_candidate

    req = read(request_path)
    case = read(req["case"])
    baseline, candidate = Path(req["baseline"]), Path(req["candidate"])
    rel = Path(req["board_relative"])
    started = time.monotonic()
    result = grade_candidate(baseline / rel, candidate / rel, case["nets"],
                             req.get("baseline_board_sha256", case["baseline_sha256"][str(rel)]))
    original = input_hashes(case["project"], baseline)
    current = input_hashes(case["project"], candidate)
    result["dependencies_unchanged"] = {
        k: v for k, v in original.items() if k != str(rel)
    } == {k: v for k, v in current.items() if k != str(rel)}
    old = pcbnew.LoadBoard(str(baseline / rel))
    board = pcbnew.LoadBoard(str(candidate / rel))
    old_ids = {item_uuid(item) for item in old.GetTracks()}
    x0, y0, x1, y1 = case["scope"]["roi_mm"]
    escaped = []
    for item in board.GetTracks():
        if item_uuid(item) in old_ids:
            continue
        radius = item.GetWidth(item.TopLayer()) / 2e6 if isinstance(item, pcbnew.PCB_VIA) else item.GetWidth() / 2e6
        if any(not (x0 <= p.x / 1e6 - radius and p.x / 1e6 + radius <= x1
                    and y0 <= p.y / 1e6 - radius and p.y / 1e6 + radius <= y1)
               for p in (item.GetStart(), item.GetEnd())):
            escaped.append(item_uuid(item))
    result["roi_escaped_objects"] = escaped
    result["grade_seconds"] = round(time.monotonic() - started, 3)
    started = time.monotonic()
    report_path = candidate / "work/native-drc.json"
    report = run_drc(case["project"], report_path, root=candidate)
    validate_provenance(report_path, case["project"], candidate)
    result.update(drc_checked=True, drc_seconds=round(time.monotonic() - started, 3),
                  drc_violations=len(report["violations"]),
                  schematic_parity_errors=len(report["schematic_parity"]),
                  drc_types=sorted({row["type"] for row in report["violations"]}))
    result["geometry_pass"] = bool(result.get("candidate_pass") and result.get("selected_complete")
        and result["dependencies_unchanged"] and not escaped
        and not result["drc_violations"] and not result["schematic_parity_errors"])
    result["electrically_qualified"] = False
    write(candidate / "validation.json", result)


def run(args):
    experiment_started = time.monotonic()
    case = read(args.case)
    recipe = read(PROFILE)
    verified_sources(case)
    tool = args.engine.resolve()
    revision = subprocess.check_output(["git", "-C", str(tool), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(tool), "status", "--porcelain", "--untracked-files=no"], text=True)
    if revision != recipe["engine"]["source_commit"] or dirty:
        raise ValueError("Engine source differs from measured pinned version")
    if sha(tool / "rust_router/grid_router.so") != recipe["engine"]["macos_arm64_binary_sha256"]:
        raise ValueError("Engine binary differs from pinned version")
    if not args.engine_python.is_file() or not KICAD_PYTHON.is_file():
        raise ValueError("Prepared engine and KiCad Python runtimes are required")
    output = Path(tempfile.mkdtemp(prefix="routing-benchmark-", dir=ROOT / "work"))
    shutil.copy2(args.case, output / "case.json")
    shutil.copy2(PROFILE, output / "engine-profile.json")
    print(json.dumps({"output": str(output), "case": case["id"]}), flush=True)
    project = case["project"]
    project_rel = Path("hardware/ecad/kicad") / project
    board_rel = project_rel / (project + ".kicad_pcb")
    baseline = output / "baseline"
    for name in ("libraries", "kicad/" + project):
        shutil.copytree(ROOT / "hardware/ecad" / name, baseline / "hardware/ecad" / name)
    fixture = None
    if args.move:
        write(output / "fixture-request.json", {"case": str(output / "case.json"),
              "baseline": str(baseline), "project": project, "move": args.move})
        preparation = execute([str(KICAD_PYTHON), str(Path(__file__).resolve()),
            "--prepare-fixture", str(output / "fixture-request.json")], output / "fixture.log", 120)
        if preparation["exit_code"] != 0:
            write(output / "fixture-failure.json", preparation)
            raise ValueError("Fixture preparation rejected; see " + str(output / "fixture.log"))
        fixture = read(baseline / "fixture.json")
    from h6_r2_drc import input_hashes
    baseline_inputs = input_hashes(project, baseline)
    floors = output / "floors.txt"
    floors.write_text(recipe["execution"]["fab_overrides_file_contents"])
    env = os.environ.copy()
    env.update(recipe["execution"]["environment"])
    env.update(PYTHONUNBUFFERED="1", PYTHONHASHSEED="0")
    profiles = case["profiles"]
    if args.sweep:
        profiles = [{"id": f"grid{grid}-via{cost}-{order}", "grid_step": grid,
                     "via_cost": cost, "ordering": order}
                    for grid in (0.1, 0.05) for cost in (50, 75, 125)
                    for order in ("mps", "inside_out")]
    if args.profiles:
        names = set(args.profiles.split(","))
        if names - {p["id"] for p in profiles}:
            raise ValueError("Unknown profile")
        profiles = [p for p in profiles if p["id"] in names]
    summary = {"case": case["id"], "candidate_only": True,
               "model_calls_inside_runs": 0, "orchestration_tokens": None,
               "electrically_qualified": False, "production_promoted": False,
               "engine_commit": revision, "baseline_inputs": baseline_inputs, "runs": []}
    summary["fixture"] = fixture
    summary["setup_seconds"] = round(time.monotonic() - experiment_started, 3)
    summary["controller_sha256"] = sha(__file__)
    summary["grader_sha256"] = sha(LAYOUT / "h6_r2_route_candidate.py")
    summary["case_sha256"] = sha(output / "case.json")
    summary["profile_sha256"] = sha(PROFILE)
    summary["runtime"] = json.loads(subprocess.check_output([
        str(args.engine_python.absolute()), "-c",
        "import sys,json,numpy,scipy,shapely; print(json.dumps(dict(python=sys.version, numpy=numpy.__version__, scipy=scipy.__version__, shapely=shapely.__version__)))"
    ], text=True))
    summary["setup_seconds"] = round(time.monotonic() - experiment_started, 3)
    initial_profile_count = len(profiles)
    # Repeated runs always restart from the exact same unrouted snapshot.
    for profile_index, profile in enumerate(profiles):
        if time.monotonic() - experiment_started > args.max_seconds:
            summary["budget_exhausted"] = True
            break
        for repeat in range(args.repeats):
            verified_sources(case)
            started = time.monotonic()
            dest = output / (profile["id"] + "-" + str(repeat + 1))
            shutil.copytree(baseline, dest)
            prepared = time.monotonic()
            # Resolving the venv's Python symlink bypasses its site-packages.
            command = [str(args.engine_python.absolute()), str(tool / "py_router/route.py"),
                       str(baseline / board_rel), str(dest / board_rel),
                       "--nets", *[n["kicad_net"] for n in case["nets"]],
                       *recipe["execution"]["arguments"], "--fab-overrides", str(floors),
                       "--grid-step", str(profile["grid_step"]),
                       "--via-cost", str(profile["via_cost"]),
                       "--ordering", profile["ordering"],
                       "--json-out", str(dest / "engine-summary.json")]
            if profile.get("direction"):
                command.extend(["--direction", profile["direction"]])
            if profile.get("layers"):
                if not set(profile["layers"]) <= {"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"}:
                    raise ValueError("Profile cannot introduce a prohibited layer")
                command.extend(["--layers", *profile["layers"]])
            row = {"profile": profile, "repeat": repeat + 1, "candidate": str(dest / board_rel),
                   "command": command, "prepare_seconds": round(prepared - started, 3)}
            row["engine"] = execute(command, dest / "engine.log", case["engine_timeout_seconds"], env)
            # Detect and discard ALL engine dependency edits before native DRC.
            row["discarded_dependency_edits"] = restore_dependencies(
                baseline, dest, baseline_inputs, board_rel)
            request = {"case": str(output / "case.json"), "baseline": str(baseline),
                       "candidate": str(dest), "board_relative": str(board_rel),
                       "baseline_board_sha256": baseline_inputs[str(board_rel)]}
            write(dest / "request.json", request)
            row["validation_process"] = execute([str(KICAD_PYTHON), str(Path(__file__).resolve()),
                "--worker", str(dest / "request.json")], dest / "validation.log", case["validation_timeout_seconds"])
            if (dest / "validation.json").exists():
                row["validation"] = read(dest / "validation.json")
            row["geometry_pass"] = (row["engine"]["exit_code"] == 0
                and row["validation_process"]["exit_code"] == 0
                and row.get("validation", {}).get("geometry_pass", False))
            if input_hashes(project, baseline) != baseline_inputs:
                raise ValueError("Benchmark baseline mutated")
            verified_sources(case)
            row["end_to_end_seconds"] = round(time.monotonic() - started, 3)
            summary["runs"].append(row)
            summary["benchmark_seconds"] = round(time.monotonic() - experiment_started, 3)
            write(output / "summary.json", summary)
            grade = row.get("validation", {})
            print(json.dumps({"profile": profile["id"], "repeat": repeat + 1,
                "seconds": row["end_to_end_seconds"], "engine_seconds": row["engine"]["seconds"],
                "geometry_pass": row["geometry_pass"], "resolved": grade.get("resolved_connections"),
                "vias": grade.get("new_vias"), "length_mm": grade.get("new_trace_length_mm"),
                "drc": grade.get("drc_types"), "roi_escapes": len(grade.get("roi_escaped_objects", []))}), flush=True)
        if profile_index + 1 == initial_profile_count and args.repeat_best:
            best = select_best(summary["runs"])
            summary["selection_policy"] = "complete + all geometry gates; minimize vias, then length, then wall time; not electrical qualification"
            if best:
                summary["best_initial_profile"] = best["profile"]
                summary["best_initial_geometry_signature"] = best["validation"]["added_geometry_signature"]
                profiles.extend([{**best["profile"], "id": best["profile"]["id"] + f"-replay{i}",
                                  "replay_of": best["profile"]["id"]}
                                 for i in range(1, args.repeat_best + 1)])
    replays = [row for row in summary["runs"] if row["profile"].get("replay_of")]
    summary["replay_pass"] = (len(replays) == args.repeat_best and args.repeat_best > 0
        and all(row["geometry_pass"] for row in replays)
        and {row["validation"]["added_geometry_signature"] for row in replays}
            == {summary.get("best_initial_geometry_signature")})
    summary["benchmark_seconds"] = round(time.monotonic() - experiment_started, 3)
    write(output / "summary.json", summary)
    print(json.dumps({"summary": str(output / "summary.json")}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--prepare-fixture", type=Path)
    parser.add_argument("--case", type=Path, default=LAYOUT / "benchmarks/ui-upper-keys-28.json")
    parser.add_argument("--engine", type=Path, default=ROOT / "work/kicad-routing-tools-bench")
    parser.add_argument("--engine-python", type=Path, default=ROOT / "work/route-batch-Z7Zt8C/venv/bin/python")
    parser.add_argument("--profiles", help="Comma-separated exact profile IDs; default all")
    parser.add_argument("--repeats", type=int, choices=range(1, 4), default=1)
    parser.add_argument("--sweep", action="store_true", help="Bounded 12-profile parameter sweep")
    parser.add_argument("--repeat-best", type=int, choices=range(4), default=0)
    parser.add_argument("--max-seconds", type=int, default=1800, help="Stop scheduling new profiles after this budget")
    parser.add_argument("--move", nargs=3, metavar=("REF", "DX_MM", "DY_MM"),
                        help="Small selected-component move in a checked disposable baseline")
    args = parser.parse_args()
    if args.prepare_fixture:
        prepare_fixture(args.prepare_fixture)
    elif args.worker:
        worker(args.worker)
    else:
        run(args)


if __name__ == "__main__":
    main()
