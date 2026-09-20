"""Conditional two-resistor feedback synthesis using pinned EDG 0.5.2.

The existing EDG divider solver chooses both preferred nominal values. Its
floating-point result is only a proposal: exact independent circuit corners
must fit the supplied voltage and parallel-impedance requirements. Factors
are independent Cartesian multiplicative bounds, including caller-supplied
tolerance/drift. Only explicitly zero leakage is supported. No JVM, download,
MPN selection, board edit, or physical qualification is performed.
"""

from fractions import Fraction
import hashlib
from importlib import metadata
import inspect
from itertools import product
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hardware/verification"))
from h6_power_corner_math import Interval, _physical_interval

F = Fraction
EDG_VERSION = "0.5.2"
EDG_SOURCE_SHA256 = {
    "edg/abstract_parts/ESeriesUtil.py": "10b23014b3cdc803c833b9134d5ab64259bdac28641222c701d7796fd6190b05",
    "edg/circuits/ResistiveDivider.py": "c9ffc14fbe6546dc433f960f1f9122eef99a13b91683bd9b629a455eae0cc448",
    "edg/core/Range.py": "55a849aa25ea16ecdd66c4c16607a45ed2908e986b942be0e4e9fcc016e2a5dd",
}


def _bounds(interval, name):
    _physical_interval(interval, name)
    return F(interval.minimum), F(interval.maximum)


def verify_candidate(rtop, rbottom, reference, required_v, top_factors,
                     bottom_factors, impedance_ohm):
    """Reject any proposal outside the exact, zero-leakage circuit contract.

    This checker does not use EDG, its ratio calculation, or search tolerance.
    Voltage and parallel resistance extrema occur at the enumerated corners
    for positive resistors/reference. Nominals must already be exact Fractions.
    """
    if any(not isinstance(r, F) or r <= 0 for r in (rtop, rbottom)):
        raise ValueError("candidate nominals must be strictly positive exact Fractions")
    vref = _bounds(reference, "reference voltage")
    required = _bounds(required_v, "required voltage")
    top = _bounds(top_factors, "top factors")
    bottom = _bounds(bottom_factors, "bottom factors")
    impedance = _bounds(impedance_ohm, "parallel impedance")
    voltages = [v * (1 + rtop * ft / (rbottom * fb))
                for v, ft, fb in product(vref, top, bottom)]
    parallels = [(rtop * ft * rbottom * fb) / (rtop * ft + rbottom * fb)
                 for ft, fb in product(top, bottom)]
    vlow, vhigh = min(voltages), max(voltages)
    zlow, zhigh = min(parallels), max(parallels)
    if not (required[0] <= vlow <= vhigh <= required[1]
            and impedance[0] <= zlow <= zhigh <= impedance[1]):
        raise ValueError("candidate failed independent exact voltage/impedance check")
    return {"average_v_exact": [str(vlow), str(vhigh)],
            "parallel_impedance_ohm_exact": [str(zlow), str(zhigh)]}


def _load_edg():
    # Lazy loading keeps analytical infeasibility and exact checking available
    # without EDG. Pin all three numerical implementation files before import.
    distribution = metadata.distribution("edg")
    if distribution.version != EDG_VERSION:
        raise ValueError("unreviewed EDG version")
    for relative, digest in EDG_SOURCE_SHA256.items():
        source = Path(distribution.locate_file(relative))
        if (source.is_symlink() or not source.is_file()
                or hashlib.sha256(source.read_bytes()).hexdigest() != digest):
            raise ValueError(f"unreviewed EDG numerical source: {relative}")
    from edg.abstract_parts import ESeriesRatioUtil, ESeriesUtil, Range
    from edg.circuits.ResistiveDivider import DividerValues
    for cls, relative in ((ESeriesRatioUtil, "edg/abstract_parts/ESeriesUtil.py"),
                          (DividerValues, "edg/circuits/ResistiveDivider.py"),
                          (Range, "edg/core/Range.py")):
        if Path(inspect.getfile(cls)).resolve() != Path(distribution.locate_file(relative)).resolve():
            raise ValueError(f"imported EDG numerical source differs from pinned distribution: {relative}")
    return ESeriesRatioUtil, ESeriesUtil, Range, DividerValues


def _search_range(bounds, Range):
    # Search-only halo accommodates EDG's binary arithmetic at closed bounds.
    # It grants no acceptance margin: verify_candidate always uses exact inputs.
    try:
        low, high = float(bounds[0]) * (1 - 1e-12), float(bounds[1]) * (1 + 1e-12)
    except OverflowError as exc:
        raise ValueError("domain cannot be represented by finite EDG search") from exc
    if not 0 < low <= high < math.inf or not math.isfinite(low + high):
        raise ValueError("domain cannot be represented by finite EDG search")
    return Range(low, high)


def _find_pair(ratio, impedance, tolerance, series):
    ESeriesRatioUtil, ESeriesUtil, Range, DividerValues = _load_edg()
    # Round upward so conversion cannot make the common enclosure narrower.
    float_tolerance = float(tolerance)
    if F(float_tolerance) < tolerance:
        float_tolerance = math.nextafter(float_tolerance, math.inf)
    if float_tolerance >= 1:
        raise ValueError("unsupported EDG tolerance representation reaching one")
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[series], float_tolerance, DividerValues)
    try:
        values = calculator.find(DividerValues(_search_range(ratio, Range),
                                              _search_range(impedance, Range)))
    except ESeriesRatioUtil.NoMatchException:
        return None
    if (not isinstance(values, tuple) or len(values) != 2
            or any(isinstance(r, bool) or not isinstance(r, (int, float))
                   or not math.isfinite(r) or r <= 0 for r in values)):
        raise ValueError("EDG returned invalid nominal values")
    # EDG rounds its decimal preferred numbers; decimal strings recover those
    # nominal values exactly, without retaining binary floating-point artifacts.
    return tuple(F(str(r)) for r in values)


def synthesize_pair(reference: Interval, required_v: Interval,
                    top_factors: Interval, bottom_factors: Interval,
                    impedance_ohm: Interval, leakage_a: Interval, *, series=192) -> dict:
    """Choose both nominals for Vout = Vref * (1 + Rtop/Rbottom).

    A returned candidate is conditional and never qualified. No EDG match is
    not an infeasibility proof: its shared symmetric tolerance can over-enclose
    the original factors, and its search is limited. The only infeasibility
    shortcut here is an impossible ratio even before resistor uncertainty.
    """
    vref = _bounds(reference, "reference voltage")
    required = _bounds(required_v, "required voltage")
    top = _bounds(top_factors, "top factors")
    bottom = _bounds(bottom_factors, "bottom factors")
    impedance = _bounds(impedance_ohm, "parallel impedance")
    if not isinstance(leakage_a, Interval):
        raise ValueError("explicit leakage must be an Interval")
    if leakage_a.minimum != 0 or leakage_a.maximum != 0:
        raise NotImplementedError("nonzero leakage is unsupported by the EDG pair adapter")
    if isinstance(series, bool) or not isinstance(series, int) or series not in (3, 6, 12, 24, 48, 96, 192):
        raise ValueError("unsupported E-series")
    ratio = vref[1] / required[1], vref[0] / required[0]
    tolerance = max(abs(factor - 1) for factor in (*top, *bottom))
    result = {
        "qualified": False,
        "selected_nominal_ohm_exact": None,
        "required_ratio_exact": [str(value) for value in ratio],
        "common_symmetric_tolerance_fraction_exact": str(tolerance),
        "factor_enclosure": "shared symmetric enclosure of both supplied factor intervals; conservative",
        "selector": {"name": "EDG ESeriesRatioUtil + DividerValues", "version": EDG_VERSION,
                     "series": series, "source_sha256": dict(EDG_SOURCE_SHA256), "executed": False},
        "limitations": ["zero leakage assumption; no physical qualification or MPN adoption",
                        "no candidate is not proof of infeasibility or exhaustive optimization"],
    }
    if ratio[0] > ratio[1] or ratio[0] >= 1:
        return dict(result, status="conditional_infeasible",
                    reason="incompatible_reference_output_ratio_bounds")
    if tolerance >= 1:
        raise ValueError("unsupported factors: positive shared symmetric enclosure requires tolerance below one")
    values = _find_pair(ratio, impedance, tolerance, series)
    result["selector"]["executed"] = True
    if values is None:
        return dict(result, status="preferred_selector_found_no_candidate")
    rtop, rbottom = values
    checked = verify_candidate(rtop, rbottom, reference, required_v,
                               top_factors, bottom_factors, impedance_ohm)
    return dict(result, status="conditional_candidate",
                selected_nominal_ohm_exact={"top": str(rtop), "bottom": str(rbottom)}, **checked)
