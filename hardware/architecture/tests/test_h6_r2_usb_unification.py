"""Finite GCT adoption: preserve every working contact; no generic pad waiver."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_usb_unification as guard

try:
    import pcbnew
except ImportError:
    pcbnew = None

REVIEW = ROOT / "hardware/layout/h6-r2-usb-unification.json"


def states():
    data = json.loads(REVIEW.read_text())["migration_snapshots"]
    return data["before"], data["after"]


class UsbUnificationTests(unittest.TestCase):
    def test_exact_reviewed_transition_and_independent_contact_population(self):
        before, after = states()
        result = guard.verify_transition(before, after, "LESHY2-RF-R2")
        expected = Counter({name: 1 for name in (
            "A1", "A4", "A5", "A6", "A7", "A8", "A9", "A12",
            "B1", "B4", "B5", "B6", "B7", "B8", "B9", "B12")})
        expected["SH"] = 4
        for state in (before, after):
            self.assertEqual(expected, Counter(p["number"] for p in state["pads"] if p["number"]))
            nets = {p["number"]: p["net"] for p in state["pads"] if p["number"]}
            for name in ("A6", "B6"):
                self.assertEqual("/RF_01_USB_PD_CHARGE/USB2_CONNECTOR_P", nets[name])
            for name in ("A7", "B7"):
                self.assertEqual("/RF_01_USB_PD_CHARGE/USB2_CONNECTOR_N", nets[name])
            self.assertEqual("", nets["A8"])
            self.assertEqual("", nets["B8"])
        self.assertEqual(20, result["named_pad_net_occurrences_preserved"])
        self.assertEqual(17, result["logical_contacts_preserved"])
        self.assertEqual(2, result["removed_anonymous_no_net_smd_lands"])
        self.assertFalse(result["fabrication_ready"])

    def test_every_missing_or_changed_named_pad_is_rejected_on_both_sides(self):
        for side in (0, 1):
            original = states()[side]
            for index, pad in enumerate(original["pads"]):
                if not pad["number"]:
                    continue
                for mutation in ("remove", "net", "rename", "duplicate"):
                    pair = states()
                    if mutation == "remove":
                        del pair[side]["pads"][index]
                    elif mutation == "net":
                        pair[side]["pads"][index]["net"] = "/wrong/full/net"
                    elif mutation == "rename":
                        pair[side]["pads"][index]["number"] = "SH" if pad["number"] != "SH" else "A1"
                    else:
                        pair[side]["pads"].append(copy.deepcopy(pad))
                    with self.subTest(side=side, pad=pad["number"], mutation=mutation), self.assertRaises(ValueError):
                        guard.verify_transition(*pair, "LESHY2-RF-R2")

    def test_anonymous_geometry_drill_layer_or_net_changes_are_rejected(self):
        for side in (0, 1):
            for index, pad in enumerate(states()[side]["pads"]):
                for field in ("at_nm", "size_nm", "drill_nm", "shape", "layers", "net", "kind"):
                    pair = states()
                    changed = pair[side]["pads"][index]
                    if field.endswith("_nm"):
                        changed[field][0] += 1
                    elif field == "shape":
                        changed[field] += 1
                    elif field == "layers":
                        changed[field] = changed[field][1:]
                    elif field == "net":
                        changed[field] = "/foreign/net"
                    else:
                        changed[field] = "unsupported"
                    with self.subTest(side=side, index=index, field=field), self.assertRaises(ValueError):
                        guard.verify_transition(*pair, "LESHY2-RF-R2")

    def test_wrong_board_reference_identity_side_pose_or_extra_pad_is_rejected(self):
        for side in (0, 1):
            for field, value in (("reference", "J4"), ("footprint", "wrong:Footprint"),
                                 ("value", "GCT USB4105-GF-A-alternative"), ("side", "F.Cu"),
                                 ("rotation_deg", 0), ("anchor_nm", [16470000, 146325000])):
                pair = states(); pair[side][field] = value
                with self.subTest(side=side, field=field), self.assertRaises(ValueError):
                    guard.verify_transition(*pair, "LESHY2-RF-R2")
        before, after = states()
        with self.assertRaises(ValueError):
            guard.verify_transition(before, after, "LESHY2-UI-R2")
        after["pads"].append(copy.deepcopy(next(p for p in before["pads"] if not p["number"] and p["kind"] == "smd")))
        with self.assertRaises(ValueError):
            guard.verify_transition(before, after, "LESHY2-RF-R2")

    def test_review_sha_and_finite_scope_are_required(self):
        allowance = {"feature_id": guard.FEATURE_ID,
                     "source_review_sha256": hashlib.sha256(REVIEW.read_bytes()).hexdigest()}
        self.assertEqual(allowance, guard.verify_allowance(allowance, guard.PROJECT, REVIEW))
        for bad in ({}, {**allowance, "source_review_sha256": "0" * 64}, {**allowance, "extra": True}):
            with self.assertRaises(ValueError):
                guard.verify_allowance(bad, guard.PROJECT, REVIEW)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.json"
            for field, value in (("feature_id", "wrong"), ("changed_references", ["J1"]),
                                 ("after_footprint", guard.BEFORE_ID), ("production_release_authorized", True)):
                data = json.loads(REVIEW.read_text()); data[field] = value
                path.write_text(json.dumps(data))
                bad = {"feature_id": guard.FEATURE_ID, "source_review_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                with self.subTest(field=field), self.assertRaises(ValueError):
                    guard.verify_allowance(bad, guard.PROJECT, path)


@unittest.skipUnless(pcbnew, "KiCad Python is required for native preservation guards")
class NativeUsbUnificationTests(unittest.TestCase):
    def test_companion_is_exact_translation_not_an_arbitrary_second_move(self):
        board = pcbnew.LoadBoard(str(ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb"))
        fp = next(f for f in board.GetFootprints() if f.GetReference() == "U5")
        after = guard.snapshot(fp, pcbnew)
        before = copy.deepcopy(after)
        before["anchor_nm"][1] += 150000
        for pad in before["pads"]:
            pad["at_nm"][1] += 150000
        result = guard.verify_companion(before, after, guard.PROJECT)
        self.assertEqual([0,-150000], result["translation_nm"])
        for field, value in (("reference", "C31"), ("side", "F.Cu"), ("rotation_deg", 180),
                             ("anchor_nm", [16500001,139350000]), ("footprint", "Other:FP"), ("value", "Other MPN")):
            changed = copy.deepcopy(after); changed[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                guard.verify_companion(before, changed, guard.PROJECT)
        for field in ("at_nm", "size_nm", "net"):
            changed = copy.deepcopy(after)
            if field == "net": changed["pads"][0][field] = "/wrong/net"
            else: changed["pads"][0][field][0] += 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                guard.verify_companion(before, changed, guard.PROJECT)

    def test_current_four_ports_are_the_same_exact_gct_with_flush_mouths(self):
        geometries = []
        for project, refs in (("LESHY2-RF-R2", {"J1": 16469999, "J4": 37470000}),
                              ("LESHY2-UI-R2", {"J9": 26100000, "J11": 14870000})):
            path = ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
            before = path.read_bytes()
            board = pcbnew.LoadBoard(str(path))
            fps = {f.GetReference(): f for f in board.GetFootprints()}
            for ref, x in refs.items():
                state = guard.snapshot(fps[ref], pcbnew)
                self.assertEqual("Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", state["footprint"])
                self.assertEqual("GCT USB4105-GF-A", state["value"])
                self.assertEqual("B.Cu", state["side"])
                self.assertEqual(180, state["rotation_deg"])
                self.assertEqual([x, 146325000], state["anchor_nm"])
                self.assertEqual(150000000, state["anchor_nm"][1]+3675000)
                for pad in state["pads"]:
                    pad["at_nm"] = [pad["at_nm"][0]-x, pad["at_nm"][1]-146325000]
                geometries.append(guard.geometry_sha256(state))
            if project == "LESHY2-RF-R2":
                u5 = fps["U5"]
                self.assertEqual([16500000,139350000], [u5.GetPosition().x,u5.GetPosition().y])
                self.assertTrue(u5.IsFlipped())
                self.assertEqual(0, u5.GetOrientationDegrees() % 360)
            self.assertEqual(before, path.read_bytes())
        self.assertEqual(4, len(geometries))
        self.assertEqual(1, len(set(geometries)), "all four physical pad/locator geometries must match by translation")

    def test_generic_stage_guard_still_rejects_anonymous_smd_removal(self):
        import h6_r2_stage_placement_update as stage
        for allowance in ([], {}, [""], {"": 2}):
            with self.subTest(allowance=allowance), self.assertRaises(ValueError):
                stage.verify_pad_nets("J1", Counter({("", ""): 2}), Counter(), allowance)

    def test_old_named_or_anonymous_copper_attachments_are_rejected(self):
        for reference in ("J1", "U5"):
            for number in ("A6", ""):
                board = pcbnew.BOARD()
                for ref in ("J1", "U5"):
                    fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref); board.Add(fp)
                    pad = pcbnew.PAD(fp); pad.SetNumber(number)
                    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD); pad.SetShape(pcbnew.PAD_SHAPE_RECT)
                    pad.SetSize(pcbnew.VECTOR2I(500000, 500000))
                    layers = pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu); pad.SetLayerSet(layers)
                    pad.SetPosition(pcbnew.VECTOR2I(10000000 if ref == "J1" else 20000000, 10000000))
                    fp.Add(pad)
                guard.require_no_old_copper_attachments(board, ["J1", "U5"], pcbnew)
                fp = next(f for f in board.GetFootprints() if f.GetReference() == reference)
                start = next(iter(fp.Pads())).GetPosition()
                track = pcbnew.PCB_TRACK(board); track.SetStart(start)
                track.SetEnd(pcbnew.VECTOR2I(start.x + 2000000, start.y))
                track.SetWidth(200000); track.SetLayer(pcbnew.F_Cu); board.Add(track)
                with self.subTest(reference=reference, number=number), self.assertRaises(ValueError):
                    guard.require_no_old_copper_attachments(board, ["J1", "U5"], pcbnew)
        with self.assertRaises(ValueError):
            guard.require_no_old_copper_attachments(board, ["J1"], pcbnew)


if __name__ == "__main__":
    unittest.main()
