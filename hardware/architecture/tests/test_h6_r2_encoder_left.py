"""Historical left-side review, current under-Cap shaft and real bypass owners.

Historical rows cannot pin superseded parts to their earlier positions. Their
exact replacement scope and current source/native checks are independent;
neither nominal plan gaps nor these tests qualify finger/3D/routing access.
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
REPLACEMENT_REVIEW = "hardware/layout/h6-r2-encoder-under-cap-review.json"
HISTORICAL_ROWS_SHA = "8895c9796dfb23fd4a7c1f033c9d948c0fb1e854e229215276a49580557c944a"
PROJECT = "LESHY2-RF-R2"
PCB = ROOT / f"hardware/ecad/kicad/{PROJECT}/{PROJECT}.kicad_pcb"
EXPECTED_REFS = {
    "SW3", "U111", "U94", "U30", "U109", "U31", "C125", "C244",
    "C245", "C266", "C264", "C114", "U47", "C142", "C33", "C34",
    "C35", "C36", "R224", "R284", "R283", "R271", "C258", "R286",
}
SUPERSEDED_REFS = frozenset("C114 C125 C142 C244 C245 C258 C264 C266 R224 R271 R283 R284 R286 SW3 U109 U111 U30 U31 U47 U94".split())
# The finite user-approved candidate inventory, not all current overrides and
# not a set inferred from whichever rows happen to remain in the new review.
REPLACEMENT_REFS = frozenset("C114 C122 C125 C130 C131 C132 C136 C142 C144 C145 C149 C195 C199 C230 C244 C245 C250 C251 C252 C253 C256 C257 C258 C264 C265 C266 C268 C271 C276 C282 C58 C69 J3 Q6 R105 R115 R116 R117 R118 R119 R120 R121 R134 R138 R140 R171 R185 R201 R203 R224 R225 R230 R236 R237 R239 R242 R243 R244 R249 R251 R255 R256 R260 R261 R264 R267 R271 R279 R281 R282 R283 R284 R286 R287 R288 R49 R54 R56 R68 SW3 U100 U103 U109 U110 U111 U114 U119 U123 U126 U128 U15 U19 U30 U31 U32 U39 U40 U41 U42 U47 U48 U49 U68 U82 U83 U94".split())
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


def validate_scope(review, contract, replacement):
    rows = review["placement_rows"]
    assert len(rows) == len(EXPECTED_REFS) == 24
    assert {row["reference"] for row in rows} == EXPECTED_REFS
    assert hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == HISTORICAL_ROWS_SHA
    assert review["status"] == "placement_partially_superseded_not_mechanics_qualified"
    scope = review["placement_scope"]
    assert scope["historical_status"] == "isolated_source_candidate_requires_joint_audio_integration"
    assert scope["historical_fields"] == ["placement_rows", "source_inputs", "pad_pair_review", "native_preliminary_proof", "joint_dependencies", "encoder_nominal_plan_review"]
    assert scope["historical_placement_rows_sha256"] == HISTORICAL_ROWS_SHA
    assert scope["superseded_references"] == sorted(SUPERSEDED_REFS)
    assert scope["retained_current_reference_count"] == len(EXPECTED_REFS - SUPERSEDED_REFS) == 4
    assert scope["current_replacement_review"] == REPLACEMENT_REVIEW
    assert isinstance(replacement, dict), "current under-Cap replacement review is missing"
    new_rows = replacement["placement_rows"]
    assert len(new_rows) == len(REPLACEMENT_REFS) == 106
    assert {row["reference"] for row in new_rows} == REPLACEMENT_REFS
    new = {row["reference"]: row for row in new_rows}
    assert EXPECTED_REFS & new.keys() == SUPERSEDED_REFS
    for row in rows:
        ref, instance = row["reference"], row["instance"]
        expected = row["after"]
        if ref in SUPERSEDED_REFS:
            assert new[ref]["instance"] == instance
            expected = new[ref]["after"]
        got = contract["placement_overrides"][instance]
        assert expected["side"] == ("F.Cu" if ref == "SW3" else "B.Cu")
        assert got["frame"] == ("rear-outer" if ref == "SW3" else "rear-inner")
        assert expected["anchor_mm"] == got["anchor_mm"], ref
        assert expected["rotation_deg"] % 360 == got["rotation_deg"] % 360, ref
        assert got["mechanical_locked"] is True
        assert "centre_mm" not in got


class EncoderLeftSourceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text())
        self.review = json.loads(REVIEW.read_text())
        path = ROOT / REPLACEMENT_REVIEW
        self.replacement = json.loads(path.read_text()) if path.exists() else None

    def test_finite_scope_uses_real_left_native_datum_and_keeps_supports_inner(self):
        validate_scope(self.review, self.contract, self.replacement)
        overrides = self.contract["placement_overrides"]
        encoder = overrides["encoder"]
        self.assertEqual([9.25, 54], encoder["anchor_mm"])
        self.assertEqual(270, encoder["rotation_deg"])
        self.assertEqual([], self.contract["placement_policy"]["released_instances"])

    def test_historical_rows_and_exact_supersession_cannot_be_weakened(self):
        validate_scope(self.review, self.contract, self.replacement)
        for mutation in ("row", "remove", "add", "duplicate", "count", "owner"):
            review = copy.deepcopy(self.review)
            scope = review["placement_scope"]
            if mutation == "row": review["placement_rows"][0]["after"]["anchor_mm"][1] = 54
            elif mutation == "remove": scope["superseded_references"].pop()
            elif mutation == "add": scope["superseded_references"].append("C33")
            elif mutation == "duplicate": scope["superseded_references"].append("SW3")
            elif mutation == "count": scope["retained_current_reference_count"] = 3
            else: scope["current_replacement_review"] = "unreviewed.json"
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate_scope(review, self.contract, self.replacement)

    def test_new_review_requires_exact_unique_inventory_and_matching_current_poses(self):
        validate_scope(self.review, self.contract, self.replacement)
        for mutation in ("missing", "duplicate", "extra", "wrong_ref", "wrong_instance", "side", "pose", "angle"):
            replacement = copy.deepcopy(self.replacement)
            rows = replacement["placement_rows"]
            row = next(r for r in rows if r["reference"] == "SW3")
            if mutation == "missing": rows.remove(row)
            elif mutation == "duplicate": rows.append(copy.deepcopy(row))
            elif mutation == "extra": rows.append({**copy.deepcopy(row), "reference": "C197"})
            elif mutation == "wrong_ref": row["reference"] = "C197"
            elif mutation == "wrong_instance": row["instance"] = "ptt_switch"
            elif mutation == "side": row["after"]["side"] = "B.Cu"
            elif mutation == "pose": row["after"]["anchor_mm"][1] = 81.25
            else: row["after"]["rotation_deg"] = 0
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate_scope(self.review, self.contract, replacement)

    def test_retained_u6_cap_pose_cannot_drift_behind_supersession(self):
        validate_scope(self.review, self.contract, self.replacement)
        self.contract["placement_overrides"]["hub_safe_i2c_aon_100n"]["anchor_mm"][0] += 1
        with self.assertRaises(AssertionError):
            validate_scope(self.review, self.contract, self.replacement)

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
        # Inspect actual current native geometry; do not manufacture a PASS by
        # replaying source poses (or the historical24 rows) over a stale board.
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
        expected = {("A", 1_750_000, 51_500_000), ("B", 1_750_000, 56_500_000),
                    ("C", 1_750_000, 54_000_000), ("D", 16_250_000, 51_500_000),
                    ("E", 16_250_000, 56_500_000), ("MP", 9_250_000, 47_750_000),
                    ("MP", 9_250_000, 60_250_000)}
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
        # Reconstruct that historical two-part fixture explicitly; the current
        # U30 may have moved rigidly with C114 in the under-Cap correction.
        self.fps["U30"].SetOrientationDegrees(90)
        self.fps["U30"].SetPosition(pcbnew.VECTOR2I(13_225_000, 82_900_000))
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
