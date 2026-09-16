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
        return json.dumps({k: v for k, v in profile.items() if k not in ("id", "net_order")}, sort_keys=True)
    return [profile for profile in sweep_profiles() if key(profile) != key(seed)]


def portfolio_profiles():
    """Bounded cold-rebuild alternatives, never looser widths/clearances.

    Search direction and failed-net-first ordering attack endpoint congestion;
    finer grid attacks discretization. Replays freeze the effective net order.
    """
    seed = dict(grid_step=0.05, via_cost=75, ordering="mps")
    return [dict(seed, id="known-fine75"),
            dict(seed, id="reverse-search", direction="backward"),
            dict(seed, id="hard-nets-first", ordering="original", net_order_strategy="failed_first"),
            dict(seed, id="hard-nets-first-backward", ordering="original",
                 direction="backward", net_order_strategy="failed_first"),
            dict(seed, id="inside-out-backward", ordering="inside_out", direction="backward"),
            dict(seed, id="lower-heuristic", heuristic_weight=1.3),
            dict(seed, id="finer-grid", grid_step=0.025),
            dict(seed, id="finer-grid-backward", grid_step=0.025, direction="backward")]


def freeze_net_order(profile, rows, runs):
    names = [row["kicad_net"] for row in rows]
    profile = dict(profile)
    if "net_order" not in profile:
        if profile.get("net_order_strategy") == "failed_first" and runs:
            best = max(runs, key=lambda row: row.get("validation", {}).get("resolved_connections", -1))
            remaining = best.get("validation", {}).get("per_net", {})
            names = sorted(names, key=lambda name: -remaining.get(name, [0, 0])[1])
        profile["net_order"] = names
    if len(profile["net_order"]) != len(names) or set(profile["net_order"]) != set(names):
        raise ValueError("Profile net order must be an exact permutation of the reviewed scope")
    return profile
