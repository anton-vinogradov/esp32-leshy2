"""Exact under-Cap repack: source scope and actual, read-only native geometry.

Pad-centre distances are lower bounds, not routed lengths or audio/RF/assembly
qualification. Native checks intentionally fail on the old placement; they do
not replay the desired source poses over a stale board to manufacture a pass.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = "LESHY2-RF-R2"
REVIEW_PATH = "hardware/layout/h6-r2-encoder-under-cap-review.json"
PCB = ROOT / f"hardware/ecad/kicad/{PROJECT}/{PROJECT}.kicad_pcb"
BASELINE_BOARD_SHA = "5d79ceab06d8ca16c87114b67e0217b462f4c044b559bc1160bdc07a8dca0795"
BASELINE_CONTRACT_SHA = "caedfdf37c1546feb18969396706e1f922c02f09cadf667027ff9f7874b839a9"
# Freeze the original identities, before poses and native pad-net multisets,
# independently of the current review/ledger. A joint substitution cannot pass.
IDENTITY_BEFORE_NETS_SHA = "b5b5ce1a3ebb87d96a14c85a734819ed57cf395a8065c7daf89203a54732f128"
PAIR_BASELINE_SHA = "4a126b13bfbb361b7872886a1a6bb1838b8dc03ed533d08848e92ce29ef86a32"
UNCHANGED_SOURCE_SHA = "e42d7151007f52c98b53a707137144cf2d7a0671a5229266f6bb5517153316c9"
EXPECTED_REFS = frozenset("""
    C114 C122 C125 C130 C131 C132 C136 C142 C144 C145 C149 C195 C199 C230
    C244 C245 C250 C251 C252 C253 C256 C257 C258 C264 C265 C266 C268 C271
    C276 C282 C58 C69 J3 Q6 R105 R115 R116 R117 R118 R119 R120 R121 R134
    R138 R140 R171 R185 R201 R203 R224 R225 R230 R236 R237 R239 R242 R243
    R244 R249 R251 R255 R256 R260 R261 R264 R267 R271 R279 R281 R282 R283
    R284 R286 R287 R288 R49 R54 R56 R68 SW3 U100 U103 U109 U110 U111 U114
    U119 U123 U126 U128 U15 U19 U30 U31 U32 U39 U40 U41 U42 U47 U48 U49
    U68 U82 U83 U94
""".split())
STRATEGIC = {
    "SW3": ("encoder", "F.Cu", 270, [9.25, 54]),
    "U39": ("voice", "B.Cu", 90, [15.4, 89]),
    "U83": ("headphone_jack", "B.Cu", 0, [.8, 39]),
    "J3": ("rf_rp_dbg_header", "B.Cu", 90, [30.425, 106.92]),
    "BT1": ("pack_holder", "F.Cu", 90, [40, 85]),
    "SW4": ("ptt_switch", "F.Cu", 0, [72.1, 67.42]),
    "MK1": ("microphone", "B.Cu", 0, [47, 147.4]),
    "U85": ("headset_mic_selector", "B.Cu", 90, [16.5, 113.75]),
    "U51": ("voice_v", "B.Cu", 90, [40.05, 53.5]),
}
RESERVED = {
    "C197": ("audio_capture_mic_coupling", "B.Cu", 270, [13.25, 111.25]),
    "R169": ("audio_capture_mic_bias", "B.Cu", 270, [13.25, 113.85]),
    "R235": ("unit_bleeder", "B.Cu", 0, [25.25, 127.5]),
}
NATIVE_ROUNDING = {
    "C132": [17.8695, 65.522499], "U128": [21.07, 66.394999],
    "R287": [45.25, 132.229999], "R288": [45.25, 133.479999],
}
# These are independent bounds on the *complete* 33-pair review, not a filter
# accepting whichever favorable pairs happen to remain in a future document.
PAIR_BOUNDS = {
    ("U68", "1", "C197", "2"): (0, 4.3),
    ("U68", "1", "R169", "1"): (0, 4.3),
    ("C197", "2", "R169", "1"): (0, 1.4),
    ("U85", "4", "C197", "1"): (0, 3.7),
    ("C231", "1", "C197", "1"): (0, 1.9),
    ("U68", "4", "C195", "1"): (0, 2.3),
    ("U68", "5", "C199", "1"): (0, 1.5),
    ("U68", "2", "C199", "2"): (3, 3.2),
    ("U68", "3", "C198", "2"): (66, 67),
    ("U68", "3", "R170", "1"): (76, 77),
    ("C195", "2", "U67", "3"): (71, 72),
    ("C195", "2", "C196", "1"): (45, 47),
    ("C195", "2", "R167", "1"): (44, 45),
    ("C195", "2", "R168", "2"): (42, 44),
    ("U68", "6", "U106", "1"): (51, 52),
    ("U68", "6", "R171", "1"): (64, 65),
    ("R169", "2", "R204", "2"): (0, 1.9),
    ("U100", "7", "C250", "1"): (0, 3),
    ("U100", "5", "C251", "1"): (0, 5),
    ("U100", "10", "C252", "1"): (0, 2.7),
    ("U100", "6", "C253", "1"): (0, 3),
    ("U100", "6", "R235", "1"): (11, 11.2),
    ("U100", "2", "R236", "1"): (0, 2.3),
    ("U100", "5", "R237", "1"): (0, 3.7),
    ("U100", "2", "R237", "2"): (0, 3.2),
    ("U100", "9", "R239", "1"): (0, 4),
    ("U100", "8", "C250", "2"): (0, 3.2),
    ("U100", "8", "C251", "2"): (8, 8.2),
    ("U100", "8", "C252", "2"): (4, 4.2),
    ("U100", "8", "C253", "2"): (0, 2.7),
    ("U83", "1", "U85", "3"): (80, 81),
    ("C136", "1", "U37", "4"): (0, 2.3),
    ("C136", "2", "U37", "6"): (0, 2.8),
}
REGRESSIONS = {
    ("U68", "2", "C199", "2"), ("U68", "3", "C198", "2"),
    ("U68", "3", "R170", "1"), ("C195", "2", "U67", "3"),
    ("C195", "2", "C196", "1"), ("C195", "2", "R167", "1"),
    ("C195", "2", "R168", "2"), ("U68", "6", "U106", "1"),
    ("U68", "6", "R171", "1"), ("U100", "8", "C252", "2"),
    ("U83", "1", "U85", "3"),
}


def read(relative):
    return json.loads((ROOT / relative).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def angle(value):
    assert type(value) in (int, float) and math.isfinite(value)
    return value % 360


def coordinates(value):
    assert isinstance(value, list) and len(value) == 2
    assert all(type(v) in (int, float) and math.isfinite(v) for v in value)
    return value


def validate_source(review, contract, instances, nets):
    assert review["schema_version"] == 1 and review["project"] == PROJECT
    assert review["baseline_board_sha256"] == BASELINE_BOARD_SHA
    assert review["baseline_contract_sha256"] == BASELINE_CONTRACT_SHA
    assert set(review["authority"]) == {"fabrication_ready", "assembly_qualified", "audio_qualified", "rf_qualified"}
    assert all(v is False for v in review["authority"].values())
    rows = review["placement_rows"]
    assert len(rows) == len(EXPECTED_REFS) == 106
    assert {r["reference"] for r in rows} == EXPECTED_REFS
    identity_keys = ("reference", "instance", "device_id", "mpn", "footprint", "before", "pad_number_net_multiset_sha256")
    assert digest([{k: r[k] for k in identity_keys} for r in sorted(rows, key=lambda r: r["reference"])]) == IDENTITY_BEFORE_NETS_SHA
    ledger_rows = [r for r in instances if r["project"] == PROJECT]
    ledger = {r["reference"]: r for r in ledger_rows}
    assert len(ledger) == len(ledger_rows)
    by_ref = {r["reference"]: r for r in rows}
    overrides = contract["placement_overrides"]
    for ref, row in by_ref.items():
        assert all(row[k] == ledger[ref][k] for k in ("instance", "device_id", "mpn", "footprint")), ref
        after = row["after"]
        target = overrides[row["instance"]]
        assert after["side"] == ("F.Cu" if ref == "SW3" else "B.Cu"), ref
        assert target["frame"] == ("rear-outer" if ref == "SW3" else "rear-inner"), ref
        assert coordinates(after["anchor_mm"]) == coordinates(target["anchor_mm"]), ref
        assert angle(after["rotation_deg"]) == angle(target["rotation_deg"]), ref
        assert target["mechanical_locked"] is True and "centre_mm" not in target, ref
        assert row["before"] != after, ref
    assert {r["reference"] for r in rows if "native_after_anchor_mm" in r} == set(NATIVE_ROUNDING)
    for ref, expected in NATIVE_ROUNDING.items():
        assert by_ref[ref]["native_after_anchor_mm"] == expected
        delta = [round(abs(a-b) * 1e6) for a, b in zip(expected, by_ref[ref]["after"]["anchor_mm"])]
        assert delta == [0, 1], ref
    assert set(review["strategic_poses"]) == set(STRATEGIC)
    for ref, (instance, side, rotation, at) in {**STRATEGIC, **RESERVED}.items():
        assert ledger[ref]["instance"] == instance, ref
        target = overrides[instance]
        # The unchanged holder uses its established centre datum; the moved
        # components and the other reserved interfaces use native anchors.
        assert target["centre_mm" if ref == "BT1" else "anchor_mm"] == at, ref
        assert angle(target["rotation_deg"]) == rotation, ref
        assert target["frame"] == ("rear-outer" if side == "F.Cu" else "rear-inner"), ref
        assert target["mechanical_locked"] is True, ref
        if ref in STRATEGIC:
            assert review["strategic_poses"][ref] == dict(anchor_mm=at, rotation_deg=rotation, side=side), ref
        if ref in EXPECTED_REFS:
            assert by_ref[ref]["after"] == dict(anchor_mm=at, rotation_deg=rotation, side=side), ref
    unchanged = {ref: spec for ref, spec in {**STRATEGIC, **RESERVED}.items() if ref not in EXPECTED_REFS}
    assert digest({ref: overrides[spec[0]] for ref, spec in unchanged.items()}) == UNCHANGED_SOURCE_SHA
    assert review["unchanged_reserved_cell_references"] == sorted(RESERVED)
    assert review["nominal_plan_gaps_mm"] == {"15mm_knob_to_cap": 5.48, "15mm_knob_to_holder": 3.3}
    for name, expected in (("audio", {"U68", "C199", "C195", "C197", "R169"}),
                           ("external_unit_efuse", {"U100", "C250", "C251", "C252", "C253", "R235", "R236", "R237", "R239"})):
        cell = review["compact_cells"][name]
        assert set(cell) == expected
        for ref, pose in cell.items():
            target = overrides[ledger[ref]["instance"]]
            assert pose["anchor_mm"] == target["anchor_mm"], ref
            assert angle(pose["rotation_deg"]) == angle(target["rotation_deg"]), ref
    pairs = review["actual_pad_centre_distances_not_route_lengths"]
    assert len(pairs) == len(PAIR_BOUNDS) == 33
    assert {tuple(r["first"] + r["second"]) for r in pairs} == set(PAIR_BOUNDS)
    assert digest([{k: r[k] for k in ("first", "second", "net", "before_mm")} for r in pairs]) == PAIR_BASELINE_SHA
    for pair in pairs:
        key = tuple(pair["first"] + pair["second"])
        for ref, pad in (pair["first"], pair["second"]):
            endpoints = [r for r in nets if r["project"] == PROJECT and r["reference"] == ref and r["physical"] == pad]
            assert endpoints and all(r["net"] == pair["net"].rsplit("/", 1)[-1] for r in endpoints), key
        before, after, delta = (pair[k] for k in ("before_mm", "after_mm", "delta_mm"))
        assert all(type(v) in (int, float) and math.isfinite(v) for v in (before, after, delta)), key
        low, high = PAIR_BOUNDS[key]
        assert low <= after <= high and abs(round(after-before, 6)-delta) < 1e-9, key
        assert (delta > 0) == (key in REGRESSIONS), key
    assert review["preservation_required"] == dict(original_copper_objects=765, original_ui_board_unchanged=True,
        all_pad_net_identities=True, all_exact_mpns=True)
    limits = " ".join(review["limits"])
    for phrase in ("not finger access", "paths become longer", "low-noise audio routing", "do not qualify the audio circuit",
                   "does not approve RF performance", "including regressions", "do not qualify return loops",
                   "No phase completion or fabrication release"):
        assert phrase in limits, phrase


class EncoderUnderCapSourceTests(unittest.TestCase):
    def setUp(self):
        self.review = read(REVIEW_PATH)
        self.contract = read("hardware/layout/h6-r2-placement-contract.json")
        self.instances = read("hardware/ecad/generated/H2-R2-native-instance-ledger.json")["rows"]
        self.nets = read("hardware/ecad/generated/H2-R2-native-net-ledger.json")["rows"]

    def check(self):
        validate_source(self.review, self.contract, self.instances, self.nets)

    def test_exact_106_identity_source_scope_strategic_poses_and_33_pair_bounds(self):
        self.check()

    def test_missing_duplicate_extra_or_substituted_inventory_rejected(self):
        for change in ("missing", "duplicate", "extra", "wrong_ref"):
            review = copy.deepcopy(self.review)
            rows = review["placement_rows"]
            if change == "missing": rows.pop()
            elif change == "duplicate": rows[-1] = copy.deepcopy(rows[0])
            elif change == "extra": rows.append(copy.deepcopy(rows[0]))
            else: rows[-1]["reference"] = "U85"
            with self.subTest(change=change), self.assertRaises(AssertionError):
                validate_source(review, self.contract, self.instances, self.nets)

    def test_joint_old_encoder_pose_or_wrong_face_is_rejected(self):
        for change in ("old_pose", "face", "angle"):
            review, contract = copy.deepcopy(self.review), copy.deepcopy(self.contract)
            row = next(r for r in review["placement_rows"] if r["reference"] == "SW3")
            if change == "old_pose":
                row["after"]["anchor_mm"] = contract["placement_overrides"]["encoder"]["anchor_mm"] = [9.25, 81.25]
            elif change == "face":
                row["after"]["side"] = "B.Cu"
                contract["placement_overrides"]["encoder"]["frame"] = "rear-inner"
            else:
                row["after"]["rotation_deg"] = contract["placement_overrides"]["encoder"]["rotation_deg"] = 0
            with self.subTest(change=change), self.assertRaises(AssertionError):
                validate_source(review, contract, self.instances, self.nets)

    def test_baseline_identity_pad_hash_and_fixed_source_cannot_drift(self):
        for change in ("baseline", "before", "net_hash", "joint_mpn", "fixed_source", "rounding"):
            review, contract, instances = copy.deepcopy(self.review), copy.deepcopy(self.contract), copy.deepcopy(self.instances)
            row = next(r for r in review["placement_rows"] if r["reference"] == "U100")
            if change == "baseline": review["baseline_board_sha256"] = "0" * 64
            elif change == "before": row["before"]["anchor_mm"][0] += 1
            elif change == "net_hash": row["pad_number_net_multiset_sha256"] = "0" * 64
            elif change == "joint_mpn":
                row["mpn"] = "substitute"
                next(r for r in instances if r["project"] == PROJECT and r["reference"] == "U100")["mpn"] = "substitute"
            elif change == "fixed_source": contract["placement_overrides"]["headset_mic_selector"]["anchor_mm"][1] += 1
            else: next(r for r in review["placement_rows"] if r["reference"] == "R287")["native_after_anchor_mm"][1] += .000001
            with self.subTest(change=change), self.assertRaises(AssertionError):
                validate_source(review, contract, instances, self.nets)

    def test_hidden_remote_audio_regression_bad_cell_or_qualification_is_rejected(self):
        for change in ("missing_pair", "duplicate_pair", "hide_span", "bad_local", "net", "authority", "limits"):
            review = copy.deepcopy(self.review)
            pairs = review["actual_pad_centre_distances_not_route_lengths"]
            if change == "missing_pair": pairs.pop()
            elif change == "duplicate_pair": pairs[-1] = copy.deepcopy(pairs[0])
            elif change in ("hide_span", "bad_local"):
                row = next(r for r in pairs if r["first"] == (["U83", "1"] if change == "hide_span" else ["U100", "7"]))
                row["after_mm"] = 4 if change == "hide_span" else 12
                row["delta_mm"] = round(row["after_mm"]-row["before_mm"], 6)
            elif change == "net": pairs[0]["net"] = "POWER_GROUND"
            elif change == "authority": review["authority"]["audio_qualified"] = True
            else: review["limits"] = []
            with self.subTest(change=change), self.assertRaises(AssertionError):
                validate_source(review, self.contract, self.instances, self.nets)


try:
    import pcbnew
except ImportError:
    pcbnew = None


@unittest.skipUnless(pcbnew, "Native KiCad Python required; no CLI or production board writes")
class EncoderUnderCapNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_sha = hashlib.sha256(PCB.read_bytes()).hexdigest()
        cls.board = pcbnew.LoadBoard(str(PCB))
        cls.fps = {fp.GetReference(): fp for fp in cls.board.GetFootprints()}
        cls.review = read(REVIEW_PATH)
        cls.rows = {r["reference"]: r for r in cls.review["placement_rows"]}
        cls.bindings = read("hardware/layout/generated/H6-R2-kicad-net-bindings.json")["projects"][PROJECT]["canonical_to_kicad"]

    @classmethod
    def tearDownClass(cls):
        assert hashlib.sha256(PCB.read_bytes()).hexdigest() == cls.before_sha

    def assert_pose(self, ref, side, rotation, at):
        fp = self.fps[ref]
        self.assertEqual(side == "B.Cu", fp.IsFlipped(), ref)
        self.assertEqual(rotation % 360, angle(fp.GetOrientationDegrees()), ref)
        self.assertEqual([round(v * 1e6) for v in at], [fp.GetPosition().x, fp.GetPosition().y], ref)

    def assert_identity(self, ref):
        fp, row = self.fps[ref], self.rows[ref]
        self.assertEqual(row["mpn"], fp.GetValue(), ref)
        self.assertEqual(row["footprint"], fp.GetFPIDAsString(), ref)
        self.assertEqual(row["pad_number_net_multiset_sha256"],
            digest(sorted([p.GetNumber(), p.GetNetname()] for p in fp.Pads())), ref)

    def test_all_106_actual_native_poses_and_pad_net_multisets(self):
        self.assertEqual(EXPECTED_REFS, set(self.rows))
        self.assertEqual(106, len(self.review["placement_rows"]))
        for ref, row in self.rows.items():
            pose = row["after"]
            with self.subTest(ref=ref):
                self.assert_pose(ref, pose["side"], pose["rotation_deg"], row.get("native_after_anchor_mm", pose["anchor_mm"]))
                self.assert_identity(ref)

    def test_strategic_and_reserved_native_positions_are_independent(self):
        for ref, (_, side, rotation, at) in {**STRATEGIC, **RESERVED}.items():
            with self.subTest(ref=ref): self.assert_pose(ref, side, rotation, at)
        self.assertEqual(765, len(list(self.board.GetTracks())))

    def test_all_33_recorded_distances_use_actual_matching_native_pads(self):
        pairs = self.review["actual_pad_centre_distances_not_route_lengths"]
        self.assertEqual(set(PAIR_BOUNDS), {tuple(r["first"] + r["second"]) for r in pairs})
        self.assertEqual(33, len(pairs))
        for row in pairs:
            key = tuple(row["first"] + row["second"])
            endpoint_pads = [[p for p in self.fps[ref].Pads() if p.GetNumber() == pad] for ref, pad in (row["first"], row["second"])]
            with self.subTest(pair=key):
                self.assertTrue(all(endpoint_pads))
                canonical = row["net"].rsplit("/", 1)[-1]
                self.assertEqual({self.bindings[canonical]}, {p.GetNetname() for group in endpoint_pads for p in group})
                actual = min(math.hypot((a.GetPosition().x-b.GetPosition().x)/1e6,
                    (a.GetPosition().y-b.GetPosition().y)/1e6) for a in endpoint_pads[0] for b in endpoint_pads[1])
                self.assertAlmostEqual(row["after_mm"], actual, delta=.000001)
                low, high = PAIR_BOUNDS[key]
                self.assertGreaterEqual(actual, low)
                self.assertLessEqual(actual, high)

    def test_old_encoder_native_pose_and_wrong_face_are_rejected_in_memory(self):
        fp = self.fps["SW3"]
        saved = fp.GetPosition()
        try:
            fp.SetPosition(pcbnew.VECTOR2I(9_250_000, 81_250_000))
            with self.assertRaises(AssertionError): self.assert_pose("SW3", "F.Cu", 270, [9.25, 54])
        finally:
            fp.SetPosition(saved)
        with self.assertRaises(AssertionError): self.assert_pose("SW3", "B.Cu", 270, [9.25, 54])

    def test_native_part_substitution_or_pad_net_loss_is_rejected_in_memory(self):
        fp = self.fps["U100"]
        saved = fp.GetValue()
        try:
            fp.SetValue("substitute")
            with self.assertRaises(AssertionError): self.assert_identity("U100")
        finally:
            fp.SetValue(saved)
        pad = next(p for p in fp.Pads() if p.GetNumber() == "7")
        net = pad.GetNetCode()
        try:
            pad.SetNetCode(0)
            with self.assertRaises(AssertionError): self.assert_identity("U100")
        finally:
            pad.SetNetCode(net)


if __name__ == "__main__":
    unittest.main()
