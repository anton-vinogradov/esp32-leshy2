"""Copy-only routing backend; no work-script or historical seed dependency.

authority -> prepare (cold copy/native proof) -> engine -> validate. Contexts
are JSON-serializable, sealed to on-disk receipts and checked before/after each
phase. Native validation is serialized and one-shot; existing output evidence
is never reused. The caller owns scheduling, cancellation and sleep prevention.
Successful results describe geometry only, not electrical/production approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import fcntl
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from .h6_r2_autorouter_benchmark import KICAD_PYTHON, PROFILE, read, write, sha, restore_dependencies, verified_sources
from .h6_r2_drc import input_hashes, validate_provenance
from . import h6_r2_component_inventory as inventory

ROOT = Path(__file__).resolve().parents[2]
STRICT_ARGUMENTS = ["--layers", "F.Cu", "In2.Cu", "In3.Cu", "B.Cu", "--track-width", "0.15",
                    "--via-size", "0.4", "--via-drill", "0.2", "--keep-input-copper", "--no-stub-layer-swap",
                    "--no-fix-drc-settings", "--fab-tier", "standard", "--escalation", "off", "--strict-sizes"]
PENDING_PAD_PROTECTION_PATCH_SHA256 = "0dec1ef898beec101580f496a7ef48a9042cb45ad77b29b2468e26c3f8a63067"


def require(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Recipe:
    name: str
    direction: str = "forward"
    ordering: str = "mps"
    grid_step: float = 0.05
    via_cost: int = 75
    heuristic_weight: float | None = None
    rip_selected: bool = False
    max_ripup: int | None = None
    blocker_select: str | None = None
    abandon_metric: str = "stranded"
    endpoint_reservations_all: bool = False
    dense_first: bool = False
    pending_pad_protection: bool = False
    max_iterations: int | None = None
    dynamic_iterations_grace: int = 0
    board_edge_clearance: float = 0.30
    clearance: float = 0.16
    net_order: list[str] | tuple[str, ...] | None = None

    def __post_init__(self):
        require(isinstance(self.name, str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", self.name), "Invalid recipe name")
        for value, allowed, label in ((self.direction, ("forward", "backward"), "direction"),
                                      (self.ordering, ("mps", "inside_out", "original", "bus"), "ordering"),
                                      (self.grid_step, (0.025, 0.05, 0.1), "grid_step"),
                                      (self.heuristic_weight, (None, 1.3, 1.6, 2.3), "heuristic_weight"),
                                      (self.blocker_select, (None, "count", "near-target", "bidir", "mincut", "cost"), "blocker_select"),
                                      (self.abandon_metric, ("stranded", "total-pads"), "abandon_metric")):
            require(value in allowed, "Unsupported recipe " + label)
        for value, allowed, label in ((self.via_cost, (50, 75, 125), "via_cost"),
                                      (self.max_ripup, (None, 0, 3, 5, 8), "max_ripup"),
                                      (self.max_iterations, (None, 200000, 1000000), "max_iterations"),
                                      (self.dynamic_iterations_grace, (0, 1, 2), "dynamic_iterations_grace")):
            require(value in allowed and (value is None or type(value) is int), "Unsupported recipe " + label)
        require(type(self.rip_selected) is bool, "rip_selected must be boolean")
        require(type(self.endpoint_reservations_all) is bool and type(self.dense_first) is bool,
                "Endpoint reservation/dense-first controls must be boolean")
        require(type(self.pending_pad_protection) is bool, "pending_pad_protection must be boolean")
        for value, lo, hi in ((self.clearance, 0.16, 0.5), (self.board_edge_clearance, 0.30, 1.0)):
            require(type(value) in (int, float) and math.isfinite(value) and lo <= value <= hi, "Recipe cannot weaken clearance floors")
        require(self.net_order is None or isinstance(self.net_order, (list, tuple))
                and all(isinstance(n, str) for n in self.net_order), "net_order must be an exact name sequence")


def _git(tool, *args):
    return subprocess.check_output(["git", "-C", str(tool), *args], timeout=10)


def _engine_pins(tool, python, patch, profile):
    require(re.fullmatch(r"[0-9a-f]{64}", patch) is not None, "Invalid engine patch SHA256")
    require(_git(tool, "rev-parse", "HEAD").decode().strip() == profile["engine"]["source_commit"], "Engine base changed")
    require(hashlib.sha256(_git(tool, "diff", "--binary", "HEAD", "--")).hexdigest() == patch, "Engine tracked patch changed")
    require(sha(tool / "rust_router/grid_router.so") == profile["engine"]["macos_arm64_binary_sha256"], "Engine binary changed")
    others = _git(tool, "ls-files", "--others", "-z", "--", "py_router").decode().split("\0")
    require(all(not n or ("__pycache__" in Path(n).parts and n.endswith(".pyc")) for n in others), "Untracked engine runtime files")
    require(python.is_file(), "Prepared engine Python is missing")


def _case(path):
    case = read(path)
    require(case["project"] in inventory.PROJECTS and isinstance(case["nets"], list) and case["nets"], "Invalid case project/nets")
    names = [r["kicad_net"] for r in case["nets"]]
    require(all(isinstance(n, str) and n and not n.startswith(("-", "!"))
                and not any(c in n for c in "*?[]\n\r") for n in names) and len(names) == len(set(names)), "Net names must be unique exact literals")
    for row in case["nets"]:
        require(type(row["remaining_connections"]) is int and row["remaining_connections"] > 0
                and isinstance(row["exact_ref_pads"], list) and row["exact_ref_pads"]
                and all(isinstance(p, str) and "." in p and not any(c.isspace() for c in p) for p in row["exact_ref_pads"]), "Malformed endpoint/remaining scope")
    require(type(case["scope"]["expected_connections"]) is int
            and sum(r["remaining_connections"] for r in case["nets"]) == case["scope"]["expected_connections"], "Case total mismatch")
    for name, digest in case["baseline_sha256"].items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts
                and (ROOT / name).resolve().is_relative_to(ROOT)
                and re.fullmatch(r"[0-9a-f]{64}", digest), "Invalid original source hash/path")
    verified_sources(case)
    return case


def authority(case_path, *, engine_root, engine_python, engine_patch_sha256):
    """Freeze canonical case, production inputs, exact engine and local check code."""
    path, tool, python = Path(case_path).resolve(), Path(engine_root).resolve(), Path(engine_python).absolute()
    require(path.parent == ROOT / "hardware/layout/benchmarks", "Use a canonical repository case")
    case, profile = _case(path), read(PROFILE)
    require(profile["execution"]["arguments"] == STRICT_ARGUMENTS
            and profile["engine"]["entrypoint"] == "py_router/route.py", "Strict base profile changed")
    _engine_pins(tool, python, engine_patch_sha256, profile)
    expected_rows, sources, _ = inventory.expected_inventory()
    # Local code closure is independent of CLI/work scripts and old summaries.
    paths = [*sorted((ROOT / "hardware/layout").glob("h6_r2_*.py")),
             *sorted((ROOT / "hardware/ecad").glob("h2_r2_*.py")), PROFILE, path]
    sources = {**sources, **{str(p.relative_to(ROOT)): sha(p) for p in paths}}
    return {"case_path": str(path), "case_sha256": sha(path), "profile_sha256": sha(PROFILE),
            "engine_root": str(tool), "engine_python": str(python), "engine_python_sha256": sha(python),
            "engine_python_realpath": str(python.resolve()), "engine_patch_sha256": engine_patch_sha256,
            "engine_commit": profile["engine"]["source_commit"], "engine_binary_sha256": profile["engine"]["macos_arm64_binary_sha256"],
            "baseline_inputs": input_hashes(case["project"], ROOT), "source_hashes": dict(sorted(sources.items())),
            "inventory_expected_sha256": inventory.identity_hash(expected_rows)}


def _authority_check(auth):
    require(authority(auth["case_path"], engine_root=auth["engine_root"], engine_python=auth["engine_python"],
                      engine_patch_sha256=auth["engine_patch_sha256"]) == auth, "Authority/input/code changed")


def _relative(case):
    p = case["project"]
    return Path(f"hardware/ecad/kicad/{p}/{p}.kicad_pcb")


def _payload(ctx):
    return {k: v for k, v in ctx.items() if k not in ("receipt_path", "receipt_sha256")}


def _seal(ctx, filename):
    path = Path(ctx["folder"]) / filename
    write(path, _payload(ctx))
    ctx.update(receipt_path=str(path), receipt_sha256=sha(path))


def _load(path):
    ctx = read(path)
    ctx.update(receipt_path=str(path), receipt_sha256=sha(path))
    return ctx


def recipe_dict(case, recipe):
    """Validate an optional exact net permutation and return effective settings."""
    recipe = recipe if isinstance(recipe, Recipe) else Recipe(**recipe)
    values = asdict(recipe)
    names = [r["kicad_net"] for r in case["nets"]]
    values["net_order"] = list(recipe.net_order) if recipe.net_order is not None else names
    require(Counter(values["net_order"]) == Counter(names), "net_order is not an exact case permutation")
    return values


def _settings(ctx, case):
    recipe = Recipe(**ctx["recipe"])
    names = [r["kicad_net"] for r in case["nets"]]
    require(recipe.net_order is not None and Counter(recipe.net_order) == Counter(names), "net_order is not an exact case permutation")
    folder, auth = Path(ctx["folder"]), ctx["authority"]
    profile = read(PROFILE)
    env = {**profile["execution"]["environment"], "PYTHONHASHSEED": "0", "PYTHONUNBUFFERED": "1",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPYCACHEPREFIX": str(folder / "python-cache"),
           "KICAD_SMOOTH_ROUTE": "0", "KICAD_INRUN_FLOOR_SYNC": "0",
           "KICAD_DYNAMIC_ITERATIONS_GRACE": str(recipe.dynamic_iterations_grace)}
    if recipe.endpoint_reservations_all:
        env["KICAD_FINE_PITCH_PSEUDO_STUBS"] = "0"
    if recipe.dense_first:
        env["KICAD_MULTIPOINT_DENSE_FIRST"] = "1"
    if recipe.pending_pad_protection:
        require(auth["engine_patch_sha256"] == PENDING_PAD_PROTECTION_PATCH_SHA256,
                "pending_pad_protection requires the supported pinned engine patch")
        env["KICAD_PENDING_PAD_PROTECTION"] = "1"
    relative = _relative(case)
    command = [auth["engine_python"], str(Path(auth["engine_root"]) / "py_router/route.py"),
               str(Path(ctx["baseline_root"]) / relative), str(Path(ctx["candidate_root"]) / relative),
               "--nets", *recipe.net_order, *STRICT_ARGUMENTS, "--fab-overrides", str(folder / "floors.txt"),
               "--grid-step", str(recipe.grid_step), "--via-cost", str(recipe.via_cost), "--ordering", recipe.ordering,
               "--json-out", str(folder / "candidate/engine-summary.json"), "--direction", recipe.direction,
               "--clearance", str(recipe.clearance), "--board-edge-clearance", str(recipe.board_edge_clearance),
               "--ripup-abandon-metric", recipe.abandon_metric]
    for name, value in (("--heuristic-weight", recipe.heuristic_weight), ("--max-ripup", recipe.max_ripup),
                        ("--ripup-blocker-select", recipe.blocker_select), ("--max-iterations", recipe.max_iterations)):
        if value is not None:
            command += [name, str(value)]
    if recipe.rip_selected:
        command += ["--rip-existing-nets", *recipe.net_order]
    return env, command


def check_context(ctx):
    """Reject changed authority, sealed settings, copper or nonboard dependencies."""
    folder, auth = Path(ctx["folder"]), ctx["authority"]
    require(folder == folder.resolve() and folder != ROOT / "work" and folder.is_relative_to(ROOT / "work"), "Output must be an isolated work/ directory")
    require(ctx["baseline_root"] == str(folder / "baseline") and ctx["candidate_root"] == str(folder / "candidate"), "Context root paths changed")
    receipt = Path(ctx["receipt_path"])
    require(receipt.parent == folder and sha(receipt) == ctx["receipt_sha256"] and read(receipt) == _payload(ctx), "Context receipt changed")
    _authority_check(auth)
    case = _case(auth["case_path"])
    require(ctx["case"] == case["id"] and sha(folder / "case.json") == auth["case_sha256"]
            and sha(folder / "engine-profile.json") == auth["profile_sha256"]
            and sha(folder / "backend.py") == auth["source_hashes"][str(Path(__file__).resolve().relative_to(ROOT))], "Case/profile/backend snapshot changed")
    for root in (ROOT, folder / "baseline"):
        require(input_hashes(case["project"], root) == auth["baseline_inputs"], "Original input dependencies changed")
    expected = dict(auth["baseline_inputs"], **{str(_relative(case)): ctx["candidate_sha256"]})
    require(input_hashes(case["project"], folder / "candidate") == expected, "Candidate PCB/nonboard dependencies changed")
    require(_settings(ctx, case) == (ctx["environment"], ctx["command"]), "Effective routing recipe changed")
    require((folder / "floors.txt").read_text() == read(PROFILE)["execution"]["fab_overrides_file_contents"], "Fab overrides changed")
    if ctx.get("prepared"):
        proof = read(folder / "baseline-proof.json")
        names = [r["kicad_net"] for r in case["nets"]]
        require(sha(folder / "baseline-proof.json") == ctx["baseline_proof_sha256"]
                and proof["baseline_sha256"] == auth["baseline_inputs"][str(_relative(case))]
                and proof["exact_endpoints_checked"] is True and proof["native_version"] == "10.0.5"
                and proof["selected_remaining"] == [case["scope"]["expected_connections"]] * 2
                and proof["selected_original_copper_and_zones"] == dict.fromkeys(names, 0), "Native baseline proof changed")
    if "engine" in ctx:
        request = {"case": str(folder / "case.json"), "baseline": ctx["baseline_root"],
                   "candidate": ctx["candidate_root"], "board_relative": str(_relative(case))}
        require(read(folder / "worker-request.json") == request
                and sha(folder / "worker-request.json") == ctx["worker_request_sha256"], "Worker request changed")
    return case


def prepare(auth, recipe, outfolder, registry):
    """Construct a fresh cold copy and independently prove all selected nets empty."""
    _authority_check(auth)
    recipe = recipe if isinstance(recipe, Recipe) else Recipe(**recipe)
    case, folder = _case(auth["case_path"]), Path(outfolder).absolute()
    require(folder == folder.resolve() and folder.is_relative_to(ROOT / "work") and folder != ROOT / "work", "Invalid output directory")
    require(not folder.exists() or not any(folder.iterdir()), "Cold output directory is not empty")
    folder.mkdir(parents=True, exist_ok=True)
    values = recipe_dict(case, recipe)
    ctx = {"case": case["id"], "folder": str(folder), "baseline_root": str(folder / "baseline"),
           "candidate_root": str(folder / "candidate"), "recipe": values, "authority": auth, "prepared": False,
           "candidate_sha256": auth["baseline_inputs"][str(_relative(case))]}
    ctx["environment"], ctx["command"] = _settings(ctx, case)
    for name in auth["baseline_inputs"]:
        path = folder / "baseline" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, path)
    shutil.copytree(folder / "baseline", folder / "candidate")
    shutil.copy2(auth["case_path"], folder / "case.json")
    shutil.copy2(PROFILE, folder / "engine-profile.json")
    shutil.copy2(__file__, folder / "backend.py")
    (folder / "floors.txt").write_text(read(PROFILE)["execution"]["fab_overrides_file_contents"])
    _seal(ctx, "prepare-request.json")
    check_context(ctx)
    process = registry.run([str(KICAD_PYTHON), "-m", "hardware.layout.h6_r2_batch_backend", "--prove", ctx["receipt_path"]],
                           folder / "baseline-proof.log", 120, cwd=ROOT)
    check_context(ctx)
    require(type(process["exit_code"]) is int and process["exit_code"] == 0, "Native cold baseline proof failed")
    ctx.update(prepared=True, baseline_proof_process=process, baseline_proof_sha256=sha(folder / "baseline-proof.json"))
    _seal(ctx, "prepared-context.json")
    check_context(ctx)
    return ctx


def engine(ctx, registry, timeout=900):
    """Route exactly once; return the sealed context, including nonzero exits."""
    case = check_context(ctx)
    require(ctx.get("prepared") is True and "engine" not in ctx, "Engine requires a fresh prepared context")
    limit = 1800 if ctx["recipe"]["grid_step"] == 0.025 else 900
    require(type(timeout) in (int, float) and 0 < timeout <= limit, f"Engine timeout must be bounded to {limit} seconds")
    folder = Path(ctx["folder"])
    frozen = copy.deepcopy(ctx)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("KICAD_", "PYTHON"))}
    env.update(ctx["environment"])
    process = registry.run(ctx["command"], folder / "engine.log", timeout, cwd=ROOT, env=env)
    require(ctx == frozen and sha(Path(ctx["receipt_path"])) == ctx["receipt_sha256"]
            and read(ctx["receipt_path"]) == _payload(ctx), "Context changed during engine execution")
    _authority_check(ctx["authority"])
    require(input_hashes(case["project"], folder / "baseline") == ctx["authority"]["baseline_inputs"], "Engine changed cold input")
    discarded = restore_dependencies(folder / "baseline", folder / "candidate", ctx["authority"]["baseline_inputs"], _relative(case))
    ctx.update(engine=process, discarded_dependency_edits=discarded, candidate_sha256=sha(folder / "candidate" / _relative(case)))
    write(folder / "worker-request.json", {"case": str(folder / "case.json"), "baseline": ctx["baseline_root"],
                                          "candidate": ctx["candidate_root"], "board_relative": str(_relative(case))})
    ctx["worker_request_sha256"] = sha(folder / "worker-request.json")
    _seal(ctx, "engine-context.json")
    check_context(ctx)
    return ctx


@contextmanager
def _native_lock(cancel, deadline):
    with (ROOT / "work/route-board.lock").open("a") as lock:
        while True:
            require(not cancel.is_set(), "Cancelled while waiting for native validation")
            require(time.monotonic() < deadline, "Native queue deadline exceeded")
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                cancel.wait(0.1)
        yield


def geometry_pass(grade, target):
    remaining, native = grade.get("selected_remaining"), grade.get("native_unconnected")
    return (all(grade.get(k) is True for k in ("geometry_pass", "candidate_pass", "selected_complete", "drc_checked",
                "candidate_unchanged_during_checks", "preservation_recipe_pass", "dependencies_unchanged"))
            and remaining == [target, 0] and all(type(n) is int for n in remaining)
            and isinstance(native, list) and len(native) == 2 and all(type(n) is int and n >= 0 for n in native)
            and native[0] > native[1] and type(grade.get("resolved_connections")) is int
            and grade["resolved_connections"] == native[0] - native[1]
            and isinstance(grade.get("added_geometry_signature"), str) and re.fullmatch(r"[0-9a-f]{64}", grade["added_geometry_signature"]) is not None
            and grade.get("kicad_version") == "10.0.5"
            and grade.get("electrically_qualified") is False
            and all(grade.get(k) == 0 and type(grade.get(k)) is int for k in ("drc_selected_unconnected", "drc_violations", "schematic_parity_errors"))
            and grade.get("failures") == {} and grade.get("roi_escaped_objects") == [] and grade.get("all_net_regressions") == {})


def preflight(ctx, registry, timeout=180):
    """Bounded native CLI check on the prepared baseline copy, never production."""
    case = check_context(ctx)
    require(ctx.get("prepared") is True and "engine" not in ctx, "Preflight requires a prepared cold copy")
    require(type(timeout) in (int, float) and 0 < timeout <= 180, "Native timeout must be bounded to 180 seconds")
    folder, baseline = Path(ctx["folder"]), Path(ctx["baseline_root"])
    report = baseline / "work/preflight-drc.json"
    receipt = report.with_name(report.name + ".provenance.json")
    require(not report.exists() and not receipt.exists(), "Preflight evidence already exists")
    with _native_lock(registry.cancel_event, time.monotonic() + 300):
        check_context(ctx)
        process = registry.run([str(KICAD_PYTHON), "-m", "hardware.layout.h6_r2_batch_backend", "--native-probe", ctx["receipt_path"]],
                               folder / "preflight.log", timeout, cwd=ROOT)
        check_context(ctx)
        require(type(process["exit_code"]) is int and process["exit_code"] == 0, "Native preflight failed")
        validate_provenance(report, case["project"], baseline)
        value = read(report)
        require(value["kicad_version"] == "10.0.5" and value["violations"] == [] and value["schematic_parity"] == [], "Baseline native DRC/parity failure")
    result = {"pass": True, "process": process, "report_sha256": sha(report), "receipt_sha256": sha(receipt),
              "board_sha256": ctx["candidate_sha256"], "drc_violations": 0, "schematic_parity_errors": 0,
              "native_unconnected": len(value["unconnected_items"]), "kicad_version": value["kicad_version"]}
    write(folder / "preflight-result.json", result)
    return result


def validate(ctx, registry, timeout=180, queue_deadline=None):
    """One fresh serial native worker + independent two-board inventory; no reroute."""
    case = check_context(ctx)
    require(type(ctx["engine"]["exit_code"]) is int and ctx["engine"]["exit_code"] == 0, "Failed engine cannot be validated")
    require(type(timeout) in (int, float) and 0 < timeout <= 180, "Native timeout must be bounded to 180 seconds")
    folder, candidate = Path(ctx["folder"]), Path(ctx["candidate_root"])
    native = candidate / "work/native-drc.json"
    paths = [candidate / "validation.json", native, native.with_name(native.name + ".provenance.json"), folder / "inventory.json"]
    require(not any(p.exists() for p in paths), "Native evidence already exists; stale/repeated validation forbidden")
    deadline = min(time.monotonic() + 300, queue_deadline) if queue_deadline is not None else time.monotonic() + 300
    with _native_lock(registry.cancel_event, deadline):
        check_context(ctx)
        worker = registry.run([str(KICAD_PYTHON), str(ROOT / "hardware/layout/h6_r2_autorouter_benchmark.py"),
                               "--worker", str(folder / "worker-request.json")], folder / "validation.log", timeout, cwd=ROOT)
        check_context(ctx)
        require(type(worker["exit_code"]) is int and worker["exit_code"] == 0, "Independent native worker failed")
        composition = registry.run([str(KICAD_PYTHON), "-m", "hardware.layout.h6_r2_batch_backend", "--inventory", ctx["receipt_path"]],
                                   folder / "inventory.log", 120, cwd=ROOT)
        check_context(ctx)
        require(type(composition["exit_code"]) is int and composition["exit_code"] == 0, "Native component inventory failed")
    grade, drc, components = read(paths[0]), read(native), read(folder / "inventory.json")
    require(grade["candidate_sha256"] == ctx["candidate_sha256"] and sha(native) == grade["drc_report_sha256"]
            and sha(paths[2]) == grade["drc_receipt_sha256"], "Candidate/native evidence hash mismatch")
    validate_provenance(native, case["project"], candidate)
    require(grade["drc_violations"] == len(drc["violations"])
            and grade["schematic_parity_errors"] == len(drc["schematic_parity"])
            and grade["drc_types"] == sorted({r["type"] for r in drc["violations"]}), "Native observations disagree")
    boards = {p: sha(ROOT / f"hardware/ecad/kicad/{p}/{p}.kicad_pcb") for p in inventory.PROJECTS}
    boards[case["project"]] = ctx["candidate_sha256"]
    require(components["status"] == "pass" and components["findings"] == [] and components["read_only"] is True
            and components["board_sha256"] == boards and components["expected_inventory_sha256"] == ctx["authority"]["inventory_expected_sha256"]
            and components["source_sha256"] == inventory.expected_inventory()[1], "Component inventory evidence mismatch")
    check_context(ctx)
    result = {"geometry_pass": geometry_pass(grade, case["scope"]["expected_connections"]), "validation": grade,
              "engine": ctx["engine"], "validation_process": worker, "inventory_process": composition,
              "candidate_sha256": ctx["candidate_sha256"], "validation_sha256": sha(paths[0]),
              "inventory_sha256": sha(folder / "inventory.json"), "drc_report_sha256": sha(native),
              "drc_receipt_sha256": sha(paths[2]), "production_ready": False, "electrically_qualified": False}
    write(folder / "checked-result.json", result)
    return result


def _prove(ctx):
    import pcbnew
    from .h6_r2_route_candidate import grade_candidate
    case = check_context(ctx)
    board_path = Path(ctx["baseline_root"]) / _relative(case)
    expected = ctx["authority"]["baseline_inputs"][str(_relative(case))]
    grade = grade_candidate(board_path, board_path, case["nets"], expected)
    target = case["scope"]["expected_connections"]
    require(grade.get("preservation_recipe_pass") is True and grade.get("selected_remaining") == [target, target]
            and set(grade.get("failures", {})) == {"no_positive_progress"}, "Native baseline endpoints/connectivity mismatch")
    board = pcbnew.LoadBoard(str(board_path))
    counts = Counter(str(item.GetNetname()) for item in board.GetTracks())
    counts.update(str(z.GetNetname()) for z in board.Zones() if not z.GetIsRuleArea())
    selected = {row["kicad_net"]: counts[row["kicad_net"]] for row in case["nets"]}
    require(not any(selected.values()), "Selected original net contains copper or a zone")
    require(pcbnew.GetBuildVersion() == "10.0.5", "Native KiCad must be 10.0.5")
    check_context(ctx)
    write(Path(ctx["folder"]) / "baseline-proof.json", {"baseline_sha256": expected, "exact_endpoints_checked": True,
          "selected_remaining": [target, target], "selected_original_copper_and_zones": selected, "native_version": pcbnew.GetBuildVersion()})


def _inventory(ctx):
    case = check_context(ctx)
    boards = {p: ROOT / f"hardware/ecad/kicad/{p}/{p}.kicad_pcb" for p in inventory.PROJECTS}
    boards[case["project"]] = Path(ctx["candidate_root"]) / _relative(case)
    value = inventory.build(boards)
    check_context(ctx)
    write(Path(ctx["folder"]) / "inventory.json", value)
    require(value["status"] == "pass" and not value["findings"], "Independent inventory failed")


def _native_probe(ctx):
    from .h6_r2_drc import run_drc
    case = check_context(ctx)
    run_drc(case["project"], Path("work/preflight-drc.json"), root=Path(ctx["baseline_root"]))
    check_context(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Internal read-only native proof/inventory modes; no router")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prove", type=Path)
    modes.add_argument("--inventory", type=Path)
    modes.add_argument("--native-probe", type=Path)
    args = parser.parse_args()
    (_prove if args.prove else _inventory if args.inventory else _native_probe)(_load((args.prove or args.inventory or args.native_probe).resolve()))
