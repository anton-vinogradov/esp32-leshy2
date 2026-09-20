#!/usr/bin/env python3
"""Run TI's existing comparator model with native-derived resistive stress loads.

Not a whole-EV simulation: LED and forward diode paths are replaced by shorts,
configurable GPIOs are assumed high-impedance, and unbounded leakage is omitted.
This deliberately tests the simulation mechanism and conditional loading, not
hardware acceptance, worst-case semiconductor behavior or powered-off states.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import signal
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hardware.verification import h6_r2_power_domain_crossings as crossings
from hardware.verification import h6_r2_ev_load_fixture as fixture
from hardware.layout.h6_r2_parallel_process import ProcessRegistry
from tools.route_board import keep_awake
from tools import ngspice_worker

DEFAULT_MODEL = ROOT / "work/ev-source-WnTYZH/snom763.zip"
DEFAULT_LIBRARY = Path("/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.0.dylib")
ARCHIVE_SHA = "ba28ca4a4dc6d26071dc21b77db8cdbedabba88ba5fc51080f26ac1ceb83f1d1"
MODEL_SHA = "d53d28964bcb5aa8ccabd3c826ab6637647c06caa8d1daa7c60b41ed05ddc4b6"
MODEL_MEMBER = "tlv1821.lib"
LIMITATIONS = [
    "TI TLV1821 family macro v1.0 (2022) is a typical single-channel model, not exact TLV1824PWR package qualification",
    "LED and forward diode paths are shorts for a named resistive stress stimulus, not their I-V models",
    "TCA/Safety GPIOs are assumed inputs; software configuration and fault-state contention are not proved",
    "Other diode branches, reverse leakage, receiver leakage and dynamic capacitances are not modeled",
    "Initial resistor tolerance is sampled at -1%; temperature, lifetime and semiconductor corners are not established",
    "Common ground and ideal AON voltage are assumed; delivered rails and return offsets remain unproven",
    "No power-off/transition test: TI explicitly gives artificial mid-supply behavior outside the model's valid range",
    "Convergence and Kirchhoff residuals validate a simulation run, not electrical/physical acceptance",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "missing or symlinked simulation source")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model(path):
    require(sha(path) == ARCHIVE_SHA, "TI model archive changed; review required")
    with zipfile.ZipFile(path) as archive:
        require(archive.namelist().count(MODEL_MEMBER) == 1, "model member absent/duplicate")
        raw = archive.read(MODEL_MEMBER)
    require(hashlib.sha256(raw).hexdigest() == MODEL_SHA, "TI model member changed")
    return raw.decode("ascii").splitlines()


def sources(model, library):
    paths = [Path(__file__), ROOT / "tools/ngspice_worker.py", ROOT / "tools/route_board.py",
             ROOT / "hardware/layout/h6_r2_parallel_process.py", *fixture.source_paths()]
    return {**crossings.snapshot(), **{str(p.relative_to(ROOT)): sha(p) for p in paths},
            str(model.resolve()): sha(model), **{str(p): sha(p) for p in ngspice_worker.runtime_paths(library)}}


def load_fixture(before):
    data = {key: crossings.load(ROOT / path) for key, path in crossings.INPUTS.items()}
    contracts = {key: crossings.load(ROOT / path) for key, path in crossings.LEDGER_CONTRACTS.items()}
    crossings.validate_provenance(data, contracts, before)
    reviews = crossings.semantics.reviewed_maps([crossings.load(p) for p in crossings.semantics.MAPS], data["material"]["groups"])
    return fixture.extract(data, reviews)


def make_cases(native, model):
    require(native.get("full_EV_qualified") is False, "load fixture cannot qualify hardware")
    require(len(native["channels"]) == 2 and {c["id"] for c in native["channels"]} == {"c5", "ir"},
            "exact two-channel case coverage required")
    cases = [{"id": "known-divider", "kind": "control", "request": {
        "netlist": ["Known 3.3-V divider", "vcc rail 0 3.3", "r1 rail out 1000", "r2 out 0 1000", ".end"],
        "vectors": ["v(out)"]}}]
    for channel in native["channels"]:
        # This is a declared diagnostic corner, not an optimization/part choice.
        r = {key: float(channel[key]) * 0.99 for key in
             ("pullup_ohm", "led_series_ohm", "hysteresis_ohm", "threshold_top_ohm", "threshold_bottom_ohm", "diode_or_pullup_ohm")}
        require(all(math.isfinite(v) and v > 0 for v in r.values()), "invalid resistive fixture")
        for voltage in ("2.7", "3.3", "3.6"):
            for state in ("low", "high"):
                ident = f"{channel['id']}-{voltage}-{state}"
                deck = ["TI TLV182x conditional resistive-load stress, not whole-EV model", *model,
                        f"vcc aon 0 {voltage}", f"vdet detector 0 {voltage if state == 'low' else '0'}",
                        "xcmp threshold detector aon 0 comparator_out TLV1821", "vsense ev comparator_out 0",
                        f"rp aon ev {r['pullup_ohm']:.12g}", f"rledshort aon ev {r['led_series_ohm']:.12g}",
                        f"rorshort aon ev {r['diode_or_pullup_ohm']:.12g}",
                        f"rt aon threshold {r['threshold_top_ohm']:.12g}",
                        f"rb threshold 0 {r['threshold_bottom_ohm']:.12g}",
                        f"rf threshold ev {r['hysteresis_ohm']:.12g}", ".temp 25", ".end"]
                cases.append({"id": ident, "kind": "conditional_model", "channel": channel["id"],
                              "aon_v": float(voltage), "state": state, "resistors_ohm": r,
                              "request": {"netlist": deck, "vectors": ["v(ev)", "v(threshold)", "i(vsense)"]}})
    require(len(cases) == 13 and len({c["id"] for c in cases}) == 13, "exact two-channel case coverage required")
    return cases


def validate_values(case, values):
    require(set(values) == set(case["request"]["vectors"]), "worker vector coverage differs")
    require(all(type(v) in (int, float) and math.isfinite(v) for v in values.values()), "nonfinite/nonreal simulation value")
    if case["kind"] == "control":
        require(abs(values["v(out)"] - 1.65) < 1e-9, "known divider control failed")
        return {"known_divider_pass": True}
    r, v, out, threshold = case["resistors_ohm"], case["aon_v"], values["v(ev)"], values["v(threshold)"]
    into_output = sum((v - out) / r[key] for key in ("pullup_ohm", "led_series_ohm", "diode_or_pullup_ohm")) + (threshold - out) / r["hysteresis_ohm"]
    residual = into_output - values["i(vsense)"]
    threshold_residual = (v - threshold) / r["threshold_top_ohm"] + (out - threshold) / r["hysteresis_ohm"] - threshold / r["threshold_bottom_ohm"]
    require(abs(residual) < 1e-9 and abs(threshold_residual) < 1e-9, "independent branch KCL residual too large")
    require(0 <= out <= v + 1e-8 and 0 <= threshold <= v, "model output outside named stimulus")
    require(out < 0.3 if case["state"] == "low" else out > 0.9 * v, "model polarity/load smoke test failed")
    return {"output_kcl_residual_a": residual, "threshold_kcl_residual_a": threshold_residual,
            "model_polarity_smoke_pass": True, "legacy_0_1v_assumption_exceeded_in_this_stress": case["state"] == "low" and out > 0.1}


def run_cases(cases, directory, library, jobs):
    registry = ProcessRegistry(grace_seconds=2)
    def one(case):
        request = directory / (case["id"] + ".request.json")
        request.write_text(json.dumps(case["request"]))
        result = directory / (case["id"] + ".worker.json")
        execution = registry.run([sys.executable, "-B", str(ROOT / "tools/ngspice_worker.py"),
                                  "--library", str(library), "--request", str(request)],
                                 result, 30, cwd=ROOT, stderr_log=directory / (case["id"] + ".stderr.log"))
        require(execution["exit_code"] == 0 and not execution["orphaned_descendants"], "ngspice worker failed: " + case["id"])
        report = json.loads(result.read_text())
        require(report.get("qualified") is False, "worker cannot qualify hardware")
        require(report.get("status") == "worker_execution_success" and report.get("analysis") == "op",
                "unexpected worker execution status")
        request_hash = hashlib.sha256(json.dumps(case["request"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        require(report.get("request_sha256") == request_hash
                and report.get("worker_sha256") == sha(ROOT / "tools/ngspice_worker.py")
                and report.get("library_sha256") == sha(library)
                and report.get("code_model_sha256") == {str(p): sha(p) for p in ngspice_worker.runtime_paths(library)[1:]},
                "worker source/request identity differs")
        values = report["values"]
        check = validate_values(case, values)
        return {"id": case["id"], "values": values, "checks": check, "execution": execution,
                "worker_report": str(result.relative_to(ROOT)), "worker_sha256": sha(result),
                "request_sha256": sha(request)}
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        try:
            futures = [pool.submit(one, case) for case in cases]
            return [future.result() for future in futures]
        finally:
            registry.cancel_all()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-archive", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args(argv)
    def interrupt(signum, frame):
        raise KeyboardInterrupt("simulation cancelled")
    previous = signal.signal(signal.SIGTERM, interrupt)
    directory = None
    try:
        before = sources(args.model_archive, args.library)
        model, native = load_model(args.model_archive), load_fixture(before)
        cases = make_cases(native, model)
        require((ROOT / "work").is_dir() and not (ROOT / "work").is_symlink(), "real work directory required")
        directory = Path(tempfile.mkdtemp(prefix="ev-spice-", dir=ROOT / "work"))
        started, awake, runs = time.monotonic(), {}, []
        with keep_awake(awake, directory):
            for repeat in range(2):
                subdir = directory / str(repeat)
                subdir.mkdir()
                runs.append(run_cases(cases, subdir, args.library, args.jobs))
        first, second = ({row["id"]: row["values"] for row in run} for run in runs)
        require(first == second, "cold process simulation replay differs")
        require(sources(args.model_archive, args.library) == before, "simulation inputs changed")
        report = {"status": "not_qualified", "mechanism_status": "pass", "qualified": False,
                  "native_cad_changed": False, "full_EV_qualified": False, "model_source": {
                      "url": "https://www.ti.com/lit/zip/SNOM763", "archive_sha256": ARCHIVE_SHA,
                      "member": MODEL_MEMBER, "member_sha256": MODEL_SHA, "model_revision": "TLV1821 1.0, 2022-08-29"},
                  "fixture": native, "limitations": LIMITATIONS, "source_sha256": before,
                  "case_count": len(cases), "cold_replays": 2, "jobs": args.jobs,
                  "runs": runs, "elapsed_s": round(time.monotonic() - started, 3), "caffeinate": awake,
                  "model_calls": 0, "model_calls_meaning": "No LLM calls; numerical engine evaluations listed in runs"}
        path = directory / "result.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print(json.dumps({"status": report["status"], "mechanism_status": "pass", "cases": len(cases),
                          "replays": 2, "report": str(path)}))
        return 1
    except (Exception, KeyboardInterrupt) as error:
        print(json.dumps({"status": "cancelled" if isinstance(error, KeyboardInterrupt) else "execution_error",
                          "qualified": False, "report": None, "work_directory": str(directory) if directory else None,
                          "error": f"{type(error).__name__}: {error}"}))
        return 130 if isinstance(error, KeyboardInterrupt) else 2
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(main())
