"""Necessary static monitor screen, coupled to a conditional rail envelope.

An ideal, arbitrary divider excludes leakage, tolerances and delay. Failure
rejects only this independent-corner model. Feasibility never qualifies a
monitor, its supply/logic path, transient response or a complete power cell.
"""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROWS_PATH = Path(__file__).with_name("h6-main-monitor-sources.json")
REVIEWED_SHA256 = "6c0f3097bbecf136f073b85842ebb999a15a0b571281f4da3f2e6b5f441dd6d7"


def load_reviewed_rows():
    if ROWS_PATH.is_symlink() or not ROWS_PATH.is_file():
        raise ValueError("missing or symlinked monitor transcription")
    raw = ROWS_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REVIEWED_SHA256:
        raise ValueError("monitor transcription changed; independent review required")
    return json.loads(raw)["rows"]


def screen(floor, ceiling, falling, rising):
    """Exact two-inequality check for one ideal divider's gain >=1.

    Separate falling/rising limits avoid mistaking the allowed 3.3-V ceiling
    for a voltage this loaded supply can actually reach at every corner.
    """
    if any(not isinstance(v, F) for v in (floor, ceiling, falling, rising)):
        raise ValueError("explicit exact Fraction voltage bounds required")
    if min(floor, falling) <= 0 or rising < falling:
        raise ValueError("invalid voltage/threshold bounds")
    # Nonpositive rail headroom is valid rejection evidence, not a malformed
    # report. Fixed resistive division cannot produce a gain below one.
    minimum_gain = max(F(1), floor / falling)
    maximum_gain = ceiling / rising
    return {"necessary_ideal_window_exists": minimum_gain <= maximum_gain,
            "minimum_gain_exact": str(minimum_gain),
            "maximum_gain_exact": str(maximum_gain),
            "lowest_worst_case_rising_v_exact": str(minimum_gain * rising),
            "rising_margin_v_exact": str(ceiling - minimum_gain * rising)}


def assess(*, floor, selected_local_min, optimistic_local_min_ceiling):
    rows = []
    for source in load_reviewed_rows():
        falling, rising = F(source["falling_min_v"]), F(source["rising_max_v"])
        row = {"id": source["id"], "qualified": False, "source": source,
               "selected_feedback_pair": None if selected_local_min is None else
               screen(floor, selected_local_min, falling, rising),
               "optimistic_continuous_feedback_ceiling": None if optimistic_local_min_ceiling is None else
               screen(floor, optimistic_local_min_ceiling, falling, rising)}
        rows.append(row)
    return {"qualified": False, "static_only": True,
            "derived_local_falling_floor_v_exact": str(floor),
            "selected_pair_local_min_v_exact": None if selected_local_min is None else str(selected_local_min),
            "optimistic_local_min_ceiling_v_exact": None if optimistic_local_min_ceiling is None else str(optimistic_local_min_ceiling),
            "rows": rows,
            "limitations": [
                "Independent source corners, ideal monitor resistors, zero input leakage and zero response time",
                "Selected-pair rejection is not rejection of every other feedback ratio",
                "Continuous ceiling excludes preferred-value and impedance restrictions; feasibility is not a constructed circuit",
                "Actual source conditions, monitor supply/logic, transient margin, complete-cell protection and production sourcing remain unqualified"]}
