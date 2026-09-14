#!/usr/bin/env python3
"""Boolean/order witness ONLY: not the installed C5 mux circuit or a timing model.

O = hardware service owner; R = requested SEL (0 USB, 1 SDIO);
A = connect enable (proposed meaning of ACK); L = release/Hub-hold request;
P = RUN_PERMIT; F = FAULT_ASSERT_N. O is an input, not a simulated latch.
HUB_HOLD = O | L | !R is realized with U17-derived !O and !L, NOT U18.Q_N.
Both latch outputs can be HIGH during simultaneous active preset and clear.
No production contracts, netlists, MPNs or generated artifacts are consumed.
"""

from __future__ import annotations

import itertools
import json
import math
from typing import NamedTuple


class Controls(NamedTuple):
    O: int
    R: int
    A: int
    L: int
    P: int
    F: int


class AssumedWait(NamedTuple):
    """A conditional premise supplied by a trace author, NOT measured evidence."""

    kind: str
    duration_ms: float | None = None


def boundary() -> dict:
    return {
        "status": "verification_candidate_not_implemented",
        "model": "zero_delay_boolean_and_ordered_events",
        "owner_complement": "U17 NOT(Q); U18.Q_N remains unused, never assumed equal to NOT(Q)",
        "production_topology_verified": False,
        "timing_qualified": False,
        "release_allowed": False,
        "open_conditions": [
            "Actual mux topology, voltage levels and AON-on/MAIN-off behavior are not bound.",
            "O preset/clear, VBUS qualification and asynchronous latch hazards are not modeled.",
            "Reset-sink assertions are logical commands, not measured reset-low or pad-high-Z.",
            "OE reconnects the mux and releases Q3/C5 reset together; relative delays are open.",
            "Assumed waits do not prove mux settling, strap timing, C5 readiness or recovery.",
            "Initial trace state is a premise; expander initialization and fault detection are external.",
        ],
    }


def evaluate(state: Controls) -> dict:
    if not isinstance(state, Controls) or any(
        type(value) not in (int, bool) or value not in (0, 1) for value in state
    ):
        raise ValueError("Controls require exactly six defined binary values")
    O, R, A, L, P, F = state
    valid = not (O and R)
    oe = not (A and valid and P and F)
    # Equivalent to O | L | !R, using two U17 NOT gates (!O and !L).
    # Do not substitute raw U18.Q_N: Q=Q_N=1 is possible with PRE_N=CLR_N=0.
    owner_not = not O
    hub_hold = not (owner_not and not L and R)
    return {
        "VALID": int(valid),
        "OE": int(oe),
        "HUB_HOLD": int(hub_hold),
        "SEL": R,
        "path": "disconnected" if oe else ("sdio" if R else "usb"),
        # Q3 remains driven by OE; existing KILL/fault C5 sinks are not removed.
        "C5_RESET_SINK": int(oe or not P or not F),
        # Existing Q2 KILL half remains; do not invent a direct F-to-Hub sink.
        "HUB_RESET_SINK": int(hub_hold or not P),
    }


def truth_table() -> list[dict]:
    return [
        {"inputs": state._asdict(), "outputs": evaluate(state)}
        for state in (Controls(*bits) for bits in itertools.product((0, 1), repeat=6))
    ]


def check_sequence(events: list[Controls | AssumedWait]) -> dict:
    """Reject bad ordering; accepted traces remain conditional, never HIL PASS.

    R changes need an earlier state with A=0, L=1 and an assumed reset/high-Z
    wait. Connection needs a subsequent assumed mux-settle wait. Hub release
    needs a separate assumed >=3 ms strap hold AND C5-ready premise. There is
    deliberately no invented 1 us reset-to-high-Z or mux settling guarantee.
    """
    if not events or not isinstance(events[0], Controls):
        raise ValueError("A trace must start with an explicit Controls state")
    state = events[0]
    out = evaluate(state)
    errors: list[str] = []
    assumptions: list[dict] = []
    quiescent = settled = c5_ready = False

    for index, event in enumerate(events[1:], 1):
        def reject(message: str) -> None:
            errors.append(f"step {index}: {message}")

        if isinstance(event, AssumedWait):
            if event.kind not in {"reset_and_pad_high_z", "mux_settle", "c5_strap_and_ready"}:
                raise ValueError("Unknown conditional wait")
            duration = event.duration_ms
            if duration is not None and (
                type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0
            ):
                raise ValueError("Conditional duration must be finite and nonnegative")
            assumptions.append({"step": index, **event._asdict(), "measured": False})
            if event.kind == "reset_and_pad_high_z":
                if state.A or not (out["OE"] and out["C5_RESET_SINK"] and out["HUB_RESET_SINK"]):
                    reject("reset/high-Z premise requires A=0 and both reset sinks asserted")
                else:
                    quiescent = True
            elif event.kind == "mux_settle":
                if state.A or not out["OE"] or not quiescent:
                    reject("mux-settle premise requires a preceding reset/high-Z premise while off")
                else:
                    settled = True
            elif (duration is None or duration < 3 or out["path"] != "sdio"
                  or out["C5_RESET_SINK"] or not out["HUB_RESET_SINK"]):
                reject("strap/ready premise requires >=3 ms after C5 release with SDIO on and Hub held")
            else:
                c5_ready = True
            continue

        new_out = evaluate(event)
        if event.R != state.R:
            if state.A or event.A:
                reject("A=0 must precede and remain through SEL change")
            if not state.L or not event.L:
                reject("L=1 must precede and remain through SEL change")
            if not quiescent:
                reject("SEL change lacks preceding conditional reset/high-Z wait")
            settled = c5_ready = False
        if state.O and not event.O:
            if not state.L or not event.L or state.A or event.A or not quiescent:
                reject("owner clear requires prior A=0, L=1 and conditional reset/high-Z wait")
            # VBUS-absent/physical clear qualification stays outside this six-input model.
        if out["OE"] and not new_out["OE"]:
            if state.A or not event.A:
                reject("reconnection requires an explicit A=0 to A=1 step, not automatic gate release")
            if not settled:
                reject("reconnection lacks a conditional mux-settle wait after the last SEL change")
            if new_out["path"] == "sdio" and not event.L:
                reject("SDIO reconnection requires L=1 to keep Hub held")
        if out["HUB_RESET_SINK"] and not new_out["HUB_RESET_SINK"]:
            if not c5_ready or new_out["path"] != "sdio" or new_out["C5_RESET_SINK"]:
                reject("early Hub release: conditional C5 strap/ready wait is missing or invalidated")
        if new_out["C5_RESET_SINK"]:
            c5_ready = False
        if not new_out["C5_RESET_SINK"] or not new_out["HUB_RESET_SINK"]:
            quiescent = False
        if not new_out["OE"]:
            settled = False
        state, out = event, new_out

    return {
        "status": "candidate_sequence_rejected" if errors else "conditional_sequence_consistent",
        "errors": errors,
        "conditional_waits": assumptions,
        "final_inputs": state._asdict(),
        "final_outputs": out,
        "boundary": boundary(),
    }


if __name__ == "__main__":
    print(json.dumps({"boundary": boundary(), "truth_table": truth_table()}, indent=2))
