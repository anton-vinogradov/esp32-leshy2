#!/usr/bin/env python3
"""Nonproduction MAIN RILM comparison using current inputs and pinned EDG E192.

Only a conditional Eq5 resistor nominal is selected, never an MPN or circuit.
Run with the prepared EDG Python environment; no downloads, JVM or LLM calls.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import signal
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import synthesize_main_feedback as source
from h6_passive_synthesis import NominalWindow
from h6_power_corner_math import ResistanceDriftBudget, resistor_interval, efuse_current_interval
import h3_r2_inrush_watchdog as inrush
from hardware.verification import h6_r2_power_startup as power
from hardware.verification import h6_r2_power_domain_crossings as crossings
from route_board import keep_awake

BUDGETS = {
    "initial_plus_tcr": (),
    "additional_solder_and_load_life_diagnostic": (
        ResistanceDriftBudget("solder", ".01", ".05"),
        ResistanceDriftBudget("load_life", ".01", ".05")),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact(value):
    require(type(value) in (str, int, Decimal, F), "exact finite numeric input required")
    if isinstance(value, F):
        return value
    number = Decimal(value)
    require(number.is_finite(), "finite input required")
    return F(number)


def decimal_text(value):
    """EDG decimal nominals must not be silently rounded before verification."""
    value = exact(value)
    with localcontext() as context:
        context.prec = 100
        result = str(Decimal(value.numerator) / Decimal(value.denominator))
    require(F(result) == value, "nominal is not exactly representable by the decimal kernel")
    return result


def source_paths():
    h3 = source.h3
    return sorted({Path(__file__), Path(source.__file__), Path(power.__file__), Path(inrush.__file__),
        ROOT / "tools/route_board.py", ROOT / "hardware/verification/h6_passive_synthesis.py",
        *(ROOT / p for p in power.INPUTS.values()), *inrush.SOURCES, *crossings.source_paths(),
        h3.CONTRACT, h3.LOADS, h3.STATES, h3.METHODS, h3.H0, h3.INSTANCES, h3.NETS,
        h3.DEVICES, h3.CORNER_MATH, h3.OUTPUT, Path(h3.__file__)})


def snapshot(paths):
    for path in paths:
        require(path.is_absolute() and path.resolve() == path and path.is_relative_to(ROOT),
                "noncanonical or escaped source path")
    return source.snapshot(paths)


def load_current():
    """Current ledger provenance and regenerated reports, not fresh KiCad export."""
    paths = source_paths()
    before = snapshot(paths)
    source.load_current()  # Existing full H3 regeneration and fitted identity checks.
    data = {key: json.loads((ROOT / p).read_text(), parse_float=Decimal) for key, p in power.INPUTS.items()}
    source.verify_regenerated_report(json.loads((ROOT / power.INPUTS["inrush"]).read_text()), inrush.build()[1])
    data["material"] = crossings.load(ROOT / crossings.INPUTS["material"])
    contracts = {key: crossings.load(ROOT / p) for key, p in crossings.LEDGER_CONTRACTS.items()}
    crossings.validate_provenance(data, contracts, before)
    reviews = crossings.semantics.reviewed_maps(
        [crossings.load(p) for p in crossings.semantics.MAPS], data["material"]["groups"])
    crossings.indexes(data, reviews)  # Reject duplicates, omissions and material/instance conflicts.
    baseline = power.build()
    power.validate_result(baseline)
    baseline_paths = {*power.INPUTS.values(), "hardware/verification/h6_power_corner_math.py"}
    require(baseline.get("source_sha256") == {p: before[p] for p in baseline_paths},
            "baseline power source inventory/hash differs")
    result = extract(data, baseline)
    require(snapshot(source_paths()) == before, "sources changed while loading")
    return {**result, "baseline_power_review": baseline, "source_sha256": before}


def extract(data, baseline):
    checks = {row["id"]: row for row in baseline["checks"]}
    required = {"h3_current_limit_bound_to_fitted_rilm", "main_feedback_target"}
    required.update("identity:" + name for name in power.PINS)
    required.update("pin:" + name + "." + pin for name, (_, pins) in power.PINS.items() for pin in pins)
    required.update("path:" + name for name in power.PASSIVES)
    require(required <= set(checks) and all(checks[name]["pass"] is True for name in required),
            "current native power identity, topology or fitted model differs")
    rail = data["h3"]["rails"]["3V3_MAIN"]
    model = rail["conditioned_model"]
    spec = model["protection"]
    require(spec["nominal_ohm"] == "1650" and spec["gain_tolerance_fraction"] == "0.10"
            and spec["equation_constant_a_ohm"] == "5747", "reviewed RILM model differs")
    current = exact(data["margins"]["worst_current_by_rail"]["3V3_MAIN"]["load_ma"]) / 1000
    reserve = exact(data["h3"]["policy"]["steady_current_reserve_minimum_percent"])
    floor = exact(data["h0"]["power_rebaseline"]["h1_required_envelope"]["step_a_min"])
    rows = [r for r in data["inrush"]["startup_envelopes"] if r["rail"] == "3V3_MAIN"]
    require(len(rows) == 1, "missing or duplicate MAIN startup case")
    startup = exact(rows[0]["combined_current_ma"]) / 1000
    require(current > 0 and startup >= current and reserve == 25 and floor >= F("4.25"),
            "current, reserve, step or startup requirements are missing/weakened")
    upper = exact(model["converter_current"]["rated_output_a"])
    require(upper == exact(rail["converter_min_a"]) == 6
            and exact(data["h1"]["main_power_cell"]["converter"]["continuous_rating_a"]) == 6,
            "upper ceiling must be 6 A continuous, not the valley trip limit")
    h1 = data["h1"]["main_power_cell"]["efuse_threshold_resistor"]
    require(exact(h1["resistance_ohm"]) == 1180, "H1 intended resistance differs")
    demands = {"h0_step_a": floor, "pf03_reserve_a": current * (1 + reserve / 100),
               "existing_inrush_a": startup}
    return {"spec": spec, "h1_identity_reference_only": h1["mpn"],
            "requirements_a": {key: str(value) for key, value in demands.items()},
            "required_lower_a": max(demands.values()), "strict_upper_a": upper}


def inverse(required, ceiling, spec, budgets):
    """Exact affine inversion of initial + ordered stress + TCR resistance.

    Lower nominal bound is OPEN because the high trip current must be <6 A.
    The independent forward check uses the existing Decimal resistor kernel.
    """
    required, ceiling = exact(required), exact(ceiling)
    require(required > 0 and ceiling > 0, "positive current bounds required")
    # Existing kernel validates finite fractions, temperature ordering and budgets.
    resistor_interval("1650", spec["initial_tolerance_fraction"], spec["tcr_ppm_per_c"],
                      *spec["temperature_c"], budgets, spec["reference_temperature_c"])
    t, gain, k = (exact(spec[name]) for name in
                  ("initial_tolerance_fraction", "gain_tolerance_fraction", "equation_constant_a_ohm"))
    require(0 <= gain < 1 and k > 0, "invalid eFuse equation")
    thermal = exact(spec["tcr_ppm_per_c"]) / 1000000 * max(
        abs(exact(v) - exact(spec["reference_temperature_c"])) for v in spec["temperature_c"])
    low, high, lo_offset, hi_offset = 1-t, 1+t, F(0), F(0)
    for budget in budgets:
        f, a = F(budget.fraction), F(budget.absolute_ohm)
        low, high = low*(1-f), high*(1+f)
        lo_offset, hi_offset = lo_offset*(1-f)-a, hi_offset*(1+f)+a
    low, lo_offset = low*(1-thermal), lo_offset*(1-thermal)
    high, hi_offset = high*(1+thermal), hi_offset*(1+thermal)
    minimum = max(F(0), (k*(1+gain)/ceiling-lo_offset)/low)
    maximum = (k*(1-gain)/required-hi_offset)/high
    return NominalWindow(minimum, maximum,
                         None if minimum < maximum else "incompatible_strict_current_bounds")


def forward(nominal, spec, budgets, required, ceiling):
    """Existing spread kernel, then exact rational Eq5; no inverse/EDG reuse."""
    nominal, required, ceiling = exact(nominal), exact(required), exact(ceiling)
    resistance = resistor_interval(decimal_text(nominal), spec["initial_tolerance_fraction"],
        spec["tcr_ppm_per_c"], *spec["temperature_c"], budgets, spec["reference_temperature_c"])
    k, gain = exact(spec["equation_constant_a_ohm"]), exact(spec["gain_tolerance_fraction"])
    require(k / F(resistance.maximum) > exact(spec["configured_accuracy_domain_min_a_exclusive"]),
            "configured current falls outside reviewed Eq5 accuracy domain")
    lower, upper = k*(1-gain)/F(resistance.maximum), k*(1+gain)/F(resistance.minimum)
    approximate = efuse_current_interval(resistance, spec["gain_tolerance_fraction"], spec["equation_constant_a_ohm"])
    return {"nominal_ohm": decimal_text(nominal),
            "resistance_ohm": [str(resistance.minimum), str(resistance.maximum)],
            "current_a_exact": [str(lower), str(upper)],
            "current_a_display": [str(approximate.minimum), str(approximate.maximum)],
            "lower_margin_a_exact": str(lower-required), "strict_upper_margin_a_exact": str(ceiling-upper),
            "numerical_constraints_met": lower >= required and upper < ceiling,
            "qualified": False}


def compare(data, chooser=source.choose_edg):
    spec, required, ceiling = data["spec"], data["required_lower_a"], data["strict_upper_a"]
    require(exact(ceiling) == 6, "fixed comparison ceiling is strictly 6 A continuous")
    nominal = {"current_fitted": F(spec["nominal_ohm"]), "h1_intended_not_fitted": F(1180)}
    selections = []
    for name, budgets in BUDGETS.items():
        window = inverse(required, ceiling, spec, budgets)
        row = {"budget": name, "continuous_feasible": window.feasible,
               "nominal_ohm_exact": [str(window.minimum_ohm), str(window.maximum_ohm)],
               "minimum_exclusive": True, "maximum_inclusive": True,
               "selected_nominal_ohm": None, "qualified": False,
               "status": "conditional_infeasible"}
        if window.feasible:
            candidate = chooser(window)
            row["status"] = "preferred_selector_found_no_candidate"
            if candidate is not None:
                require(type(candidate) is F and window.minimum_ohm < candidate <= window.maximum_ohm,
                        "selector candidate outside exact open/closed nominal bounds")
                check = forward(candidate, spec, budgets, required, ceiling)
                require(check["numerical_constraints_met"], "selector failed independent forward check")
                row.update(status="conditional_candidate", selected_nominal_ohm=decimal_text(candidate))
                nominal["synthesized_for_" + name] = candidate
        selections.append(row)
    return {"selections": selections, "comparisons": [
        {"id": name, "budget": budget, **forward(value, spec, stresses, required, ceiling)}
        for name, value in nominal.items() for budget, stresses in BUDGETS.items()]}


def run(chooser=source.choose_edg):
    started = time.monotonic()
    data = load_current()
    result = compare(data, chooser)
    require(snapshot(source_paths()) == data["source_sha256"], "sources changed during comparison")
    return {**result, "schema_version": 1, "status": "not_qualified", "qualified": False,
        "production_mpn_selected": False, "startup_proven": False, "gate_closed": False,
        "scope": "Conditional MAIN RILM nominal comparison; current H2 ledger provenance, not fresh KiCad export",
        "requirements_a_exact": data["requirements_a"], "required_lower_a_exact": str(data["required_lower_a"]),
        "strict_upper_a": "6", "h1_identity_reference_only": data["h1_identity_reference_only"],
        "resistor_class_hypothesis": data["spec"],
        "diagnostic_stress_budgets": {name: [{"name": b.name, "fraction": str(b.fraction),
            "absolute_ohm": str(b.absolute_ohm)} for b in values] for name, values in BUDGETS.items()},
        "baseline_power_review": data["baseline_power_review"],
        "selector": {"name": "EDG E192", "version": "0.5.2", "source_sha256": source.EDG_SELECTOR_SHA256},
        "selection_policy": "EDG preferred-number feasibility only; not maximum-margin optimization or a production recommendation",
        "source_sha256": data["source_sha256"], "model_decisions_inside_command": 0,
        "elapsed_s": round(time.monotonic()-started, 6),
        "limitations": [
            "Candidate nominals assume the fitted 1%, 100ppm/C class; H1 Yageo identity is reference-only, not a reviewed candidate class",
            "Named sequential solder/load-life allowances are diagnostics, not a combined lifetime guarantee",
            "TI Eq5 accuracy/test conditions do not qualify actual VIN, startup, foldback, thermal or PCB behavior",
            "All baseline PG/voltage/source/AON findings remain open; no counterfactual is inserted into the native review",
            "No MPN adoption, stock acceptance, schematic/PCB writes, requirement relaxation or physical qualification"]}


def main():
    try:
        def interrupted(*_):
            raise KeyboardInterrupt("comparison cancelled")
        signal.signal(signal.SIGTERM, interrupted)
        work = ROOT / "work"
        work.mkdir(exist_ok=True)
        require(work.resolve() == work and not work.is_symlink(), "unsafe work directory")
        directory = Path(tempfile.mkdtemp(prefix="main-current-limit-", dir=work))
        awake = {}
        with keep_awake(awake, directory):
            result = run()
        require(snapshot(source_paths()) == result["source_sha256"], "sources changed before publication")
        result["caffeinate"] = awake
        path = directory / "result.json"
        with path.open("x") as stream:
            stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
        require(json.loads(path.read_text()) == result, "persisted report differs")
        print(json.dumps({"status": result["status"], "qualified": False, "report": str(path),
                          "selected": {r["budget"]: r["selected_nominal_ohm"] for r in result["selections"]}}))
        return 1
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({"status": "execution_error", "qualified": False, "error": str(exc), "report": None}))
        return 130 if isinstance(exc, KeyboardInterrupt) else 2


if __name__ == "__main__":
    raise SystemExit(main())
