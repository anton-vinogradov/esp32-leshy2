import importlib.util
import itertools
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/c5_mux_control_candidate.py"
SPEC = importlib.util.spec_from_file_location("c5_mux_control_candidate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
C = MODULE.Controls
W = MODULE.AssumedWait


class C5MuxControlCandidateTest(unittest.TestCase):
    def assert_rejected(self, events, fragment):
        result = MODULE.check_sequence(events)
        self.assertEqual("candidate_sequence_rejected", result["status"])
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def assert_conditional(self, events, path):
        result = MODULE.check_sequence(events)
        self.assertEqual([], result["errors"])
        self.assertEqual("conditional_sequence_consistent", result["status"])
        self.assertEqual(path, result["final_outputs"]["path"])
        self.assertFalse(result["boundary"]["production_topology_verified"])
        self.assertFalse(result["boundary"]["timing_qualified"])
        self.assertFalse(result["boundary"]["release_allowed"])
        self.assertTrue(all(not row["measured"] for row in result["conditional_waits"]))
        return result

    def test_all_64_defined_states_against_independent_allowed_paths(self):
        table = MODULE.truth_table()
        self.assertEqual(64, len(table))
        self.assertEqual(64, len({tuple(row["inputs"].values()) for row in table}))
        # Literal (O,R,A) acceptance set, independently of the NAND implementation.
        allowed = {(0, 0, 1): "usb", (0, 1, 1): "sdio", (1, 0, 1): "usb"}
        for bits in itertools.product((0, 1), repeat=6):
            state = C(*bits)
            with self.subTest(state=state):
                out = MODULE.evaluate(state)
                expected = allowed.get((state.O, state.R, state.A), "disconnected")
                if not state.P or not state.F:
                    expected = "disconnected"
                self.assertEqual(expected, out["path"])
                self.assertEqual(int(expected == "disconnected"), out["OE"])
                self.assertEqual(state.R, out["SEL"])
                self.assertEqual(int((state.O, state.R) != (1, 1)), out["VALID"])
                self.assertEqual(int((state.O, state.L, state.R) != (0, 0, 1)), out["HUB_HOLD"])
                if not state.P or not state.F:
                    self.assertEqual((1, 1), (out["OE"], out["C5_RESET_SINK"]))
                if not state.P or not state.R:
                    self.assertEqual(1, out["HUB_RESET_SINK"])

    def test_old_owner_free_usb_counterexample_now_holds_hub(self):
        out = MODULE.evaluate(C(0, 0, 1, 0, 1, 1))
        self.assertEqual(("usb", 1), (out["path"], out["HUB_RESET_SINK"]))

    def test_invalid_latch_both_high_requires_inverted_q_not_raw_q_n(self):
        # Static forbidden PRE_N=CLR_N=0 case only; no propagation-time proof.
        q, raw_q_n, release, request = 1, 1, 0, 1
        old_direct_q_n_hold = int(not (raw_q_n and not release and request))
        corrected = MODULE.evaluate(C(q, request, 1, release, 1, 1))
        self.assertEqual(0, old_direct_q_n_hold)
        self.assertEqual((1, 1), (corrected["HUB_HOLD"], corrected["HUB_RESET_SINK"]))
        self.assertEqual(1, corrected["OE"])
        self.assertIn("U18.Q_N remains unused", MODULE.boundary()["owner_complement"])

    def test_hot_insert_with_ack_high_disconnects_without_changing_sel(self):
        runtime = C(0, 1, 1, 0, 1, 1)
        seized = runtime._replace(O=1)
        self.assertEqual("sdio", MODULE.evaluate(runtime)["path"])
        out = MODULE.evaluate(seized)
        self.assertEqual((1, 1, 1, 1),
                         (out["SEL"], out["OE"], out["C5_RESET_SINK"], out["HUB_RESET_SINK"]))
        off = seized._replace(A=0, L=1)
        usb = off._replace(R=0)
        self.assert_conditional([
            runtime, seized, off, W("reset_and_pad_high_z"), usb,
            W("mux_settle"), usb._replace(A=1),
        ], "usb")

    def return_to_runtime(self):
        service = C(1, 0, 1, 0, 1, 1)
        off = service._replace(A=0, L=1)
        selected = off._replace(R=1)
        cleared = selected._replace(O=0)
        connected = cleared._replace(A=1)
        return [service, off, W("reset_and_pad_high_z"), selected, cleared,
                W("mux_settle"), connected, W("c5_strap_and_ready", 3), connected._replace(L=0)]

    def test_owner_clear_does_not_release_hub_before_c5_strap_hold(self):
        events = self.return_to_runtime()
        self.assertEqual(1, MODULE.evaluate(events[4])["HUB_RESET_SINK"])
        self.assertEqual(1, MODULE.evaluate(events[6])["HUB_RESET_SINK"])
        result = self.assert_conditional(events, "sdio")
        self.assertEqual(0, result["final_outputs"]["HUB_RESET_SINK"])

    def test_uninitialized_expander_pulldowns_are_logically_off_not_initialized_proof(self):
        for owner in (0, 1):
            for permit, fault in itertools.product((0, 1), repeat=2):
                out = MODULE.evaluate(C(owner, 0, 0, 0, permit, fault))
                self.assertEqual((1, 1, 1),
                                 (out["OE"], out["C5_RESET_SINK"], out["HUB_RESET_SINK"]))

    def test_sel_change_with_ack_high_is_rejected_even_if_owner_veto_disconnects(self):
        for owner in (0, 1):
            before = C(owner, 1, 1, 1, 1, 1)
            self.assert_rejected([before, before._replace(R=0)], "A=0 must precede")

    def test_simultaneous_disable_hold_and_select_is_not_ordered(self):
        before = C(0, 1, 1, 0, 1, 1)
        self.assert_rejected([before, before._replace(A=0, L=1, R=0)], "A=0 must precede")
        self.assert_rejected([before, before._replace(A=0, L=1, R=0)], "L=1 must precede")

    def test_hold_must_precede_select_even_when_mux_already_off(self):
        before = C(1, 1, 0, 0, 1, 1)
        self.assert_rejected([before, W("reset_and_pad_high_z"), before._replace(R=0, L=1)],
                             "L=1 must precede")

    def test_missing_reset_and_settle_waits_fail_closed(self):
        before = C(1, 1, 0, 1, 1, 1)
        selected = before._replace(R=0)
        self.assert_rejected([before, selected], "SEL change lacks preceding")
        self.assert_rejected([before, W("reset_and_pad_high_z"), selected, selected._replace(A=1)],
                             "reconnection lacks a conditional mux-settle wait")

    def test_a_settle_wait_before_select_cannot_be_reused_after_select(self):
        before = C(1, 1, 0, 1, 1, 1)
        selected = before._replace(R=0)
        self.assert_rejected([before, W("reset_and_pad_high_z"), W("mux_settle"),
                              selected, selected._replace(A=1)], "reconnection lacks")

    def test_early_hub_release_and_short_or_premature_strap_wait_are_rejected(self):
        events = self.return_to_runtime()
        self.assert_rejected(events[:7] + events[8:], "early Hub release")
        self.assert_rejected(events[:7] + [W("c5_strap_and_ready", 2.999)] + events[8:],
                             "strap/ready premise requires >=3 ms")
        self.assert_rejected(events[:6] + [W("c5_strap_and_ready", 3)] + events[6:7] + events[8:],
                             "strap/ready premise requires >=3 ms")

    def test_reset_invalidates_prior_ready_wait(self):
        events = self.return_to_runtime()[:8]
        connected = events[6]
        self.assert_rejected(events + [connected._replace(A=0), connected._replace(A=0, L=0)],
                             "early Hub release")

    def test_owner_clear_without_prior_hold_or_with_ack_high_is_rejected(self):
        for state in (C(1, 1, 0, 0, 1, 1), C(1, 1, 1, 1, 1, 1)):
            self.assert_rejected([state, state._replace(O=0)], "owner clear requires")

    def test_fault_or_kill_clearing_with_stale_ack_is_not_an_authorized_reconnect_step(self):
        for field in ("P", "F"):
            initial = C(0, 1, 1, 1, 1, 1)._replace(**{field: 0})
            self.assert_rejected([initial, initial._replace(**{field: 1})],
                                 "not automatic gate release")

    def test_unknown_states_and_malformed_conditional_waits_are_not_safe_defaults(self):
        for value in (None, 2, -1, "0", 0.0):
            with self.assertRaises(ValueError):
                MODULE.evaluate(C(0, 0, value, 0, 1, 1))
        for wait in (W("measured_high_z"), W("mux_settle", float("nan")), W("mux_settle", -1)):
            with self.assertRaises(ValueError):
                MODULE.check_sequence([C(0, 0, 0, 1, 1, 1), wait])
        with self.assertRaises(ValueError):
            MODULE.check_sequence([])


if __name__ == "__main__":
    unittest.main()
