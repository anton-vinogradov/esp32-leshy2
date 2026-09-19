#!/usr/bin/env python3
"""Cold UI252/RF222 portfolio and three checked replays, without model decisions.

Candidates and receipts stay under work/. Never modifies production boards.
Success is geometry/repeatability only, not electrical or manufacturing release.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import hashlib
import json
from pathlib import Path
import signal
import sys
import tempfile
from threading import Condition, Event, Thread
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hardware.layout.h6_r2_parallel_jobs import run_jobs, PhaseResult
from hardware.layout.h6_r2_parallel_process import ProcessRegistry
from tools.route_board import assess, keep_awake, load_cases

PLAN = ROOT / "hardware/layout/h6-r2-474-repeat-portfolio.json"
PATCH = "0dec1ef898beec101580f496a7ef48a9042cb45ad77b29b2468e26c3f8a63067"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def checked_result_hash(folder, result):
    """Bind saved proof to the backend return before adding CLI row fields."""
    payload = (Path(folder) / "checked-result.json").read_bytes()
    require(json.loads(payload) == result, "Saved checked result differs from backend validation")
    return hashlib.sha256(payload).hexdigest()


def check_accepted_evidence(result):
    """Recheck each credited cohort against hashes captured during validation.

    Never refresh expected hashes from saved summaries or checked-result files.
    A missing or changed proof invalidates the campaign before credit is emitted.
    """
    paths = (("candidate/validation.json", "validation_sha256"),
             ("candidate/work/native-drc.json", "drc_report_sha256"),
             ("candidate/work/native-drc.json.provenance.json", "drc_receipt_sha256"),
             ("inventory.json", "inventory_sha256"),
             ("checked-result.json", "checked_result_sha256"))
    for state in result["cases"].values():
        if not (state["assessment"] and state["assessment"]["accepted"]):
            continue
        require(state["winner"] is not None and len(state["replays"]) == 3,
                "Accepted evidence requires a winner and three replays")
        for row in [state["winner"], *state["replays"]]:
            for relative, key in paths:
                require(sha(Path(row["folder"]) / relative) == row.get(key),
                        f"Accepted evidence changed: {row['profile']['id']}/{relative}")


def expand_seeded_orders(config, cases):
    """Expand bounded plan seeds to exact immutable net permutations.

    SHA256 ordering is independent of Python RNG/version and process timing.
    Seeds select only order, never net membership, geometry or checking rules.
    Replays receive the expanded recipe, not a fresh random decision.
    """
    result = copy.deepcopy(config)
    for kind, section in result["cases"].items():
        names = [row["kicad_net"] for row in cases[kind]["nets"]]
        for recipe in section["profiles"]:
            if "order_seed" not in recipe:
                continue
            seed = recipe.pop("order_seed")
            require(type(seed) is int and 0 <= seed <= 65535, "Invalid order seed")
            require(recipe.get("ordering") == "original" and recipe.get("net_order") is None,
                    "Seed order requires original ordering and no explicit permutation")
            recipe["net_order"] = sorted(names, key=lambda n: (
                hashlib.sha256(f"route-474-order-v1\0{seed}\0{n}".encode()).digest(), n))
        require(all("order_seed" not in r for r in section.get("adaptive", [])),
                "Adaptive failed-first and seeded order are distinct strategies")
    return result


def cohort(case, winner, replays):
    """Assess only this explicitly identified candidate and its three replays.

Rejected search attempts remain in the campaign ledger, not this proof cohort.
They are never counted as resolved connections or silently erased.
"""
    rows = [winner, *replays]
    signature = winner.get("validation", {}).get("added_geometry_signature")
    same_recipe = len(replays) == 3 and all(
        row.get("recipe") == winner.get("recipe")
        and row.get("folder") != winner.get("folder") for row in replays)
    cold = all(row.get("cold_from_original") is True for row in rows)
    clean = all("all_net_regressions" in row.get("validation", {})
                and not row["validation"]["all_net_regressions"] for row in rows)
    distinct = all(isinstance(row.get("folder"), str) and row["folder"] for row in rows) and len({row["folder"] for row in rows}) == 4
    consistent = all(row.get("validation", {}).get("added_geometry_signature") == signature for row in rows)
    summary = {"case": case["id"], "candidate_only": True, "production_promoted": False,
               "electrically_qualified": False, "runs": rows,
               "best_initial_profile": winner["profile"], "best_initial_geometry_signature": signature,
               "replay_pass": same_recipe and distinct and consistent and cold and clean,
               "budget_exhausted": False}
    return assess(summary, case, case["scope"]["expected_connections"])


def ranked(rows):
    return sorted((r for r in rows if r.get("geometry_pass") is True), key=lambda r: (
        r["validation"]["new_vias"], r["validation"]["new_trace_length_mm"],
        r.get("engine", {}).get("seconds", float("inf")), r["profile"]["id"]))


def failed_first(case, rows, template, index):
    """Freeze an exact scope permutation from checked partial evidence only."""
    checked = [r for r in rows if r.get("validation", {}).get("drc_checked") is True
               and not r["validation"].get("all_net_regressions")]
    if not checked:
        return None
    best = min(checked, key=lambda r: (r["validation"]["selected_remaining"][1],
                                      r["validation"]["drc_violations"], r["profile"]["id"]))
    counts = best["validation"]["per_net"]
    names = [r["kicad_net"] for r in case["nets"]]
    require(set(names) <= set(counts), "Missing selected net evidence for adaptive order")
    recipe = copy.deepcopy(template)
    recipe.update(name=f"failed-first-{index}", ordering="original",
                  net_order=sorted(names, key=lambda n: (-counts[n][1], names.index(n))))
    return recipe


def campaign(cases, plan, execute_wave, *, wave_size=8, cancelled=lambda: False):
    """Finite deterministic state machine; execute_wave returns checked rows.

Input order, not wall-clock completion order, determines the chosen candidate.
No external decision is needed between search attempts and replay attempts.
"""
    states = {kind: {"queue": copy.deepcopy(plan[kind]["profiles"]), "attempts": [],
                     "winner": None, "replays": [], "assessment": None,
                     "adaptive_generated": False, "finished": False} for kind in cases}
    waves = 0
    while not all(s["finished"] for s in states.values()) and not cancelled():
        jobs = []
        for kind, state in states.items():
            if state["finished"]:
                continue
            if state["winner"] is not None:
                for number in range(1, 4):
                    winner = state["winner"]
                    jobs.append({"id": f"{kind}-replay-{number}", "kind": kind,
                                 "recipe": copy.deepcopy(winner["recipe"]),
                                 "replay_of": winner["profile"]["id"]})
                continue
            if not state["queue"] and not state["adaptive_generated"]:
                state["adaptive_generated"] = True
                for index, template in enumerate(plan[kind].get("adaptive", []), 1):
                    recipe = failed_first(cases[kind], state["attempts"], template, index)
                    if recipe is not None:
                        state["queue"].append(recipe)
        # Round-robin boards; a successful board gets replays instead of more search.
        searches = 0
        while searches < wave_size:
            added = False
            for kind, state in states.items():
                if searches >= wave_size:
                    break
                if not state["finished"] and state["winner"] is None and state["queue"]:
                    recipe = state["queue"].pop(0)
                    jobs.append({"id": f"{kind}-search-{len(state['attempts']) + sum(j['kind'] == kind for j in jobs) + 1}",
                                 "kind": kind, "recipe": recipe})
                    searches += 1
                    added = True
            if not added:
                break
        if not jobs:
            for state in states.values():
                state["finished"] = True
            break
        waves += 1
        rows = execute_wave(jobs, waves)
        require(len(rows) == len(jobs), "Missing portfolio job results")
        for job, row in zip(jobs, rows):
            require(row["profile"]["id"] == job["id"] and row["recipe"] == job["recipe"], "Job/result mismatch")
            state = states[job["kind"]]
            state["attempts"].append(row)
            if job.get("replay_of"):
                state["replays"].append(row)
        for kind, state in states.items():
            if state["finished"]:
                continue
            if state["winner"] is not None:
                state["assessment"] = cohort(cases[kind], state["winner"], state["replays"])
                state["finished"] = True
            else:
                passed = ranked(state["attempts"])
                if passed:
                    state["winner"] = passed[0]
                elif not state["queue"] and state["adaptive_generated"]:
                    state["finished"] = True
    accepted = {k: bool(s["assessment"] and s["assessment"]["accepted"]) for k, s in states.items()}
    return {"status": "pass" if all(accepted.values()) and not cancelled() else "fail",
            "resolved": sum(cases[k]["scope"]["expected_connections"] for k in cases if accepted[k] and not cancelled()),
            "targeted": sum(c["scope"]["expected_connections"] for c in cases.values()),
            "cancelled": cancelled(), "waves": waves, "cases": states,
            "production_ready": False, "electrically_qualified": False, "model_decisions_inside_run": 0}


class ResourceBudget:
    """Conservative memory concurrency: fine-grid attempts reserve two units."""
    def __init__(self, units, cancel):
        require(type(units) is int and units >= 1, "Resource capacity must be positive")
        self.capacity = units
        self.available, self.cancel, self.condition = units, cancel, Condition()

    @contextmanager
    def acquire(self, units):
        require(type(units) is int and 1 <= units <= self.capacity, "Invalid resource reservation")
        with self.condition:
            while self.available < units and not self.cancel.is_set():
                self.condition.wait(0.2)
            require(not self.cancel.is_set(), "Cancelled while waiting for memory budget")
            self.available -= units
        try:
            yield
        finally:
            with self.condition:
                self.available += units
                self.condition.notify_all()


def finish_registry(registry, cancel, explicit_abort, report):
    """Registry cleanup sets its Event even on success; do not call that a cancel."""
    interrupted = cancel.is_set()
    registry.cancel_all()
    interrupted = interrupted or explicit_abort.is_set()
    if interrupted:
        report.update(status="fail", resolved=0)
    report["cancelled"] = interrupted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--engine-root", type=Path, default=ROOT / "work/pending-leaf-VTy6VD")
    parser.add_argument("--engine-python", type=Path, default=ROOT / "work/route-batch-Z7Zt8C/venv/bin/python")
    parser.add_argument("--engine-patch-sha256", default=PATCH)
    parser.add_argument("--workers", type=int, choices=range(2, 9), default=8)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    from hardware.layout import h6_r2_batch_backend as backend
    config = json.loads(args.plan.read_text())
    require(config["schema_version"] == 1 and set(config["cases"]) == {"ui", "rf"}, "Expected fixed UI252/RF222 plan")
    for kind, limit in (("ui", 12), ("rf", 2)):
        section = config["cases"][kind]
        require(1 <= len(section["profiles"]) <= limit and len(section.get("adaptive", [])) <= 4,
                "Portfolio exceeds bounded search budget")
        names = [r["name"] for r in section["profiles"] + section.get("adaptive", [])]
        require(len(names) == len(set(names)), "Repeated recipe name")
    for key, maximum in (("engine_timeout_seconds", 1800), ("fine_engine_timeout_seconds", 1800),
                         ("validation_timeout_seconds", 180)):
        require(type(config.get(key)) is int and 1 <= config[key] <= maximum, "Invalid timeout: " + key)
    loaded = load_cases([ROOT / config["cases"][k]["manifest"] for k in ("ui", "rf")])
    cases = {k: row[1] for k, row in zip(("ui", "rf"), loaded)}
    config = expand_seeded_orders(config, cases)
    for section in config["cases"].values():
        for recipe in section["profiles"] + section.get("adaptive", []):
            backend.Recipe(**recipe)
    require([cases[k]["scope"]["expected_connections"] for k in ("ui", "rf")] == [252, 222], "Wrong milestone scope")
    output = Path(tempfile.mkdtemp(prefix="route-474-", dir=ROOT / "work"))
    cancel, done, explicit_abort = Event(), Event(), Event()
    registry = ProcessRegistry(cancel, grace_seconds=10)
    budget = ResourceBudget(args.workers, cancel)
    pins = {str(Path(__file__).resolve()): sha(__file__), str(args.plan.resolve()): sha(args.plan)}
    report = {"status": "fail", "targeted": 474, "resolved": 0, "production_ready": False,
              "electrically_qualified": False, "sleep_prevention": {}, "source_pins": pins}
    started = time.monotonic()
    print(json.dumps({"event": "campaign_started", "folder": str(output.relative_to(ROOT))}), flush=True)
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
    def stop(*_):
        explicit_abort.set()
        cancel.set()
    for sig in previous:
        signal.signal(sig, stop)

    def check_pins():
        require(all(sha(p) == digest for p, digest in pins.items()), "CLI/portfolio changed during run")
        require(not cancel.is_set(), "Campaign cancelled")

    contexts = {}
    try:
        authorities = {k: backend.authority(loaded[i][0], engine_root=args.engine_root.resolve(),
                        engine_python=args.engine_python.absolute(), engine_patch_sha256=args.engine_patch_sha256)
                       for i, k in enumerate(("ui", "rf"))}
        write(output / "plan.json", config)
        write(output / "authorities.json", authorities)
        with keep_awake(report["sleep_prevention"], output) as power:
            def watch_power():
                while not done.wait(0.5):
                    if power is not None and power.poll() is not None:
                        explicit_abort.set()
                        cancel.set()
                        return
            watcher = Thread(target=watch_power, daemon=True)
            watcher.start()
            # Real native DRC probe before expensive search. This catches unavailable
            # macOS services/sandbox failures that a --version check cannot detect.
            report["native_preflight"] = {}
            for kind in ("ui", "rf"):
                check_pins()
                ctx = backend.prepare(authorities[kind], config["cases"][kind]["profiles"][0],
                                      output / ("preflight-" + kind), registry)
                native = backend.preflight(ctx, registry, timeout=180)
                backend.check_context(ctx)
                report["native_preflight"][kind] = native
            report["preflight_pass"] = True

            def execute_wave(jobs, number):
                check_pins()
                wave = output / f"wave-{number}"
                wave.mkdir()
                write(wave / "jobs.json", jobs)
                def calculate(job):
                    units = 2 if job["recipe"].get("grid_step", .05) < .05 else 1
                    with budget.acquire(units):
                        check_pins()
                        ctx = backend.prepare(authorities[job["kind"]], job["recipe"], wave / job["id"], registry)
                        contexts[job["id"]] = ctx
                        timeout = config["fine_engine_timeout_seconds"] if units == 2 else config["engine_timeout_seconds"]
                        backend.engine(ctx, registry, timeout=timeout)
                        check_pins()
                        return PhaseResult(ctx["engine"]["exit_code"] == 0, ctx)
                def validate(job, ctx):
                    check_pins()
                    result = backend.validate(ctx, registry, timeout=config.get("validation_timeout_seconds", 180))
                    result["checked_result_sha256"] = checked_result_hash(ctx["folder"], result)
                    check_pins()
                    return PhaseResult(result["geometry_pass"], result)
                observed = run_jobs(jobs, calculate, validate, max_workers=args.workers,
                                    cancel_event=cancel, cancel_running=registry.cancel_all)
                rows = []
                for job, observation in zip(jobs, observed):
                    value = observation["validation"] or {}
                    ctx = observation["engine"] or contexts.get(job["id"], {})
                    row = {**value, "profile": {"id": job["id"], **({"replay_of": job["replay_of"]} if job.get("replay_of") else {})},
                           "recipe": job["recipe"], "folder": ctx.get("folder"), "cold_from_original": bool(ctx),
                           "geometry_pass": observation["accepted"] and value.get("geometry_pass") is True,
                           "engine": value.get("engine", ctx.get("engine", {"exit_code": "failed"})),
                           "validation_process": value.get("validation_process", {"exit_code": "not_run"}),
                           "validation": value.get("validation", {}), "error": observation["error"]}
                    rows.append(row)
                write(wave / "results.json", rows)
                print(json.dumps({"event": "wave_done", "wave": number, "attempts": len(rows),
                                  "geometry_passes": sum(r["geometry_pass"] for r in rows)}), flush=True)
                return rows

            if not args.preflight_only:
                result = campaign(cases, config["cases"], execute_wave, wave_size=args.workers,
                                  cancelled=cancel.is_set)
                for ctx in contexts.values():
                    backend.check_context(ctx)
                check_pins()
                check_accepted_evidence(result)
                report.update(result)
            else:
                report.update(status="preflight_pass", preflight_only=True)
            done.set()
            watcher.join(timeout=2)
    except BaseException as exc:
        report.update(status="fail", resolved=0, error=f"{type(exc).__name__}: {exc}")
    finally:
        done.set()
        finish_registry(registry, cancel, explicit_abort, report)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        report.update(wall_seconds=round(time.monotonic() - started, 3))
        write(output / "summary.json", report)
    print(json.dumps({k: report.get(k) for k in ("status", "resolved", "targeted", "wall_seconds", "error")}
                     | {"summary": str((output / "summary.json").relative_to(ROOT)), "production_ready": False}), flush=True)
    return 0 if report["status"] in ("pass", "preflight_pass") and not report["cancelled"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
