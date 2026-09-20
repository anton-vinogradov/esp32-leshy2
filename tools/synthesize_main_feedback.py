#!/usr/bin/env python3
"""Read-only MAIN nominal synthesis diagnostic, never a production approval.

Run with the prepared EDG 0.5.2 Python environment. No downloads, JVM, LLM,
PCB edits or MPN selection. The inverse bounds include initial tolerance/TCR;
EDG only chooses an E192 nominal, independently checked by forward arithmetic.
"""

from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
from importlib import metadata
import inspect
from itertools import product
import json
import math
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hardware/verification"))
import h3_r2_rail_margins as h3
from h6_passive_synthesis import feedback_top_window
from h6_power_corner_math import Interval, resistor_interval

F = Fraction
EDG_SELECTOR_SHA256 = "10b23014b3cdc803c833b9134d5ab64259bdac28641222c701d7796fd6190b05"


def snapshot(paths):
    result = {}
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or symlinked source: {path}")
        result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify_regenerated_report(saved, regenerated):
    # Full equality also rejects missing source keys, removed cases and fabricated
    # values, not merely stale hashes in whatever key subset a file declares.
    if json.dumps(saved, sort_keys=True, allow_nan=False) != json.dumps(regenerated, sort_keys=True, allow_nan=False):
        raise ValueError("H3 rail report differs from current in-memory regeneration")


def load_current():
    paths = [h3.CONTRACT, h3.LOADS, h3.STATES, h3.METHODS, h3.H0,
             h3.INSTANCES, h3.NETS, h3.DEVICES, h3.CORNER_MATH, h3.OUTPUT,
             Path(h3.__file__), ROOT / "hardware/verification/h3_r2_current_scope.py",
             ROOT / "hardware/verification/h6_passive_synthesis.py", Path(__file__)]
    before = snapshot(paths)
    _, report = h3.build()  # No writes; verifies fitted identity and topology.
    verify_regenerated_report(json.loads(h3.OUTPUT.read_text()), report)
    contract = json.loads(h3.CONTRACT.read_text())
    devices = json.loads(h3.DEVICES.read_text())["devices"]
    rail = contract["rails"]["3V3_MAIN"]
    spec = rail["conditioned_model"]
    fb = spec["feedback_resistors"]
    observed = report["conditioned_main_model"]["observed_components"]
    resistors = {position: devices[observed[fb[position + "_instance"]]["device_id"]]["electrical_contract"]
                 for position in ("top", "bottom")}
    domains = {}
    for position, electrical in resistors.items():
        domains[position] = resistor_interval(
            "1" if position == "top" else str(electrical["resistance_ohm"]),
            Decimal(str(electrical["tolerance_pct"])) / 100,
            str(electrical["temperature_coefficient_ppm_per_c"]),
            *fb["temperature_c"], reference_temperature_c=fb["reference_temperature_c"])
    cases = [(row["load_case"], F(row["load_ma"]) / 1000)
             for row in report["profile_voltage_corners"] if row["rail"] == "3V3_MAIN"]
    cases += [(name, F(row["load_ma"]) / 1000) for name, row in
              report["declared_target_voltage_corners"]["3V3_MAIN"].items()]
    if not cases or len({name for name, _ in cases}) != len(cases) or any(a < 0 for _, a in cases):
        raise ValueError("missing, duplicate or negative MAIN load cases")
    return dict(paths=paths, before=before, rail=rail, policy=contract["policy"],
                efuse_mpn=observed["main_efuse"]["mpn"],
                reference=Interval(spec["vfb_v"]["minimum"], spec["vfb_v"]["maximum"]),
                bottom=domains["bottom"], factors=domains["top"], cases=cases,
                bottom_nominal=Decimal(str(resistors["bottom"]["resistance_ohm"])))


def choose_edg(window):
    from edg import Range
    from edg.abstract_parts.ESeriesUtil import ESeriesUtil
    source = Path(inspect.getfile(ESeriesUtil))
    if metadata.version("edg") != "0.5.2" or hashlib.sha256(source.read_bytes()).hexdigest() != EDG_SELECTOR_SHA256:
        raise ValueError("unreviewed EDG preferred-number selector")
    # Widen only the search representation, never the accepted exact bounds.
    # One ULP is insufficient: log10 can round both neighbors of 1000 to 3,
    # leaving EDG's end-exclusive exponent range empty. The tiny search halo
    # survives log10 rounding; every proposed nominal still needs exact checks.
    lower = float(window.minimum_ohm) * (1 - 1e-12)
    upper = float(window.maximum_ohm) * (1 + 1e-12)
    if not 0 < lower <= upper < math.inf:
        raise ValueError("nominal window cannot be represented by EDG finite search")
    value = ESeriesUtil.choose_preferred_number(Range(lower, upper), ESeriesUtil.SERIES[192], 0)
    return None if value is None else F(str(value))


def forward(nominal, reference, bottom, factors, leakage):
    # Independent forward equation; no inverse bounds or selector calculations.
    values = [v * (1 + nominal * factor / rb) + current * nominal * factor
              for v, rb, factor, current in product(*[
                  (F(i.minimum), F(i.maximum)) for i in (reference, bottom, factors, leakage)])]
    return min(values), max(values)


def display(value):
    if value is None:
        return None
    with localcontext() as ctx:
        ctx.prec = 18
        return format(Decimal(value.numerator) / Decimal(value.denominator), "f")


def evaluate(reference, bottom, factors, minimum, maximum, leakage, chooser=choose_edg):
    window = feedback_top_window(reference, bottom, factors, minimum, maximum, leakage)
    result = {"continuous_feasible": window.feasible,
              "nominal_ohm_exact": [str(window.minimum_ohm), None if window.maximum_ohm is None else str(window.maximum_ohm)],
              "nominal_ohm_display": [display(window.minimum_ohm), display(window.maximum_ohm)],
              "selected_nominal_ohm": None, "qualified": False}
    if not window.feasible:
        result.update(status="conditional_infeasible", reason=window.infeasible_reason)
        return result
    if window.minimum_ohm <= 0 or window.maximum_ohm is None:
        result.update(status="unsupported_search_domain")
        return result
    candidate = chooser(window)
    if candidate is None:
        # Not a proof that no discrete candidate exists, nor physical infeasibility.
        result.update(status="preferred_selector_found_no_candidate")
        return result
    if not isinstance(candidate, F) or candidate <= 0:
        raise ValueError("selector must return a strictly positive exact nominal")
    low, high = forward(candidate, reference, bottom, factors, leakage)
    if not window.minimum_ohm <= candidate <= window.maximum_ohm or not F(minimum) <= low <= high <= F(maximum):
        raise ValueError("selector candidate failed independent exact forward check")
    result.update(status="conditional_candidate", selected_nominal_ohm=display(candidate),
                  average_v_exact=[str(low), str(high)], average_v_display=[display(low), display(high)])
    return result


def run():
    start = time.monotonic()
    data = load_current()
    rail = data["rail"]
    d = lambda key: Decimal(str(rail[key]))
    ripple = d("ripple_pp_v") / 2
    raw_min = d("nominal_v") * Decimal(str(data["policy"]["raw_regulated_voltage_minimum_fraction_of_nominal"])) + ripple
    worst_case, worst_a = max(data["cases"], key=lambda row: row[1])
    worst_decimal = Decimal(worst_a.numerator) / Decimal(worst_a.denominator)
    full_min = max(raw_min, d("load_min_v") + ripple + worst_decimal * d("efuse_ron_max_ohm") + d("distribution_drop_v"))
    maximum = d("load_max_v") - ripple
    args = data["reference"], data["bottom"], data["factors"]
    leakage = Interval(0, 0)  # Deliberate exclusion, NOT an actual IC guarantee.
    full = evaluate(*args, full_min, maximum, leakage)
    partial = evaluate(*args, raw_min, maximum, leakage)
    if snapshot(data["paths"]) != data["before"]:
        raise ValueError("sources changed during synthesis")
    return {"schema_version": 1, "status": "not_qualified", "qualified": False,
            "scope": "conditional MAIN top-resistor nominal only; fixed bottom and current source model",
            "full_requirements": full, "raw_only_diagnostic_not_a_solution": partial,
            "required_average_v": [str(full_min), str(maximum)],
            "load_cases": len(data["cases"]), "limiting_case": worst_case, "limiting_current_a": display(worst_a),
            "selector": {"name": "EDG E192", "version": "0.5.2", "source_sha256": EDG_SELECTOR_SHA256},
            "limitations": ["zero leakage assumption; leakage and lifetime drift not qualified",
                            "VFB table VIN12 V does not qualify actual VIN6..8.4 V",
                            "ripple, eFuse hot RON and distribution are unqualified engineering budgets",
                            "current admission, startup, PG, dynamics, stability, thermal and routed behavior not qualified",
                            "H3 inputs regenerated in memory; their upstream engineering evidence is not requalified",
                            "no PCB or MPN adoption; exact part supply and physical prototype gates remain open"],
            "source_sha256": data["before"], "elapsed_s": round(time.monotonic() - start, 6),
            "model_decisions_inside_command": 0}


def main():
    try:
        result = run()
        (ROOT / "work").mkdir(exist_ok=True)
        folder = Path(tempfile.mkdtemp(prefix="feedback-synthesis-", dir=ROOT / "work"))
        path = folder / "result.json"
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"status": result["status"], "full": result["full_requirements"]["status"],
                          "report": str(path), "elapsed_s": result["elapsed_s"]}))
        return 1  # Expected: conditional analysis is not physical acceptance.
    except Exception as exc:
        print(json.dumps({"status": "execution_error", "error": str(exc), "report": None}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
