"""Repair authority stays within selected new copper; no engine/DRC needed."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from hardware.layout.h6_r2_route_repair import derive_repair_plan, plan_from_evidence
from hardware.layout.h6_r2_route_candidate import forms


BOARD_KEY = "hardware/ecad/kicad/TEST/TEST.kicad_pcb"


def inputs():
    case = {"id": "test", "project": "TEST", "baseline_sha256": {BOARD_KEY: "a" * 64},
            "nets": [{"kicad_net": "A", "exact_ref_pads": ["J1.1", "J1.1", "J2.1", "J3.1"],
                      "remaining_connections": 2},
                     {"kicad_net": "B", "exact_ref_pads": ["J4.1", "J5.1"],
                      "remaining_connections": 1}]}
    summary = {"failed_single": ["A"], "open_single": [], "failed_multipoint": [],
               "pad_pairs_open": [{"net": "A"}], "blockers": [
                   {"net": "A", "blocked_by": [{"net": "B"}, {"net": "C"}]}]}
    evidence = {"baseline_sha256": "a" * 64, "candidate_sha256": "b" * 64,
                "preservation_recipe_pass": True,
                "original_copper_by_net": {"A": 0, "B": 0, "C": 1},
                "candidate_copper_by_net": {"A": 1, "B": 1, "C": 1},
                "remaining_by_net": {"A": 1, "B": 0, "C": 0}}
    return case, summary, evidence


class RepairPlannerTests(unittest.TestCase):
    def test_exact_new_only_authority_and_reproducibility(self):
        case, summary, evidence = inputs()
        before = deepcopy((case, summary, evidence))
        plan = plan_from_evidence(case, summary, evidence)
        self.assertEqual(["A"], plan["failed_nets"])
        self.assertEqual(["B"], plan["rip_existing_nets"])
        self.assertEqual(["--nets", "A", "--rip-existing-nets", "B"], plan["router_scope_arguments"])
        self.assertEqual([{"net": "C", "reason": "outside_reviewed_scope"}], plan["excluded_blockers"])
        self.assertEqual(1, plan["original_native_copper_objects"])
        self.assertFalse(plan["scope_widened"])
        self.assertFalse(plan["drc_checked"])
        self.assertEqual({"0"}, set(plan["required_environment"].values()))
        self.assertEqual(plan, plan_from_evidence(case, summary, evidence))
        self.assertEqual(plan, json.loads(json.dumps(plan)))
        self.assertEqual(before, (case, summary, evidence))

    def test_reports_native_opens_missing_from_engine_summary(self):
        case, summary, evidence = inputs()
        evidence["remaining_by_net"]["B"] = 1
        plan = plan_from_evidence(case, summary, evidence)
        self.assertEqual(["A", "B"], plan["failed_nets"])
        self.assertEqual(["B"], plan["unreported_native_open_nets"])

    def test_malformed_or_out_of_scope_failure_rejected(self):
        for failures in ([], ["C"], ["UNKNOWN"], ["*"], ["!A"], ["--nets"], [None], "A"):
            with self.subTest(failures=failures):
                case, summary, evidence = inputs()
                summary.update(failed_single=failures, pad_pairs_open=[])
                with self.assertRaises(ValueError):
                    plan_from_evidence(case, summary, evidence)
        for malformed in ({"failed_single": None}, {"blockers": None},
                          {"blockers": [None]}, {"blockers": [{"net": "A", "blocked_by": [None]}]},
                          {"blockers": [{"net": "B", "blocked_by": [{"net": "A"}]}]},
                          {"failed_multipoint": ["A"]}, {"pad_pairs_open": [{}]}):
            with self.subTest(malformed=malformed):
                case, summary, evidence = inputs()
                summary.update(malformed)
                with self.assertRaises(ValueError):
                    plan_from_evidence(case, summary, evidence)

    def test_no_original_copper_or_unknown_blocker_can_gain_authority(self):
        for name in ("UNKNOWN", "*", "B?"):
            with self.subTest(name=name):
                case, summary, evidence = inputs()
                summary["blockers"][0]["blocked_by"] = [{"net": name}]
                with self.assertRaises(ValueError):
                    plan_from_evidence(case, summary, evidence)
        for target in ("A", "B"):
            with self.subTest(original_copper=target):
                case, summary, evidence = inputs()
                evidence["original_copper_by_net"][target] = 1
                with self.assertRaises(ValueError):
                    plan_from_evidence(case, summary, evidence)
        case, summary, evidence = inputs()
        evidence["candidate_copper_by_net"]["B"] = 0
        with self.assertRaisesRegex(ValueError, "No eligible"):
            plan_from_evidence(case, summary, evidence)

    def test_invalid_native_proofs_and_stale_summary_rejected(self):
        changes = [("baseline_sha256", "c" * 64), ("candidate_sha256", "bad"),
                   ("preservation_recipe_pass", False), ("preservation_recipe_pass", 1),
                   ("original_copper_by_net", {"A": -1, "B": 0, "C": 1}),
                   ("candidate_copper_by_net", {"A": 1, "B": True, "C": 1}),
                   ("candidate_copper_by_net", {"A": 1, "B": 1, "C": 0}),
                   ("remaining_by_net", {"A": 1, "B": 0}),
                   ("remaining_by_net", {"A": 0, "B": 0, "C": 0})]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                case, summary, evidence = inputs()
                evidence[key] = value
                with self.assertRaises(ValueError):
                    plan_from_evidence(case, summary, evidence)

    def test_case_requires_exact_scope_and_expected_board_hash(self):
        for edit in (lambda c: c.update(project="../TEST"),
                     lambda c: c["baseline_sha256"].clear(),
                     lambda c: c["nets"].append(deepcopy(c["nets"][0])),
                     lambda c: c["nets"][0].update(kicad_net="A*"),
                     lambda c: c["nets"][0].update(project="OTHER")):
            case, summary, evidence = inputs()
            edit(case)
            with self.assertRaises(ValueError):
                plan_from_evidence(case, summary, evidence)

    def test_native_preservation_and_duplicate_pad_identity(self):
        try:
            import pcbnew
        except ImportError:
            self.skipTest("KiCad Python needed for native board checks")
        with tempfile.TemporaryDirectory() as directory:
            old, new = Path(directory) / "old.kicad_pcb", Path(directory) / "new.kicad_pcb"
            board = pcbnew.BOARD()
            nets = {}
            for name in ("A", "B", "C"):
                nets[name] = pcbnew.NETINFO_ITEM(board, name)
                board.Add(nets[name])
            for ref, x, y, name in (("J1", 10, 10, "A"), ("J2", 20, 10, "A"),
                                     ("J3", 30, 10, "A"), ("J4", 10, 20, "B"),
                                     ("J5", 20, 20, "B"), ("J6", 10, 30, "C"),
                                     ("J7", 20, 30, "C")):
                fp = pcbnew.FOOTPRINT(board)
                fp.SetReference(ref)
                fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
                board.Add(fp)
                for _ in range(2 if ref == "J1" else 1):
                    pad = pcbnew.PAD(fp)
                    pad.SetNumber("1")
                    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
                    pad.SetSize(pcbnew.VECTOR2I_MM(1, 1))
                    layers = pcbnew.LSET()
                    layers.AddLayer(pcbnew.F_Cu)
                    pad.SetLayerSet(layers)
                    pad.SetPosition(fp.GetPosition())
                    pad.SetNet(nets[name])
                    fp.Add(pad)
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pcbnew.VECTOR2I_MM(10, 30))
            track.SetEnd(pcbnew.VECTOR2I_MM(20, 30))
            track.SetWidth(150000)
            track.SetLayer(pcbnew.F_Cu)
            track.SetNet(nets["C"])
            board.Add(track)
            pcbnew.SaveBoard(str(old), board)
            source = old.read_text()
            def segment(name, y, suffix):
                return (f'(segment (start 10 {y}) (end 20 {y}) (width 0.15) '
                        f'(layer "F.Cu") (net "{name}") '
                        f'(uuid "a81de09a-e855-492f-8d15-64cf441f2a7{suffix}"))')
            routed = source[:source.rfind(")")] + segment("A", 10, "a") + segment("B", 20, "b") + ")\n"
            new.write_text(routed)
            case, summary, _ = inputs()
            case["baseline_sha256"][BOARD_KEY] = hashlib.sha256(old.read_bytes()).hexdigest()
            plan = derive_repair_plan(old, new, case, summary)
            self.assertEqual(["B"], plan["rip_existing_nets"])
            self.assertEqual(1, plan["original_native_copper_objects"])
            self.assertEqual(1, plan["selected_remaining_before_repair"])
            self.assertEqual(source, old.read_text())
            self.assertEqual(routed, new.read_text())
            # Original copper changes, footprint changes, and newly added
            # out-of-scope copper each fail independent native/raw checks.
            original_segment = next(block for kind, block in forms(source) if kind == "segment")
            for changed in (routed.replace("(width 0.15)", "(width 0.16)", 1),
                            routed.replace(original_segment, "", 1),
                            routed.replace("(at 10 10)", "(at 11 10)", 1),
                            routed[:routed.rfind(")")] + segment("C", 30, "c") + ")\n"):
                new.write_text(changed)
                with self.assertRaises(ValueError):
                    derive_repair_plan(old, new, case, summary)
                self.assertEqual(changed, new.read_text())
                self.assertEqual(source, old.read_text())
            new.write_text(routed)
            old.write_text(source + "\n")
            with self.assertRaisesRegex(ValueError, "reviewed baseline"):
                derive_repair_plan(old, new, case, summary)


if __name__ == "__main__":
    unittest.main()
