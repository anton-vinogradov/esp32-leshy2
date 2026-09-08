"""Left-side ergonomic datum and real bypass owners, without PCB writes.

The joint native stage/DRC remains separate: R286's new site requires the
coordinated inner-audio repack. A nominal plan gap is not finger/3D approval.
"""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
REVIEW = ROOT / "hardware/layout/h6-r2-encoder-left-candidate.json"
PROJECT = "LESHY2-RF-R2"
PCB = ROOT / f"hardware/ecad/kicad/{PROJECT}/{PROJECT}.kicad_pcb"
EXPECTED_REFS = {
    "SW3", "U111", "U94", "U30", "U109", "U31", "C125", "C244",
    "C245", "C266", "C264", "C114", "U47", "C142", "C33", "C34",
    "C35", "C36", "R224", "R284", "R283", "R271", "C258", "R286",
}
U6_CAPS = {
    "hub_safe_i2c_aon_100n": ("C33", "8", "AON_SAFE_3V3"),
    "hub_safe_i2c_aon_1u": ("C34", "8", "AON_SAFE_3V3"),
    "hub_safe_i2c_main_100n": ("C35", "1", "3V3_MAIN"),
    "hub_safe_i2c_main_1u": ("C36", "1", "3V3_MAIN"),
}
try:
    import pcbnew
    import h6_r2_placement as placement
except ImportError:
    pcbnew = None


class EncoderLeftSourceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text())
        self.review = json.loads(REVIEW.read_text())

    def test_finite_scope_uses_real_left_native_datum_and_keeps_supports_inner(self):
        rows = self.review["placement_rows"]
        self.assertEqual(EXPECTED_REFS, {r["reference"] for r in rows})
        self.assertEqual(len(EXPECTED_REFS), len(rows))
        overrides = self.contract["placement_overrides"]
        for row in rows:
            got = overrides[row["instance"]]
            expected = row["after"]
            self.assertEqual(expected["anchor_mm"], got["anchor_mm"], row["reference"])
            self.assertEqual(expected["rotation_deg"] % 360, got["rotation_deg"] % 360)
            self.assertTrue(got["mechanical_locked"])
            self.assertNotIn("centre_mm", got)
            self.assertEqual("rear-outer" if row["reference"] == "SW3" else "rear-inner", got["frame"])
        encoder = overrides["encoder"]
        self.assertEqual([9.25, 81.25], encoder["anchor_mm"])
        self.assertEqual(270, encoder["rotation_deg"])
        self.assertEqual([], self.contract["placement_policy"]["released_instances"])

    def test_ptt_and_encoder_footprint_are_not_replaced_or_mirrored(self):
        ptt = self.contract["placement_overrides"]["ptt_switch"]
        self.assertEqual([72.1, 67.42], ptt["anchor_mm"])
        self.assertEqual(0, ptt["rotation_deg"])
        self.assertEqual("rear-outer", ptt["frame"])
        current = json.loads((ROOT / "hardware/ecad/h2-r2-contact-materialization-contract.json").read_text())
        self.assertEqual({"SW1": ["E"], "SW2": ["D"]}, current["contact_to_pad_overrides"]["alps_ec11e18244au"])

    def test_every_override_method_is_explicitly_supported_by_the_renderer(self):
        tree = ast.parse((ROOT / "hardware/layout/h6_r2_placement.py").read_text())
        palettes = [ast.literal_eval(node.value) for node in ast.walk(tree)
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                    and any(isinstance(target, ast.Name) and target.id == "palette" for target in node.targets)]
        self.assertEqual(1, len(palettes))
        for row in self.review["placement_rows"]:
            self.assertIn(self.contract["placement_overrides"][row["instance"]]["method"], palettes[0])

    def test_actual_u6_supply_owners_and_pins_are_explicit(self):
        policy = self.contract["placement_policy"]
        ledger = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json").read_text())
        pins = {(r["instance"], r["physical"]): r for r in ledger["rows"] if r["project"] == PROJECT}
        for child, (_ref, owner_pad, net) in U6_CAPS.items():
            self.assertEqual("hub_safe_i2c_boundary", policy["locality_owner_overrides"][child])
            self.assertEqual(net, pins["hub_safe_i2c_boundary", owner_pad]["net"])
            self.assertEqual(net, pins[child, "1"]["net"])
            pairs = [p for p in policy["critical_pad_pairs"] if p["second_instance"] == child]
            self.assertEqual(1, len(pairs))
            self.assertEqual(("hub_safe_i2c_boundary", owner_pad, "1", net, 3),
                             (pairs[0]["first_instance"], pairs[0]["first_pad_number"],
                              pairs[0]["second_pad_number"], pairs[0]["canonical_net"],
                              pairs[0]["maximum_distance_mm"]))

    def test_joint_dependency_and_mechanical_limits_do_not_disappear(self):
        self.assertFalse(self.review["fabrication_ready"])
        self.assertFalse(self.review["production_written"])
        self.assertFalse(self.review["production_promotion_authorized_by_this_report"])
        self.assertFalse(self.review["encoder_nominal_plan_review"]["finger_and_housing_access_qualified"])
        self.assertEqual(3.3, self.review["encoder_nominal_plan_review"]["nominal_knob_to_holder_courtyard_x_gap_mm"])
        deps = " ".join(self.review["joint_dependencies"]["required_before_encoder_promotion"])
        for token in ("C257", "R258", "R267", "joint", "not be promoted alone"):
            self.assertIn(token, deps)
        self.assertTrue(any("R283" in s and "unrouted" in s for s in self.review["remaining_limits"]))


@unittest.skipUnless(pcbnew, "KiCad Python is required for native, read-only geometry")
class EncoderLeftNativeTests(unittest.TestCase):
    def setUp(self):
        self.original_hash = hashlib.sha256(PCB.read_bytes()).hexdigest()
        self.board = pcbnew.LoadBoard(str(PCB))
        self.fps = {f.GetReference(): f for f in self.board.GetFootprints()}
        self.contract = json.loads(CONTRACT.read_text())
        self.review = json.loads(REVIEW.read_text())
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())
        self.rows = {r["instance"]: r for b in audit["boards"] if b["project"] == PROJECT for r in b["placements"]}
        self.before_nets = {ref: sorted((p.GetNumber(), p.GetNetname()) for p in f.Pads()) for ref, f in self.fps.items()}
        for row in self.review["placement_rows"]:
            fp = self.fps[row["reference"]]
            o = self.contract["placement_overrides"][row["instance"]]
            want_flipped = o["frame"] == "rear-inner"
            if fp.IsFlipped() != want_flipped:
                fp.Flip(fp.GetPosition(), False)
            fp.SetOrientationDegrees(o["rotation_deg"])
            fp.SetPosition(pcbnew.VECTOR2I(*(round(v * 1_000_000) for v in o["anchor_mm"])))
        self.bindings = json.loads((ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json").read_text())["projects"][PROJECT]["canonical_to_kicad"]

    def tearDown(self):
        self.assertEqual(self.original_hash, hashlib.sha256(PCB.read_bytes()).hexdigest())

    def u6_audit(self, contract=None, omit_owner=False):
        c = copy.deepcopy(contract or self.contract)
        c["placement_policy"]["critical_pad_pairs"] = [p for p in c["placement_policy"]["critical_pad_pairs"] if p["second_instance"] in U6_CAPS]
        entries = {instance: {"fp": self.fps[row["reference"]], "row": row} for instance, row in self.rows.items()}
        if omit_owner:
            entries.pop("hub_safe_i2c_boundary")
        return placement.critical_pad_pair_audit(PROJECT, entries, c, self.bindings)

    def test_all_seven_encoder_pth_have_exact_left_world_coordinates(self):
        fp = self.fps["SW3"]
        self.assertFalse(fp.IsFlipped())
        self.assertEqual("EC11E18244AU-ENGINEERING-PTH", str(fp.GetFPID().GetLibItemName()))
        # Independent transformation of the primary mounting-side terminal axes.
        expected = {("A", 1_750_000, 78_750_000), ("B", 1_750_000, 83_750_000),
                    ("C", 1_750_000, 81_250_000), ("D", 16_250_000, 78_750_000),
                    ("E", 16_250_000, 83_750_000), ("MP", 9_250_000, 75_000_000),
                    ("MP", 9_250_000, 87_500_000)}
        self.assertEqual(expected, {(p.GetNumber(), p.GetPosition().x, p.GetPosition().y) for p in fp.Pads()})
        self.assertEqual(7, len(list(fp.Pads())))
        for pad in fp.Pads():
            self.assertEqual(pcbnew.PAD_ATTRIB_PTH, pad.GetAttribute())
            self.assertTrue(pad.IsOnLayer(pcbnew.F_Cu) and pad.IsOnLayer(pcbnew.B_Cu))
            self.assertGreaterEqual(pad.GetBoundingBox().GetX(), 750_000)

    def test_pad_net_identities_are_preserved_without_writing_a_board(self):
        self.assertEqual(self.before_nets, {ref: sorted((p.GetNumber(), p.GetNetname()) for p in f.Pads()) for ref, f in self.fps.items()})

    def test_all_four_real_u6_bypasses_pass_actual_pin_distance(self):
        result = self.u6_audit()
        self.assertEqual("pass", result["status"])
        self.assertEqual(4, result["pair_count"])
        self.assertTrue(all(r["pad_centre_distance_mm"] < 2.3 for r in result["rows"]))

    def test_supply_pad_proximity_does_not_bypass_courtyard_locality(self):
        def local_result():
            rows = []
            for instance, ref in (("cc_band_buffer", "U30"), ("cc_band_buffer_bypass", "C114")):
                rows.append({"instance": instance, "reference": ref,
                             "courtyard_bbox_mm": placement.footprint_rect(self.fps[ref], "B.Cu")})
            return placement.locality_audit({"placements": rows}, self.contract)
        result = local_result()
        self.assertEqual("pass", result["status"])
        self.assertAlmostEqual(.175, result["rows"][0]["courtyard_gap_mm"])
        # Rejected first scratch proposal: electrically near VCC8, but1.525mm
        # from the owner courtyard exceeds the independent1.0mm policy.
        self.fps["C114"].SetOrientationDegrees(270)
        self.fps["C114"].SetPosition(pcbnew.VECTOR2I(17_100_000, 81_250_000))
        rejected = local_result()
        self.assertEqual("fail", rejected["status"])
        self.assertAlmostEqual(1.525, rejected["violations"][0]["courtyard_gap_mm"])

    def test_old_far_bypass_location_is_not_a_plausible_pass(self):
        self.fps["C33"].SetPosition(pcbnew.VECTOR2I(13_055_000, 81_355_000))
        result = self.u6_audit()
        self.assertEqual("fail", result["status"])
        self.assertTrue(any(r["second_reference"] == "C33" and r["pad_centre_distance_mm"] > 50 for r in result["violations"]))

    def test_missing_owner_wrong_pad_and_wrong_rail_fail_closed(self):
        self.assertEqual("fail", self.u6_audit(omit_owner=True)["status"])
        for key, value in (("first_pad_number", "999"), ("canonical_net", "3V3_MAIN")):
            c = copy.deepcopy(self.contract)
            pair = next(p for p in c["placement_policy"]["critical_pad_pairs"] if p["second_instance"] == "hub_safe_i2c_aon_100n")
            pair[key] = value
            with self.subTest(key=key):
                r = self.u6_audit(c)
                self.assertEqual("fail", r["status"])
                self.assertTrue(r["errors"])


if __name__ == "__main__":
    unittest.main()
