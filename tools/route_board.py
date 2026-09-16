#!/usr/bin/env python3
"""Run one or two disjoint, copy-only routing cases serially; emit one JSON result.

Usage: python3 tools/route_board.py --case hardware/layout/benchmarks/ui-controls-60.json
Add a second --case for another board or disjoint nets. --sweep explores all
grid/cost profiles; --portfolio explores order/direction variants. Adaptive
search is the default; three checked winner replays are always mandatory.
Detailed controller logs and candidate copies stay under work/. Success means
checked geometry only, never electrical qualification or production promotion.
On macOS, caffeinate prevents idle system sleep during the run; display sleep
remains allowed. Its assertion is checked at startup and released on exit.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hardware.layout.h6_r2_autorouter_benchmark import sha
from hardware.layout.h6_r2_drc import validate_provenance
from hardware.layout.h6_r2_route_candidate import _validate_rows

LAYOUT = ROOT / "hardware/layout"
CONTROLLER = LAYOUT / "h6_r2_autorouter_benchmark.py"


def stop_process(process, grace=10):
    """Give the controller time to forward cancellation to its child groups."""
    if process.poll() is None:
        try:
            process.terminate()
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@contextmanager
def keep_awake(state, directory):
    """Own only this invocation's idle-sleep assertion, never global settings."""
    state.update(platform=sys.platform, status="unsupported_not_needed", established=False,
                 active=False, display_sleep_allowed=True)
    if sys.platform != "darwin":
        yield None
        return
    state["status"] = "failed"
    log = directory / "caffeinate.log"
    state["log"] = str(log.relative_to(ROOT))
    with log.open("w") as stream:
        process = subprocess.Popen(["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())],
                                   stdin=subprocess.DEVNULL, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline and process.poll() is None:
                try:
                    observed = subprocess.run(["/usr/bin/pmset", "-g", "assertions"],
                                              capture_output=True, text=True, timeout=2, check=True)
                except (OSError, subprocess.SubprocessError) as exc:
                    raise RuntimeError("Cannot verify caffeinate idle-sleep assertion") from exc
                if re.search(rf"^\s*pid {process.pid}\(caffeinate\):[^\n]*\bPreventUserIdleSystemSleep\b",
                             observed.stdout, re.MULTILINE):
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError("caffeinate did not establish an idle-sleep assertion")
            state.update(status="active", established=True, active=True)
            yield process
            if process.poll() is not None:
                raise RuntimeError("caffeinate exited before routing finished")
        finally:
            stop_process(process, grace=3)
            state.update(status="released" if state["established"] else "failed", active=False)


def run_controller(command, stream, power):
    """Wait without orphaning the controller when this CLI is cancelled."""
    process = subprocess.Popen(command, cwd=ROOT, stdout=stream,
                               stderr=subprocess.STDOUT, start_new_session=True)
    try:
        while True:
            if power is not None and power.poll() is not None:
                raise RuntimeError("caffeinate exited while routing; controller stopped")
            try:
                return subprocess.CompletedProcess(command, process.wait(timeout=1))
            except subprocess.TimeoutExpired:
                continue
    except BaseException:
        stop_process(process)
        raise


def within(path, parent):
    path = Path(path).resolve()
    if not path.is_relative_to(parent.resolve()):
        raise ValueError("Path must stay under " + str(parent.relative_to(ROOT)))
    return path


def verify_hashes(hashes):
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("Missing input hashes")
    for name, digest in hashes.items():
        if sha(within(ROOT / name, ROOT)) != digest:
            raise ValueError("Input hash mismatch: " + name)


def load_cases(paths):
    if not 1 <= len(paths) <= 2:
        raise ValueError("Provide one or two --case manifests")
    cases, selected = [], set()
    for path in paths:
        path = within(path, ROOT)
        case = json.loads(path.read_text())
        if (case["project"] not in {"LESHY2-UI-R2", "LESHY2-RF-R2"}
                or type(case["schema_version"]) is not int or case["schema_version"] != 1):
            raise ValueError("Unsupported board project or manifest schema")
        names = _validate_rows(case["nets"])
        if any(name.startswith("-") or any(char in name for char in "*?[]") for name in names):
            raise ValueError("Wildcard net selection is forbidden")
        for row in case["nets"]:
            if row["project"] != case["project"] or any(not re.fullmatch(r"[^\s.]+\.[^\s.]+", pad) for pad in row["exact_ref_pads"]):
                raise ValueError("Malformed endpoint set or net project mismatch")
        if not case["profiles"] or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", p["id"]) for p in case["profiles"]):
            raise ValueError("Malformed profile identifiers")
        keys = {(case["project"], name) for name in names}
        if selected & keys:
            raise ValueError("Cases overlap selected nets on the same project")
        selected.update(keys)
        target = sum(row["remaining_connections"] for row in case["nets"])
        if (target <= 0 or type(case["scope"]["expected_connections"]) is not int
                or target != case["scope"]["expected_connections"]):
            raise ValueError("Case target disagrees with explicit net counts")
        for key in ("engine_timeout_seconds", "validation_timeout_seconds"):
            if type(case[key]) is not int or case[key] <= 0:
                raise ValueError("Case timeouts must be positive integer seconds")
        board = f"hardware/ecad/kicad/{case['project']}/{case['project']}.kicad_pcb"
        if board not in case["baseline_sha256"]:
            raise ValueError("Missing production board hash")
        verify_hashes(case["baseline_sha256"])
        cases.append((path, case, target))
    return cases


def assess(summary, case, target):
    """Fail closed on incomplete native checks or unverified replay claims."""
    if (summary["case"] != case["id"] or summary["candidate_only"] is not True
            or summary["production_promoted"] is not False
            or summary["electrically_qualified"] is not False
            or summary.get("fixture") is not None):
        raise ValueError("Summary does not describe the requested copy-only case")
    runs = summary["runs"]
    if not isinstance(runs, list) or not runs:
        raise ValueError("Summary has no checked attempts")
    replays = [r for r in runs if r["profile"].get("replay_of")]
    initials = [r for r in runs if not r["profile"].get("replay_of")]
    for row in runs:
        for field in ("drc_violations", "schematic_parity_errors", "drc_selected_unconnected"):
            count = row.get("validation", {}).get(field, 0)
            if type(count) is not int or count < 0:
                raise ValueError("Malformed native failure count")

    def checked(row):
        grade = row.get("validation", {})
        native = grade.get("native_unconnected", [])
        selected = grade.get("selected_remaining", [])
        return (row["geometry_pass"] is True
                and all(type(row[k]["exit_code"]) is int and row[k]["exit_code"] == 0
                        for k in ("engine", "validation_process"))
                and all(grade.get(k) is True for k in ("geometry_pass", "candidate_pass",
                    "preservation_recipe_pass", "dependencies_unchanged", "selected_complete",
                    "drc_checked", "candidate_unchanged_during_checks"))
                and selected == [target, 0] and all(type(n) is int for n in selected)
                and len(native) == 2 and all(type(n) is int and n >= 0 for n in native)
                and native[0] > native[1] and type(grade.get("resolved_connections")) is int
                and grade["resolved_connections"] == native[0] - native[1]
                and grade.get("drc_violations") == 0 and grade.get("schematic_parity_errors") == 0
                and grade.get("drc_selected_unconnected") == 0 and grade.get("kicad_version") == "10.0.5"
                and grade.get("failures") == {} and grade.get("roi_escaped_objects") == []
                and grade.get("electrically_qualified") is False)

    signature = summary.get("best_initial_geometry_signature")
    winner = summary.get("best_initial_profile", {}).get("id")
    replay_passed = (len(replays) == 3 and len({r["profile"]["id"] for r in replays}) == 3
        and isinstance(signature, str) and re.fullmatch(r"[0-9a-f]{64}", signature)
        and summary.get("replay_pass") is True
        and all(checked(r) and r["profile"]["replay_of"] == winner
                and r["validation"]["added_geometry_signature"] == signature for r in replays)
        and any(checked(r) and r["profile"]["id"] == winner
                and r["validation"]["added_geometry_signature"] == signature for r in initials))
    timed_out = any(r[k]["exit_code"] == "timeout" for r in runs for k in ("engine", "validation_process"))
    accepted = bool(replay_passed and not timed_out and not summary.get("budget_exhausted"))
    observed = [r.get("validation", {}).get("selected_remaining") for r in runs]
    partial = max([target - pair[1] for pair in observed if isinstance(pair, list) and len(pair) == 2
                   and all(type(n) is int for n in pair) and pair[0] == target and 0 <= pair[1] <= target], default=0)
    return {"case": case["id"], "targeted": target, "accepted": accepted,
            "resolved": target if accepted else 0, "remaining_targeted": 0 if accepted else target,
            "best_partial_resolved": partial,  # Diagnostic progress; never acceptance credit.
            "replay_passed": bool(replay_passed), "timed_out": timed_out,
            "native_drc_failures": sum(r.get("validation", {}).get("drc_violations", 0) for r in runs),
            "parity_failures": sum(r.get("validation", {}).get("schematic_parity_errors", 0) for r in runs)}


def run_case(path, case, target, args, directory, index):
    log = directory / f"case-{index}.log"
    result = {"case": case["id"], "targeted": target, "accepted": False, "resolved": 0,
              "best_partial_resolved": 0,
              "remaining_targeted": target, "replay_passed": False,
              "native_drc_failures": None, "parity_failures": None, "log": str(log.relative_to(ROOT))}
    command = [sys.executable, str(CONTROLLER), "--case", str(path), "--quiet", "--repeat-best", "3",
               "--max-seconds", str(args.max_seconds),
               "--sweep" if args.sweep else "--portfolio" if args.portfolio else "--adaptive"]
    for option in ("engine", "engine_python"):
        if getattr(args, option):
            command.extend(["--" + option.replace("_", "-"), str(getattr(args, option).absolute())])
    try:
        expected = {"case_sha256": sha(path), "controller_sha256": sha(CONTROLLER),
                    "profile_sha256": sha(LAYOUT / "h6-r2-autorouter-profile.json"),
                    "profile_policy_sha256": sha(LAYOUT / "h6_r2_benchmark_profiles.py"),
                    "grader_sha256": sha(LAYOUT / "h6_r2_route_candidate.py")}
        started = time.time_ns()
        with log.open("w") as stream:
            completed = run_controller(command, stream, args.power_process)
        verify_hashes(case["baseline_sha256"])
        if completed.returncode:
            raise ValueError("Controller failed; inspect controller log")
        events = [json.loads(line) for line in log.read_text().splitlines() if line.startswith("{")]
        output = within(events[0]["output"], ROOT / "work")
        summary_path = within(events[-1]["summary"], output)
        result["summary"] = str(summary_path.relative_to(ROOT))
        if (summary_path != output / "summary.json" or summary_path.stat().st_mtime_ns < started
                or sha(summary_path) != events[-1]["summary_sha256"]
                or sha(output / "case.json") != expected["case_sha256"]):
            raise ValueError("Stale or tampered case/summary evidence")
        summary = json.loads(summary_path.read_text())
        current = {"case_sha256": sha(path), "controller_sha256": sha(CONTROLLER),
                   "profile_sha256": sha(LAYOUT / "h6-r2-autorouter-profile.json"),
                   "profile_policy_sha256": sha(LAYOUT / "h6_r2_benchmark_profiles.py"),
                   "grader_sha256": sha(LAYOUT / "h6_r2_route_candidate.py")}
        if current != expected or any(summary.get(key) != digest for key, digest in expected.items()):
            raise ValueError("Summary provenance hash mismatch")
        verify_hashes(summary["baseline_inputs"])
        for row in summary["runs"]:
            candidate = within(row["candidate"], output)
            attempt = within(output / f"{row['profile']['id']}-{row['repeat']}", output)
            relative = Path("hardware/ecad/kicad") / case["project"] / (case["project"] + ".kicad_pcb")
            if candidate != attempt / relative:
                raise ValueError("Candidate path does not match its attempt")
            validation = attempt / "validation.json"
            if "validation" in row and (json.loads(validation.read_text()) != row["validation"]
                    or sha(candidate) != row["validation"]["candidate_sha256"]):
                raise ValueError("Candidate or native validation evidence changed")
            if "validation" in row:
                grade = row["validation"]
                native = attempt / "work/native-drc.json"
                receipt = native.with_name(native.name + ".provenance.json")
                if sha(native) != grade["drc_report_sha256"] or sha(receipt) != grade["drc_receipt_sha256"]:
                    raise ValueError("Native DRC report or receipt hash mismatch")
                validate_provenance(native, case["project"], attempt)
                report = json.loads(native.read_text())
                if (len(report["violations"]) != grade["drc_violations"]
                        or len(report["schematic_parity"]) != grade["schematic_parity_errors"]
                        or report["kicad_version"] != grade["kicad_version"]):
                    raise ValueError("Native DRC observations differ from candidate grade")
        result.update(assess(summary, case, target))
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
        result["error"] = str(exc)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", action="append", type=Path, required=True, help="Explicit case manifest; repeat at most twice")
    search = parser.add_mutually_exclusive_group()
    search.add_argument("--sweep", action="store_true", help="Explore all profiles, then check three winner replays")
    search.add_argument("--portfolio", action="store_true", help="Explore bounded order/direction variants, then three replays")
    parser.add_argument("--max-seconds", type=int, default=1800, help="Per-case scheduling budget in seconds (default: 1800)")
    parser.add_argument("--engine", type=Path, help="Already installed, pinned engine checkout")
    parser.add_argument("--engine-python", type=Path, help="Already prepared engine Python interpreter")
    args = parser.parse_args(argv)
    report = {"accepted_cases": 0, "resolved": 0, "replay_passed": False,
              "electrically_qualified": False, "production_promoted": False, "production_ready": False,
              "blockers": ["Experiment-only geometry benchmark", "Electrical/ESD/return-path qualification missing"],
              "cases": [], "sleep_prevention": {"status": "not_started"}}
    previous = signal.getsignal(signal.SIGTERM)
    def cancelled(signum, frame):
        raise KeyboardInterrupt("Routing cancelled")
    signal.signal(signal.SIGTERM, cancelled)
    try:
        if args.max_seconds <= 0:
            raise ValueError("--max-seconds must be positive")
        cases = load_cases(args.case)
        (ROOT / "work").mkdir(exist_ok=True)
        with (ROOT / "work/route-board.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            directory = Path(tempfile.mkdtemp(prefix="route-board-", dir=ROOT / "work"))
            with keep_awake(report["sleep_prevention"], directory) as power:
                args.power_process = power
                for index, (path, case, target) in enumerate(cases, 1):
                    result = run_case(path, case, target, args, directory, index)
                    report["cases"].append(result)
                    if result.get("timed_out"):
                        break
        for key in ("resolved", "best_partial_resolved", "native_drc_failures", "parity_failures"):
            values = [r.get(key) for r in report["cases"]]
            report[key] = sum(values) if all(v is not None for v in values) else None
        report.update(targeted=sum(c[2] for c in cases),
                      accepted_cases=sum(r["accepted"] for r in report["cases"]))
        report["remaining_targeted"] = report["targeted"] - report["resolved"]
        report["replay_passed"] = report["accepted_cases"] == len(cases)
    except KeyboardInterrupt:
        report.update(cancelled=True, error="Routing cancelled; child cleanup requested", replay_passed=False)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError) as exc:
        report["error"] = str(exc)
    finally:
        signal.signal(signal.SIGTERM, previous)
    print(json.dumps(report, sort_keys=True))
    return 130 if report.get("cancelled") else 0 if report["replay_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
