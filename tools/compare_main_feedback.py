#!/usr/bin/env python3
"""Compare explicit model hypotheses with invariant MAIN load/voltage demands.

Ready EDG chooses both resistor nominals; exact equations reject bad candidates.
Nothing here approves real components, their source conditions, or a PCB.
"""

from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import tempfile
import time

import synthesize_main_feedback as source
from edg_feedback_pair import synthesize_pair
from h6_passive_synthesis import feedback_top_window
from h6_power_corner_math import Interval, _decimal
import h6_ron_source_scope as ron_scope
from route_board import keep_awake

ROOT = source.ROOT
VARIANTS = ROOT / "hardware/verification/h6-main-feedback-variants.json"


def validate_variants(config):
    if set(config) != {"schema_version", "scope", "series", "parallel_impedance_ohm", "impedance_basis", "variants"}:
        raise ValueError("unknown/missing variant configuration fields")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("unsupported variant schema")
    if type(config["series"]) is not int or config["series"] not in (24, 48, 96, 192):
        raise ValueError("unsupported preferred series")
    impedance = Interval(*config["parallel_impedance_ohm"])
    if impedance.minimum <= 0:
        raise ValueError("positive finite parallel impedance required")
    rows = config["variants"]
    if not isinstance(rows, list) or not rows or len(rows) > 32:
        raise ValueError("1..32 explicit variants required")
    ids = set()
    for row in rows:
        if set(row) != {"id", "reference", "resistors", "efuse_ron_ohm", "distribution_drop_v"}:
            raise ValueError("variants may not override load/voltage requirements")
        if not isinstance(row["id"], str) or not row["id"] or row["id"] in ids:
            raise ValueError("missing/duplicate variant identity")
        ids.add(row["id"])
        if row["reference"] not in ("current", "ideal") or row["resistors"] not in ("current", "ideal"):
            raise ValueError("unsupported reference/resistor hypothesis")
        for key in ("efuse_ron_ohm", "distribution_drop_v"):
            if row[key] != "current" and _decimal(row[key], key) < 0:
                raise ValueError("negative series loss cannot compensate a voltage deficit")
    baseline = {"id": "current", "reference": "current", "resistors": "current",
                "efuse_ron_ohm": "current", "distribution_drop_v": "current"}
    if baseline not in rows:
        raise ValueError("unchanged baseline is mandatory")
    return impedance


def demands(data):
    rail, policy = data["rail"], data["policy"]
    d = lambda key: Decimal(str(rail[key]))
    result = {"consumer_min_v": d("load_min_v"), "consumer_max_v": d("load_max_v"),
              "ripple_half_v": d("ripple_pp_v") / 2,
              "raw_min_v": d("nominal_v") * Decimal(str(policy["raw_regulated_voltage_minimum_fraction_of_nominal"])),
              "cases": data["cases"]}
    if not result["cases"] or any(i < 0 for _, i in result["cases"]):
        raise ValueError("missing or negative demand")
    if result["consumer_min_v"] <= 0 or result["consumer_max_v"] < result["consumer_min_v"] or result["ripple_half_v"] < 0:
        raise ValueError("invalid voltage demand")
    return result


def required_average(demand, ron, distribution):
    worst = max(i for _, i in demand["cases"])
    with localcontext() as context:
        context.prec = 50
        current = Decimal(worst.numerator) / Decimal(worst.denominator)
        low = max(demand["raw_min_v"] + demand["ripple_half_v"],
                  demand["consumer_min_v"] + demand["ripple_half_v"] + current * ron + distribution)
        return low, demand["consumer_max_v"] - demand["ripple_half_v"]


def check_consumers(average, demand, ron, distribution):
    low, high = map(F, average)
    ripple, floor, ceiling = (F(demand[key]) for key in ("ripple_half_v", "consumer_min_v", "consumer_max_v"))
    if low - ripple < F(demand["raw_min_v"]) or high + ripple > ceiling:
        raise ValueError("candidate violates invariant raw voltage demand")
    corners = [(name, low - ripple - current * F(ron) - F(distribution)) for name, current in demand["cases"]]
    if any(value < floor for _, value in corners):
        raise ValueError("candidate violates invariant consumer demand")
    worst_name, worst_v = min(corners, key=lambda pair: pair[1])
    return {"checked_load_cases": len(corners), "worst_case": worst_name,
            "minimum_consumer_v_exact": str(worst_v), "lower_margin_v_exact": str(worst_v - floor),
            "upper_raw_margin_v_exact": str(ceiling - high - ripple)}


def compare(data, config, pair_solver=synthesize_pair):
    impedance = validate_variants(config)
    demand = demands(data)
    rail = data["rail"]
    bottom_nominal = data["bottom_nominal"]
    bottom_factors = Interval(data["bottom"].minimum / bottom_nominal, data["bottom"].maximum / bottom_nominal)
    rows = []
    for variant in config["variants"]:
        reference = data["reference"] if variant["reference"] == "current" else Interval(
            rail["conditioned_model"]["vfb_v"]["nominal"], rail["conditioned_model"]["vfb_v"]["nominal"])
        top = data["factors"] if variant["resistors"] == "current" else Interval(1, 1)
        bottom = bottom_factors if variant["resistors"] == "current" else Interval(1, 1)
        ron = Decimal(str(rail["efuse_ron_max_ohm"])) if variant["efuse_ron_ohm"] == "current" else _decimal(variant["efuse_ron_ohm"], "RON")
        distribution = Decimal(str(rail["distribution_drop_v"])) if variant["distribution_drop_v"] == "current" else _decimal(variant["distribution_drop_v"], "distribution")
        minimum, maximum = required_average(demand, ron, distribution)
        # Unit nominal bottom converts the inverse kernel into an exact nominal
        # top/bottom ratio bound. Scaling both resistors cannot repair an empty
        # ratio interval. This statement explicitly excludes feedback leakage.
        window = feedback_top_window(reference, bottom, top, minimum, maximum, Interval(0, 0))
        row = {"id": variant["id"], "hypothesis": variant, "qualified": False,
               "required_average_v": [str(minimum), str(maximum)],
               "continuous_ratio_feasible": window.feasible,
               "nominal_top_bottom_ratio_exact": [str(window.minimum_ohm), None if window.maximum_ohm is None else str(window.maximum_ohm)]}
        if window.feasible:
            result = pair_solver(reference, Interval(minimum, maximum), top, bottom, impedance, Interval(0, 0), series=config["series"])
            row["selection"] = result
            if result["status"] == "conditional_candidate":
                row["consumer_check"] = check_consumers(result["average_v_exact"], demand, ron, distribution)
        else:
            row["selection"] = {"status": "conditional_infeasible", "reason": window.infeasible_reason, "qualified": False}
        # Optimistic continuous upper ceiling, not a safe RON procurement target.
        ceiling = feedback_top_window(reference, bottom, top, 0, maximum, Interval(0, 0))
        worst_i = max(i for _, i in demand["cases"])
        if ceiling.feasible and ceiling.maximum_ohm is not None and worst_i > 0:
            achievable_min = F(reference.minimum) * (1 + ceiling.maximum_ohm * F(top.minimum) / F(bottom.maximum))
            row["continuous_ron_ceiling_ohm_exact"] = str((achievable_min - F(demand["ripple_half_v"]) - F(demand["consumer_min_v"]) - F(distribution)) / worst_i)
        rows.append(row)
    return {"variants": rows, "invariant_demands": {
        **{key: str(value) for key, value in demand.items() if key != "cases"},
        "load_cases_a": [[name, str(current)] for name, current in demand["cases"]]}}


def run():
    start = time.monotonic()
    extra_paths = [VARIANTS, Path(__file__), ROOT / "tools/edg_feedback_pair.py", ROOT / "tools/route_board.py",
                   ron_scope.ROWS_PATH, Path(ron_scope.__file__)]
    extra_before = source.snapshot(extra_paths)
    data = source.load_current()
    result = compare(data, json.loads(VARIANTS.read_text()))
    result["ron_source_scope"] = ron_scope.assess_main(data)
    if source.snapshot(data["paths"]) != data["before"] or source.snapshot(extra_paths) != extra_before:
        raise ValueError("source changed during variant comparison")
    result.update(schema_version=1, status="not_qualified", qualified=False,
                  source_sha256={**data["before"], **extra_before},
                  model_decisions_inside_command=0, elapsed_s=round(time.monotonic() - start, 6),
                  limitations=["Every changed model is a counterfactual, not an available or qualified component",
                               "Load currents, consumer voltage limits, raw floor and ripple allowance never change between variants",
                               "Zero feedback leakage; omitted lifetime, dynamics, startup, current protection, monitor and thermal gates remain open",
                               "VIN applicability and actual hot/current RON are unqualified; no PCB, MPN or purchasing changes",
                               "RON ceilings use continuous ratios with zero spare margin, not purchasable E-series solutions or safe targets"])
    return result


def main():
    try:
        (ROOT / "work").mkdir(exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="feedback-variants-", dir=ROOT / "work"))
        started = time.monotonic()
        awake = {}
        with keep_awake(awake, directory):
            result = run()
        result.update(caffeinate=awake, command_elapsed_s=round(time.monotonic() - started, 6))
        path = directory / "result.json"
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"status": result["status"], "report": str(path), "elapsed_s": result["elapsed_s"],
                          "variants": {r["id"]: r["selection"]["status"] for r in result["variants"]}}))
        return 1
    except (Exception, KeyboardInterrupt) as exc:
        cancelled = isinstance(exc, KeyboardInterrupt)
        print(json.dumps({"status": "cancelled" if cancelled else "execution_error", "error": str(exc), "report": None}))
        return 130 if cancelled else 2


if __name__ == "__main__":
    raise SystemExit(main())
