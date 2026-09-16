"""Deterministic routing searches; no model decisions between candidates."""
import json


def sweep_profiles():
    return [{"id": f"grid{grid}-via{cost}-{order}", "grid_step": grid,
             "via_cost": cost, "ordering": order}
            for grid in (0.1, 0.05) for cost in (50, 75, 125)
            for order in ("mps", "inside_out")]


def adaptive_fallback(seed, runs):
    """A complete independently checked seed needs no parameter search.

    This optimizes orchestration, not geometric optimality: a full sweep may
    find a shorter candidate. Three fresh checked replays are still required
    by the recommended command; production/electrical gates do not change.
    """
    if any(row.get("geometry_pass") for row in runs):
        return []
    def key(profile):
        return json.dumps({k: v for k, v in profile.items() if k != "id"}, sort_keys=True)
    return [profile for profile in sweep_profiles() if key(profile) != key(seed)]
