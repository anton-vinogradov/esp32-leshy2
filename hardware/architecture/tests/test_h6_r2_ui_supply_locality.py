"""Actual supply-pin checks, independent of capacitor-name heuristics."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
PROJECT = "LESHY2-UI-R2"
PCB = ROOT / f"hardware/ecad/kicad/{PROJECT}/{PROJECT}.kicad_pcb"
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
REVIEW = ROOT / "hardware/layout/h6-r2-ui-supply-locality.json"
EXPECTED = {
    "C7": ("backlight_efuse_input_cap", "backlight_efuse", "6", "3V3_MAIN", 2),
    "C17": ("sd_power_input_cap", "sd_power_switch", "1", "3V3_MAIN", 2.5),
    "C16": ("sd_power_hf_cap", "sd", "4", "SD_CARD_3V3", 3),
    "C15": ("sd_power_bulk_cap", "sd", "4", "SD_CARD_3V3", 6.5),
    "C63": ("nrf0_module_hf_cap", "nrf0", "1", "3V3_NRF_GROUP", 3.5),
    "C62": ("nrf0_module_bulk_cap", "nrf0", "1", "3V3_NRF_GROUP", 4.5),
    "C69": ("nrf1_module_hf_cap", "nrf1", "1", "3V3_NRF_GROUP", 5),
    "C68": ("nrf1_module_bulk_cap", "nrf1", "1", "3V3_NRF_GROUP", 7),
    "C75": ("nrf2_module_hf_cap", "nrf2", "1", "3V3_NRF_GROUP", 3),
    "C74": ("nrf2_module_bulk_cap", "nrf2", "1", "3V3_NRF_GROUP", 7.5),
}


class UISupplySourceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text())
        self.review = json.loads(REVIEW.read_text())

    def test_finite_fourteen_reference_scope_and_locked_inner_poses(self):
        rows = self.review["placement_rows"]
        self.assertEqual(set(EXPECTED) | {"R18", "R42", "R198", "R99"}, {r["reference"] for r in rows})
        self.assertEqual(14, len(rows))
        for row in rows:
            pose = self.contract["placement_overrides"][row["instance"]]
            self.assertEqual("ui-inner", pose["frame"])
            self.assertTrue(pose["mechanical_locked"])
            self.assertEqual(row["anchor_mm"], pose["anchor_mm"])
            self.assertEqual(row["rotation_deg"], pose["rotation_deg"])
        self.assertEqual([], self.contract["placement_policy"]["released_instances"])

    def test_exact_power_owners_pins_and_rails_are_not_prefix_guesses(self):
        policy = self.contract["placement_policy"]
        ledger = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json").read_text())
        pins = {(r["instance"], r["physical"]): r["net"] for r in ledger["rows"] if r["project"] == PROJECT}
        for child, owner, pad, net, limit in EXPECTED.values():
            self.assertEqual(owner, policy["locality_owner_overrides"][child])
            # New module/card locality rules use one common 2mm package-gap
            # ceiling in addition to the independent exact supply-pin bound.
            self.assertEqual(2.0, policy["locality_max_gap_mm"][child])
            self.assertEqual(net, pins[owner, pad])
            self.assertEqual(net, pins[child, "1"])
            self.assertEqual("POWER_GROUND", pins[child, "2"])
            pairs = [r for r in policy["critical_pad_pairs"] if r["project"] == PROJECT and r["second_instance"] == child]
            self.assertEqual(1, len(pairs))
            pair = pairs[0]
            self.assertEqual((owner, pad, "1", net, limit),
                             (pair["first_instance"], pair["first_pad_number"], pair["second_pad_number"],
                              pair["canonical_net"], pair["maximum_distance_mm"]))


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Requires native KiCad Python")
class UISupplyNativeTests(unittest.TestCase):
    def setUp(self):
        import pcbnew
        import h6_r2_placement
        self.p = pcbnew
        self.placement = h6_r2_placement
        self.original_hash = hashlib.sha256(PCB.read_bytes()).hexdigest()
        self.board = pcbnew.LoadBoard(str(PCB))
        self.fps = {f.GetReference(): f for f in self.board.GetFootprints()}
        self.review = json.loads(REVIEW.read_text())
        self.contract = json.loads(CONTRACT.read_text())
        self.before_nets = {ref: sorted((p.GetNumber(), p.GetNetname()) for p in f.Pads()) for ref, f in self.fps.items()}
        for row in self.review["placement_rows"]:
            f = self.fps[row["reference"]]
            self.assertTrue(f.IsFlipped())
            f.SetOrientationDegrees(row["rotation_deg"])
            f.SetPosition(pcbnew.VECTOR2I(*(round(v * 1_000_000) for v in row["anchor_mm"])))
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())
        self.entries = {r["instance"]: {"fp": self.fps[r["reference"]], "row": r}
                        for b in audit["boards"] if b["project"] == PROJECT for r in b["placements"]}
        self.bindings = json.loads((ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json").read_text())["projects"][PROJECT]["canonical_to_kicad"]

    def tearDown(self):
        self.assertEqual(self.original_hash, hashlib.sha256(PCB.read_bytes()).hexdigest())

    def result(self, contract=None, entries=None):
        c = copy.deepcopy(contract or self.contract)
        children = {x[0] for x in EXPECTED.values()}
        c["placement_policy"]["critical_pad_pairs"] = [r for r in c["placement_policy"]["critical_pad_pairs"]
                                                       if r["project"] == PROJECT and r["second_instance"] in children]
        return self.placement.critical_pad_pair_audit(PROJECT, entries or self.entries, c, self.bindings)

    def test_ten_actual_supply_pairs_and_all_original_net_identities(self):
        result = self.result()
        self.assertEqual("pass", result["status"], result)
        self.assertEqual(10, result["pair_count"])
        self.assertEqual(self.before_nets, {ref: sorted((p.GetNumber(), p.GetNetname()) for p in f.Pads()) for ref, f in self.fps.items()})

    def test_former_far_backlight_and_sd_caps_cannot_pass(self):
        for ref in ("C7", "C16"):
            row = next(r for r in self.review["placement_rows"] if r["reference"] == ref)
            self.fps[ref].SetPosition(self.p.VECTOR2I(*(round(v * 1_000_000) for v in row["old_anchor_mm"])))
        result = self.result()
        self.assertEqual("fail", result["status"])
        self.assertTrue({"C7", "C16"}.issubset({r["second_reference"] for r in result["violations"]}))

    def test_missing_owner_wrong_pad_or_wrong_rail_fails_closed(self):
        entries = dict(self.entries)
        entries.pop("backlight_efuse")
        self.assertEqual("fail", self.result(entries=entries)["status"])
        for field, value in (("first_pad_number", "999"), ("canonical_net", "SD_CARD_3V3")):
            c = copy.deepcopy(self.contract)
            pair = next(r for r in c["placement_policy"]["critical_pad_pairs"] if r["second_instance"] == "backlight_efuse_input_cap")
            pair[field] = value
            with self.subTest(field=field):
                self.assertEqual("fail", self.result(contract=c)["status"])


if __name__ == "__main__":
    unittest.main()
