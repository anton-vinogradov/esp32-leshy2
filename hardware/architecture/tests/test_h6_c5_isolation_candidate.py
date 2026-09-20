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
        self.assertFalse(first["source_screen"]["qualified"])
        self.assertEqual(10, len(first["source_reviewed_crossing_scan"]["crossings"]))

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
        for variant in candidate.VARIANTS:
            with self.subTest(variant=variant), patch.object(candidate.crossings, "load", side_effect=stale), self.assertRaisesRegex(ValueError, "stale"):
                candidate.build(variant)

    def test_midrun_source_change_is_rejected(self):
        before = candidate.snapshot()
        for variant in candidate.VARIANTS:
            with self.subTest(variant=variant), patch.object(candidate, "snapshot", side_effect=[before, {}]), self.assertRaisesRegex(ValueError, "changed during"):
                candidate.build(variant)

    def test_mutating_baseline_during_copy_is_rejected(self):
        real_make = candidate.make_candidate
        def mutate(data, reviews, variant="aon_open_drain"):
            result = real_make(data, reviews, variant)
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
            self.assertEqual(2, candidate.main([]))
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
            self.assertEqual(1, candidate.main([]))
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
                    self.assertEqual(2, candidate.main([]))
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
            self.assertEqual(1, candidate.main([]))
            saved = json.loads((Path(directory) / "result.json").read_text())
            self.assertEqual("unsupported_not_needed", saved["caffeinate"]["status"])
            self.assertFalse(saved["caffeinate"]["established"])


class C5MainSchmittCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        C5IsolationCandidateTests.setUpClass.__func__(cls)
        cls.state = candidate.crossings.state_snapshot()

    def setUp(self):
        self.original = copy.deepcopy(self.baseline)
        self.overlay = candidate.make_candidate(self.original, self.reviews, "main_schmitt")

    row = C5IsolationCandidateTests.row

    def check(self):
        return candidate.validate_delta(self.original, self.overlay, self.reviews, "main_schmitt")

    def scans(self):
        return tuple(candidate.crossings.evaluate(data, self.reviews, self.state) for data in (self.original, self.overlay))

    def test_real_schmitt_build_exact_bom_replay_and_no_qualification_ranking(self):
        report = candidate.build("main_schmitt")
        self.assertEqual(report, candidate.build("main_schmitt"))
        self.assertEqual("main_schmitt", report["variant"])
        self.assertEqual("unqualified_pending_levels_leakage_power_sequences", report["selection_status"])
        self.assertEqual((12, 12), (report["baseline"]["potential_crossings"], report["candidate"]["potential_crossings"]))
        self.assertEqual((1214, 791), (report["candidate"]["scanned_instances"], report["candidate"]["scanned_nets"]))
        self.assertEqual((4, 14), (report["delta"]["added_components"], report["delta"]["added_endpoint_rows"]))
        self.assertEqual({"SN74LVC1G17DCKR": 2, "Yageo CC0402KRX7R9BB104": 2}, report["delta"]["added_bom"])
        self.assertIn("neither an electrical ranking", report["crossing_count_interpretation"])
        for field in ("qualified", "production_promoted", "fabrication_authorized", "native_candidate_generated"):
            self.assertIs(False, report[field])
        self.assertTrue(any("source evidence only" in row for row in report["unresolved"]))

    def test_exact_old_and_new_rows_preserved(self):
        C5IsolationCandidateTests.test_only_two_original_endpoint_nets_change(self)
        self.check()
        self.assertEqual(self.baseline, self.original)
        for instance in ("safe_rearm_buffer", "safe_fault_reset_buffer"):
            for ledger in ("instances", "nets"):
                self.assertEqual([r for r in self.original[ledger]["rows"] if r["instance"] == instance],
                                 [r for r in self.overlay[ledger]["rows"] if r["instance"] == instance])
        for name in ("exp_c5_rf_schmitt", "exp_c5_ir_schmitt"):
            self.assertEqual(("1", None, "no_connect"), tuple(self.row(name + ".NC")[k] for k in ("physical", "net", "disposition")))
            self.assertEqual(("5", "3V3_MAIN"), tuple(self.row(name + ".VCC")[k] for k in ("physical", "net")))

    def test_channels_c5_observations_and_pad_swaps_reject(self):
        for suffix in ("A", "Y", "GPIO"):
            with self.subTest(suffix=suffix):
                self.overlay = candidate.make_candidate(self.original, self.reviews, "main_schmitt")
                names = ("c5.GPIO23", "c5.GPIO24") if suffix == "GPIO" else ("exp_c5_rf_schmitt." + suffix, "exp_c5_ir_schmitt." + suffix)
                a, b = [self.row(name) for name in names]
                a["net"], b["net"] = b["net"], a["net"]
                with self.assertRaises(ValueError):
                    self.check()
        self.overlay = candidate.make_candidate(self.original, self.reviews, "main_schmitt")
        self.row("exp_c5_rf_schmitt.A")["physical"] = "1"
        with self.assertRaisesRegex(ValueError, "pad/net delta"):
            self.check()

    def test_nc_main_supplies_and_bypass_rails_are_enforced(self):
        mutations = [("exp_c5_rf_schmitt.NC", {"net": "POWER_GROUND", "disposition": "connected"}),
                     ("exp_c5_rf_schmitt.A", {"net": None, "disposition": "no_connect"}),
                     ("exp_c5_rf_schmitt.VCC", {"net": "AON_SAFE_3V3"}),
                     ("exp_c5_ir_schmitt.GND", {"net": "3V3_MAIN"}),
                     ("exp_c5_rf_bypass.END_1", {"net": "AON_SAFE_3V3"}),
                     ("exp_c5_ir_bypass.END_2", {"net": "3V3_MAIN"})]
        for endpoint, update in mutations:
            with self.subTest(endpoint=endpoint):
                self.overlay = candidate.make_candidate(self.original, self.reviews, "main_schmitt")
                self.row(endpoint).update(update)
                with self.assertRaisesRegex(ValueError, "pad/net delta"):
                    self.check()

    def test_schmitt_exact_pin_function_and_part_identity_required(self):
        reviews = copy.deepcopy(self.reviews)
        reviews["ti_sn74lvc1g17_dckr"]["pins"]["4"]["type"] = "open_collector"
        with self.assertRaisesRegex(ValueError, "Schmitt pin review"):
            candidate.validate_delta(self.original, self.overlay, reviews, "main_schmitt")
        data = copy.deepcopy(self.original)
        data["devices"]["devices"]["ti_sn74lvc1g17_dckr"]["electrical_contract"]["function"] = "inverting Schmitt"
        with self.assertRaisesRegex(ValueError, "polarity/function"):
            candidate.make_candidate(data, self.reviews, "main_schmitt")
        next(r for r in self.overlay["instances"]["rows"] if r["instance"] == "exp_c5_rf_schmitt")["mpn"] = "SN74LVC1G07DCKR"
        with self.assertRaisesRegex(ValueError, "exact metadata"):
            self.check()

    def test_existing_loss_extra_or_duplicate_rows_reject(self):
        for ledger in ("instances", "nets"):
            for mutation in ("delete", "duplicate", "extra"):
                with self.subTest(ledger=ledger, mutation=mutation):
                    self.overlay = candidate.make_candidate(self.original, self.reviews, "main_schmitt")
                    rows = self.overlay[ledger]["rows"]
                    if mutation == "delete":
                        rows.pop(0)
                    else:
                        row = copy.deepcopy(rows[-1])
                        if mutation == "extra":
                            row["instance" if ledger == "instances" else "endpoint"] += "_extra"
                        rows.append(row)
                    with self.assertRaises(ValueError):
                        self.check()

    def test_schmitt_collisions_and_cross_variant_validation_reject(self):
        for kind in ("instance", "reference", "net"):
            with self.subTest(kind=kind):
                data = copy.deepcopy(self.original)
                if kind == "net":
                    data["nets"]["rows"][0]["net"] = "EXP_C5_RF_TX_EVIDENCE_N"
                else:
                    data["instances"]["rows"][0][kind] = "exp_c5_rf_schmitt" if kind == "instance" else "EXP_U_C5_RF"
                with self.assertRaisesRegex(ValueError, "collision"):
                    candidate.make_candidate(data, self.reviews, "main_schmitt")
        with self.assertRaises(ValueError):
            candidate.validate_delta(self.original, self.overlay, self.reviews)
        for value in ("unknown", None, False):
            with self.subTest(variant=value), self.assertRaisesRegex(ValueError, "variant"):
                candidate.build(value)

    def test_crossing_delta_exactly_replaces_only_c5_receivers(self):
        baseline, scan = self.scans()
        candidate.validate_scan_delta(baseline, scan, "main_schmitt")
        for old_contact, new_instance, net in (("GPIO23", "exp_c5_rf_schmitt", "EV_N1_C5"), ("GPIO24", "exp_c5_ir_schmitt", "EV_N7_IR")):
            old = next(row for row in baseline["crossings"] if row["receiver"]["instance"] == "c5" and row["receiver"]["contact"] == old_contact)
            new = next(row for row in scan["crossings"] if row["receiver"]["instance"] == new_instance)
            self.assertEqual((net, "M1", "A", ["2"]), (new["net"], new["net_scope"], new["receiver"]["contact"], new["receiver"]["pads"]))
            self.assertEqual(old["sources"], new["sources"])
            self.assertEqual(["VCC"], new["receiver_supply"]["contacts"])
            self.assertEqual("missing_off_state_tolerance", new["finding_kind"])
            self.assertEqual([], new["input_tolerance_evidence"])
        self.assertEqual(baseline["unknown_supply_ownership"], scan["unknown_supply_ownership"])
        self.assertEqual(baseline["unreviewed_connected_pins"], scan["unreviewed_connected_pins"][:-4])
        self.assertEqual({"exp_c5_rf_bypass", "exp_c5_ir_bypass"},
                         {row["instance"] for row in scan["unreviewed_connected_pins"][-4:]})

    def test_scan_omission_extra_receiver_source_and_same_count_corruption_reject(self):
        baseline, scan = self.scans()
        for mutation in ("omit", "duplicate", "replace", "source", "supply", "unknown", "unreviewed", "count", "proof"):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(scan)
                row = next(r for r in changed["crossings"] if r["receiver"]["instance"] == "exp_c5_rf_schmitt")
                if mutation == "omit":
                    changed["crossings"].remove(row)
                elif mutation == "duplicate":
                    changed["crossings"].append(copy.deepcopy(row))
                elif mutation == "replace":
                    row["receiver"]["instance"] = "unexpected_receiver"
                elif mutation == "source":
                    row["sources"][0]["pin"]["net"] = "EV_N7_IR"
                elif mutation == "supply":
                    row["receiver_supply"]["contacts"] = ["3V3"]
                elif mutation == "proof":
                    row.update(finding_kind="off_state_input_evidence_requires_voltage_review", input_tolerance_evidence=[{}])
                elif mutation == "count":
                    changed["scanned_instances"] -= 1
                else:
                    changed["unknown_supply_ownership" if mutation == "unknown" else "unreviewed_connected_pins"].pop()
                with self.assertRaises(ValueError):
                    candidate.validate_scan_delta(baseline, changed, "main_schmitt")

    def test_source_review_is_separate_exact_evidence_not_raw_graph_clearance(self):
        report = candidate.build("main_schmitt")
        for path in candidate.interface.source_paths():
            self.assertIn(str(path.relative_to(candidate.ROOT)), report["source_sha256"])
        raw = self.scans()[1]
        reviewed = report["source_reviewed_crossing_scan"]
        proofs = candidate.interface.off_input_proofs("main_schmitt")
        candidate.validate_reviewed_scan(raw, reviewed, "main_schmitt", proofs)
        self.assertEqual(12, report["candidate"]["potential_crossings"])
        changed = [row for row in reviewed["crossings"] if row["input_tolerance_evidence"]]
        self.assertEqual({"exp_c5_rf_schmitt", "exp_c5_ir_schmitt"}, {row["receiver"]["instance"] for row in changed})
        for row in changed:
            self.assertEqual("off_state_input_evidence_requires_voltage_review", row["finding_kind"])
            self.assertEqual([proofs[0]], row["input_tolerance_evidence"])
            self.assertFalse(row["pin_voltage_bounded"])
            self.assertFalse(row["qualified"])
        self.assertFalse(report["source_screen"]["qualified"])
        self.assertFalse(reviewed["qualified"])
        self.assertFalse(reviewed["gate_closed"])

    def test_source_review_may_not_change_other_findings_sources_or_authority(self):
        raw = self.scans()[1]
        proofs = candidate.interface.off_input_proofs("main_schmitt")
        reviewed = candidate.crossings.evaluate(self.overlay, self.reviews, self.state, proofs, candidate.snapshot())
        for mutation in ("proof", "source", "extra_evidence", "receiver", "unknown", "unreviewed", "status", "qualified"):
            with self.subTest(mutation=mutation):
                altered = copy.deepcopy(reviewed)
                row = next(r for r in altered["crossings"] if r["receiver"]["instance"] == "exp_c5_rf_schmitt")
                if mutation == "proof":
                    row["input_tolerance_evidence"] = []
                elif mutation == "source":
                    row["sources"][0]["pin"]["net"] = "EV_N7_IR"
                elif mutation == "extra_evidence":
                    altered["crossings"][0]["input_tolerance_evidence"] = [proofs[0]]
                elif mutation == "receiver":
                    row["receiver"]["pads"] = ["1"]
                elif mutation in ("unknown", "unreviewed"):
                    altered["unknown_supply_ownership" if mutation == "unknown" else "unreviewed_connected_pins"].pop()
                elif mutation == "status":
                    row["status"] = "pass"
                else:
                    altered["qualified"] = True
                with self.assertRaises(ValueError):
                    candidate.validate_reviewed_scan(raw, altered, "main_schmitt", proofs)
        with self.assertRaisesRegex(ValueError, "evidence"):
            candidate.validate_reviewed_scan(raw, reviewed, "aon_open_drain", proofs)

    def test_source_transcription_tamper_is_rejected_by_both_variants(self):
        for variant in candidate.VARIANTS:
            with self.subTest(variant=variant), patch.object(candidate.interface, "REVIEWED_SHA256", "0" * 64), \
                    self.assertRaisesRegex(ValueError, "transcription changed"):
                candidate.build(variant)

    def test_source_screen_cannot_promote_qualification(self):
        with patch.object(candidate.interface, "review_candidate", return_value={"qualified": True}), \
                self.assertRaisesRegex(ValueError, "cannot qualify"):
            candidate.build("main_schmitt")

    def test_cli_dispatches_schmitt_and_rejects_unknown_variant(self):
        @contextmanager
        def awake(report, directory):
            report.update(status="unsupported_not_needed", established=False)
            yield None
        report = {"variant": "main_schmitt", "status": "not_qualified", "mechanics_status": "pass", "qualified": False,
                  "baseline": {"potential_crossings": 12}, "candidate": {"potential_crossings": 12}, "source_sha256": {}}
        with tempfile.TemporaryDirectory() as directory, patch.object(candidate.tempfile, "mkdtemp", return_value=directory), \
                patch("tools.route_board.keep_awake", awake), patch.object(candidate, "build", return_value=report) as build, \
                patch.object(candidate, "snapshot", return_value={}), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(1, candidate.main(["--variant", "main_schmitt"]))
            build.assert_called_once_with("main_schmitt")
            self.assertEqual("main_schmitt", json.loads(output.getvalue())["variant"])
            self.assertEqual("main_schmitt", json.loads((Path(directory) / "result.json").read_text())["variant"])
        with patch.object(candidate, "build") as build, patch("sys.stderr", new=io.StringIO()), self.assertRaises(SystemExit) as raised:
            candidate.main(["--variant", "unknown"])
        self.assertEqual(2, raised.exception.code)
        build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
