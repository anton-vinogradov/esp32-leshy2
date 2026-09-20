"""Only the declared four-part, two-contact experimental delta is permitted."""

import copy
from contextlib import contextmanager, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from hardware.verification import h6_r2_c5_isolation_candidate as candidate


class C5IsolationCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = {key: candidate.crossings.load(candidate.ROOT / path) for key, path in candidate.crossings.INPUTS.items()}
        cls.reviews = candidate.crossings.semantics.reviewed_maps(
            [candidate.crossings.load(p) for p in candidate.crossings.semantics.MAPS], cls.baseline["material"]["groups"])

    def setUp(self):
        self.original = copy.deepcopy(self.baseline)
        self.overlay = candidate.make_candidate(self.original, self.reviews)

    def row(self, endpoint):
        return next(r for r in self.overlay["nets"]["rows"] if r["endpoint"] == endpoint)

    def check(self):
        return candidate.validate_delta(self.original, self.overlay, self.reviews)

    def test_real_build_is_repeatable_topology_only_and_unqualified(self):
        first, second = candidate.build(), candidate.build()
        self.assertEqual(first, second)
        self.assertEqual("not_qualified", first["status"])
        self.assertEqual("pass", first["mechanics_status"])
        self.assertEqual((12, 10), (first["baseline"]["potential_crossings"], first["candidate"]["potential_crossings"]))
        self.assertEqual((4, 14), (first["delta"]["added_components"], first["delta"]["added_endpoint_rows"]))
        self.assertEqual("not_selected_slew_and_output_leakage_unqualified", first["selection_status"])
        for field in ("qualified", "production_promoted", "fabrication_authorized", "native_candidate_generated"):
            self.assertIs(False, first[field])
        self.assertTrue(any("slew" in r for r in first["unresolved"]))
        self.assertTrue(any("leakage" in r and "discharge" in r for r in first["unresolved"]))
        self.assertIn("tools/route_board.py", first["source_sha256"])

    def test_copy_does_not_change_baseline_or_republish_native_metadata(self):
        self.check()
        self.assertEqual(self.baseline, self.original)
        for ledger in ("instances", "nets"):
            self.assertNotIn("sources", self.overlay[ledger])
            self.assertNotIn("summary", self.overlay[ledger])
            self.assertEqual("experimental_nonproduction_candidate", self.overlay[ledger]["status"])
            self.assertIsNot(self.original[ledger]["rows"], self.overlay[ledger]["rows"])

    def test_only_two_original_endpoint_nets_change(self):
        old = candidate.row_index(self.original["nets"]["rows"], "endpoint")
        new = candidate.row_index(self.overlay["nets"]["rows"], "endpoint")
        changed = [key for key, row in old.items() if row != new[key]]
        self.assertEqual({(candidate.PROJECT, name) for name in candidate.OUTPUTS}, set(changed))
        for key in changed:
            self.assertEqual({"net"}, {field for field in old[key] if old[key][field] != new[key][field]})

    def test_swapped_buffer_channels_are_rejected(self):
        a, b = self.row(candidate.BUFFER + ".1Y"), self.row(candidate.BUFFER + ".2Y")
        a["net"], b["net"] = b["net"], a["net"]
        with self.assertRaisesRegex(ValueError, "pad/net delta"):
            self.check()

    def test_swapped_c5_observations_are_rejected(self):
        a, b = self.row("c5.GPIO23"), self.row("c5.GPIO24")
        a["net"], b["net"] = b["net"], a["net"]
        with self.assertRaisesRegex(ValueError, "existing endpoint"):
            self.check()

    def test_lost_original_component_or_endpoint_is_rejected(self):
        for ledger in ("instances", "nets"):
            with self.subTest(ledger=ledger):
                self.overlay = candidate.make_candidate(self.original, self.reviews)
                self.overlay[ledger]["rows"].pop(0)
                with self.assertRaisesRegex(ValueError, "delta"):
                    self.check()

    def test_existing_u118_and_its_safety_wiring_are_untouched(self):
        report = self.check()
        self.assertTrue(report["original_u118_preserved"])
        old = [r for r in self.original["nets"]["rows"] if r["instance"] == "safe_fault_reset_buffer"]
        new = [r for r in self.overlay["nets"]["rows"] if r["instance"] == "safe_fault_reset_buffer"]
        self.assertEqual(old, new)
        new[0]["net"] = "STOLEN_SAFETY_CHANNEL"
        with self.assertRaisesRegex(ValueError, "existing endpoint"):
            self.check()

    def test_main_pullup_cannot_move_to_aon(self):
        self.row("exp_c5_rf_pullup.END_1")["net"] = "AON_SAFE_3V3"
        with self.assertRaisesRegex(ValueError, "pad/net delta"):
            self.check()

    def test_push_pull_substitution_is_rejected(self):
        reviews = copy.deepcopy(self.reviews)
        reviews["ti_sn74lvc3g07_dcur"]["pins"]["7"]["type"] = "output"
        with self.assertRaisesRegex(ValueError, "open-drain pin review"):
            candidate.validate_delta(self.original, self.overlay, reviews)
        row = next(r for r in self.overlay["instances"]["rows"] if r["instance"] == candidate.BUFFER)
        row["device_id"] = "ti_sn74lvc3g34_dcur"
        with self.assertRaisesRegex(ValueError, "exact metadata"):
            self.check()

    def test_unused_input_and_output_dispositions_are_enforced(self):
        for endpoint, net, disposition in (("3A", None, "no_connect"), ("3Y", "POWER_GROUND", "connected"),
                                           ("3A", "AON_SAFE_3V3", "connected")):
            with self.subTest(endpoint=endpoint, net=net):
                self.overlay = candidate.make_candidate(self.original, self.reviews)
                self.row(candidate.BUFFER + "." + endpoint).update(net=net, disposition=disposition)
                with self.assertRaisesRegex(ValueError, "pad/net delta"):
                    self.check()

    def test_wrong_pad_or_decoupling_rail_is_rejected(self):
        self.row(candidate.BUFFER + ".1A")["physical"] = "3"
        with self.assertRaisesRegex(ValueError, "pad/net delta"):
            self.check()
        self.overlay = candidate.make_candidate(self.original, self.reviews)
        self.row("exp_c5_iso_bypass.END_1")["net"] = "3V3_MAIN"
        with self.assertRaisesRegex(ValueError, "pad/net delta"):
            self.check()

    def test_original_aon_pullup_or_shared_net_cannot_change(self):
        for endpoint in ("c5_evidence_output_pullup.END_1", "m1_ui_plug.P42", "evidence_mask.P01"):
            with self.subTest(endpoint=endpoint):
                self.overlay = candidate.make_candidate(self.original, self.reviews)
                self.row(endpoint)["net"] = "UNREQUESTED_CHANGE"
                with self.assertRaisesRegex(ValueError, "existing endpoint"):
                    self.check()

    def test_experimental_names_references_and_nets_must_be_unique(self):
        for kind in ("instance", "reference", "net"):
            with self.subTest(kind=kind):
                data = copy.deepcopy(self.original)
                if kind == "net":
                    data["nets"]["rows"][0]["net"] = next(iter(candidate.OUTPUTS.values()))[1]
                else:
                    data["instances"]["rows"][0][kind] = candidate.BUFFER if kind == "instance" else candidate.PARTS[candidate.BUFFER][0]
                with self.assertRaisesRegex(ValueError, "collision"):
                    candidate.make_candidate(data, self.reviews)

    def test_added_duplicates_or_lost_new_component_are_rejected(self):
        for ledger in ("instances", "nets"):
            with self.subTest(ledger=ledger):
                self.overlay = candidate.make_candidate(self.original, self.reviews)
                self.overlay[ledger]["rows"].append(copy.deepcopy(self.overlay[ledger]["rows"][-1]))
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    self.check()
        self.overlay = candidate.make_candidate(self.original, self.reviews)
        self.overlay["instances"]["rows"].pop()
        with self.assertRaisesRegex(ValueError, "component delta"):
            self.check()

    def test_candidate_cannot_inherit_a_native_pass(self):
        self.overlay["nets"]["status"] = "pass"
        with self.assertRaisesRegex(ValueError, "native authority"):
            self.check()

    def test_stale_baseline_provenance_is_rejected(self):
        real_load = candidate.crossings.load
        def stale(path):
            data = real_load(path)
            if path == candidate.ROOT / candidate.crossings.INPUTS["nets"]:
                data["sources"]["instances"]["sha256"] = "0" * 64
            return data
        with patch.object(candidate.crossings, "load", side_effect=stale), self.assertRaisesRegex(ValueError, "stale"):
            candidate.build()

    def test_midrun_source_change_is_rejected(self):
        before = candidate.snapshot()
        with patch.object(candidate, "snapshot", side_effect=[before, {}]), self.assertRaisesRegex(ValueError, "changed during"):
            candidate.build()

    def test_mutating_baseline_during_copy_is_rejected(self):
        real_make = candidate.make_candidate
        def mutate(data, reviews):
            result = real_make(data, reviews)
            data["devices"]["unexpected"] = "mutation"
            return result
        with patch.object(candidate, "make_candidate", side_effect=mutate), self.assertRaises(ValueError):
            candidate.build()

    def test_cli_failure_never_returns_an_old_success_report(self):
        @contextmanager
        def awake(report, directory):
            yield Mock(poll=lambda: None)
        with tempfile.TemporaryDirectory() as directory, patch.object(candidate.tempfile, "mkdtemp", return_value=directory), \
                patch("tools.route_board.keep_awake", awake), patch.object(candidate, "build", side_effect=ValueError("stale")), \
                redirect_stdout(io.StringIO()) as output:
            previous = candidate.signal.getsignal(candidate.signal.SIGTERM)
            self.assertEqual(2, candidate.main())
            self.assertEqual(previous, candidate.signal.getsignal(candidate.signal.SIGTERM))
            self.assertIsNone(json.loads(output.getvalue())["report"])
            self.assertFalse((Path(directory) / "result.json").exists())

    def test_cli_success_publishes_only_unqualified_fresh_work_result(self):
        @contextmanager
        def awake(report, directory):
            report.update(established=True, status="active")
            yield Mock(poll=lambda: None)
            report["status"] = "released"
        report = {"status": "not_qualified", "mechanics_status": "pass", "qualified": False,
                  "baseline": {"potential_crossings": 12}, "candidate": {"potential_crossings": 10},
                  "source_sha256": {"input": "digest"}}
        with tempfile.TemporaryDirectory() as directory, patch.object(candidate.tempfile, "mkdtemp", return_value=directory), \
                patch("tools.route_board.keep_awake", awake), patch.object(candidate, "build", return_value=report), \
                patch.object(candidate, "snapshot", return_value={"input": "digest"}), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(1, candidate.main())
            summary = json.loads(output.getvalue())
            self.assertFalse(summary["qualified"])
            saved = json.loads((Path(directory) / "result.json").read_text())
            self.assertEqual({"input": "digest"}, saved["source_sha256"])
            self.assertEqual("released", saved["caffeinate"]["status"])
            self.assertTrue(saved["caffeinate"]["established"])

    def test_cli_rejects_caffeine_loss_or_late_source_drift(self):
        for power_status, hashes in ((1, {"input": "digest"}), (None, {"input": "changed"})):
            with self.subTest(power_status=power_status, hashes=hashes):
                @contextmanager
                def awake(report, directory):
                    yield Mock(poll=lambda: power_status)
                report = {"source_sha256": {"input": "digest"}}
                with tempfile.TemporaryDirectory() as directory, patch.object(candidate.tempfile, "mkdtemp", return_value=directory), \
                        patch("tools.route_board.keep_awake", awake), patch.object(candidate, "build", return_value=report), \
                        patch.object(candidate, "snapshot", return_value=hashes), redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(2, candidate.main())
                    self.assertIsNone(json.loads(output.getvalue())["report"])
                    self.assertFalse((Path(directory) / "result.json").exists())

    def test_cli_preserves_helper_portable_no_process_semantics(self):
        @contextmanager
        def unsupported(report, directory):
            report.update(status="unsupported_not_needed", established=False)
            yield None
        report = {"status": "not_qualified", "mechanics_status": "pass", "qualified": False,
                  "baseline": {"potential_crossings": 12}, "candidate": {"potential_crossings": 10}, "source_sha256": {}}
        with tempfile.TemporaryDirectory() as directory, patch.object(candidate.tempfile, "mkdtemp", return_value=directory), \
                patch("tools.route_board.keep_awake", unsupported), patch.object(candidate, "build", return_value=report), \
                patch.object(candidate, "snapshot", return_value={}), redirect_stdout(io.StringIO()):
            self.assertEqual(1, candidate.main())
            saved = json.loads((Path(directory) / "result.json").read_text())
            self.assertEqual("unsupported_not_needed", saved["caffeinate"]["status"])
            self.assertFalse(saved["caffeinate"]["established"])


if __name__ == "__main__":
    unittest.main()
