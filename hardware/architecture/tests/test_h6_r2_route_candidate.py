"""Small fail-closed checks for the read-only additive candidate grader."""
from collections import Counter
import hashlib
from pathlib import Path
import tempfile
import unittest

from hardware.layout import h6_r2_route_candidate as candidate


ROW = {"kicad_net": "A", "exact_ref_pads": ["J1.1", "J2.1"], "remaining_connections": 1}
BOARD = '(kicad_pcb (version 20260101) (footprint "f()" (uuid "fp")) '
TRACK = '(segment (start 0 0) (end 1 0) (width 0.15) (uuid "old"))'


class CandidateHelpersTests(unittest.TestCase):
    def test_parser_handles_nested_and_quoted_parentheses(self):
        self.assertEqual(["version", "footprint", "segment"],
                         [kind for kind, _ in candidate.forms(BOARD + TRACK + ")")])
        for text in (BOARD + TRACK, BOARD + TRACK + ") trailing", "x " + BOARD + ")",
                     "(kicad_pcb atom)", "(kicad_pcb ())"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                candidate.forms(text)

    def test_missing_and_duplicate_copper_uuids_rejected(self):
        for body in ('(segment (start 0 0))', TRACK + TRACK,
                     '(segment (uuid "a") (uuid "b"))'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                candidate.raw_copper(candidate.forms(BOARD + body + ")"))

    def test_preservation_checks_reject_edits_and_removal(self):
        original = BOARD + TRACK + ")"
        for changed, expected in (
            (original.replace("0.15", "0.16"), "original_copper_raw_changed_or_missing"),
            (BOARD + ")", "original_copper_raw_changed_or_missing"),
            (original.replace('"f()"', '"moved"'), "noncopper_raw_changed"),
            (original.replace('uuid "old"', 'uuid "fp"'), "global_duplicate_uuid"),
        ):
            failures = Counter()
            candidate._raw_checks(original, changed, failures)
            self.assertIn(expected, failures)
        failures = Counter()
        candidate._raw_checks(original, BOARD + TRACK + TRACK.replace('"old"', '"new"') + ")", failures)
        self.assertEqual({}, failures)

    def test_rows_have_no_hardcoded_batch_size(self):
        self.assertEqual({"A"}, candidate._validate_rows([ROW]))
        for rows in ([], [ROW, ROW], [dict(ROW, remaining_connections=True)],
                     [dict(ROW, remaining_connections=-1)], [dict(ROW, exact_ref_pads=[])],
                     [dict(ROW, kicad_net="")]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                candidate._validate_rows(rows)

    def test_all_net_regression_cannot_hide_behind_selected_progress(self):
        failures = Counter()
        result = candidate._connectivity_checks({"A": 1, "B": 0}, {"A": 0, "B": 1}, [ROW], failures)
        self.assertEqual({"B": [0, 1]}, result["all_net_regressions"])
        self.assertEqual(1, failures["all_net_connectivity_regressed"])
        self.assertTrue(result["selected_complete"])
        self.assertEqual([1, 0], result["selected_remaining"])

    def test_manifest_count_and_missing_net_fail(self):
        failures = Counter()
        candidate._connectivity_checks({"A": 2, "B": 0}, {"A": 1}, [ROW], failures)
        self.assertIn("allowlist_baseline_remaining", failures)
        self.assertIn("native_net_inventory_changed", failures)

    def test_geometry_signature_is_order_independent_and_geometry_sensitive(self):
        a = ("segment", "A", "F.Cu", 150000, (0, 0), (1000000, 0), ())
        b = ("via", "A", (1000000, 0), 400000, 200000, 3, "F.Cu", "B.Cu")
        self.assertEqual(candidate._geometry_signature([a, b]), candidate._geometry_signature([b, a]))
        self.assertNotEqual(candidate._geometry_signature([a]), candidate._geometry_signature([a, b]))

    def test_malformed_input_is_read_only_rejected_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline, output = Path(tmp) / "old.kicad_pcb", Path(tmp) / "new.kicad_pcb"
            baseline.write_text(BOARD + TRACK + ")")
            output.write_text("not a board")
            before = (baseline.read_bytes(), output.read_bytes())
            result = candidate.grade_candidate(baseline, output, [ROW], hashlib.sha256(before[0]).hexdigest())
            self.assertFalse(result["candidate_pass"])
            self.assertFalse(result["drc_checked"])
            self.assertFalse(result["electrically_qualified"])
            self.assertIn("input_or_native_error", result["failures"])
            self.assertEqual(before, (baseline.read_bytes(), output.read_bytes()))

    def test_native_minimal_board_progress_recipe_and_replay_signature(self):
        try:
            import pcbnew
        except ImportError:
            self.skipTest("KiCad Python needed for native board checks")
        with tempfile.TemporaryDirectory() as tmp:
            baseline, output = Path(tmp) / "old.kicad_pcb", Path(tmp) / "new.kicad_pcb"
            board = pcbnew.BOARD()
            net = pcbnew.NETINFO_ITEM(board, "A")
            board.Add(net)
            for reference, x in (("J1", 10), ("J2", 20)):
                fp = pcbnew.FOOTPRINT(board)
                fp.SetReference(reference)
                fp.SetPosition(pcbnew.VECTOR2I_MM(x, 10))
                board.Add(fp)
                pad = pcbnew.PAD(fp)
                pad.SetNumber("1")
                pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
                pad.SetSize(pcbnew.VECTOR2I_MM(1, 1))
                layers = pcbnew.LSET()
                layers.AddLayer(pcbnew.F_Cu)
                pad.SetLayerSet(layers)
                pad.SetPosition(fp.GetPosition())
                pad.SetNet(net)
                fp.Add(pad)
            pcbnew.SaveBoard(str(baseline), board)
            source = baseline.read_text()
            digest = hashlib.sha256(baseline.read_bytes()).hexdigest()
            segment = ('(segment (start 10 10) (end 20 10) (width 0.15) '
                       '(layer "F.Cu") (net "A") '
                       '(uuid "a81de09a-e855-492f-8d15-64cf441f2a7b"))')
            output.write_text(source[:source.rfind(")")] + segment + ")\n")
            accepted = candidate.grade_candidate(baseline, output, [ROW], digest)
            self.assertTrue(accepted["candidate_pass"], accepted)
            self.assertEqual("complete", accepted["routing_status"])
            self.assertEqual([1, 0], accepted["native_unconnected"])
            self.assertEqual(1, accepted["new_tracks"])
            self.assertEqual(10.0, accepted["new_trace_length_mm"])
            replay = output.read_text().replace("a81de09a-e855-492f-8d15-64cf441f2a7b",
                                                "88e6b797-2e20-4bc5-91c6-f74af9e8e8b2")
            replay = replay.replace("(start 10 10) (end 20 10)", "(start 20 10) (end 10 10)")
            output.write_text(replay)
            self.assertEqual(accepted["added_geometry_signature"],
                             candidate.grade_candidate(baseline, output, [ROW], digest)["added_geometry_signature"])
            output.write_text(replay.replace("(width 0.15)", "(width 0.16)"))
            self.assertIn("new_segment_recipe", candidate.grade_candidate(baseline, output, [ROW], digest)["failures"])
            self.assertIn("baseline_hash", candidate.grade_candidate(baseline, output, [ROW], "0" * 64)["failures"])
            output.write_text(source)
            rejected = candidate.grade_candidate(baseline, output, [ROW], digest)
            self.assertFalse(rejected["candidate_pass"])
            self.assertEqual("no_progress", rejected["routing_status"])
            self.assertEqual(source, baseline.read_text())


if __name__ == "__main__":
    unittest.main()
