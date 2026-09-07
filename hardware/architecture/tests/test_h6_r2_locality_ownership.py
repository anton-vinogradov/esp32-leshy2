"""Protect electrically reviewed bypass owners from instance-prefix inference.

These capacitors use a radio/service name but bypass a different physical IC.
The 3 mm pad-centre ceiling is a placement screening target, not a vendor
guarantee or a substitute for reviewing the routed supply/ground loop.
"""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SUPPLY = "AON_SAFE_3V3"
GROUND = "POWER_GROUND"
MAXIMUM_PAD_DISTANCE_MM = 3.0

# child: (physical owner, owner supply pad, owner ground pad)
# Supply pins come from the H2 native schematic, not name similarity.
EXPECTED_OWNERS = {
    "s3_detector_bypass": ("det_s3", "6", "2"),
    "c5_detector_bypass": ("det_c5", "6", "2"),
    "nrf0_detector_bypass": ("det_nrf0", "8", "5"),
    "nrf1_detector_bypass": ("det_nrf1", "8", "5"),
    "nrf2_detector_bypass": ("det_nrf2", "8", "5"),
    "cc_detector_bypass": ("det_cc", "8", "5"),
    "voice_detector_bypass": ("det_voice", "8", "5"),
    "voice_v_detector_bypass": ("det_voice_v", "8", "5"),
    "c5_service_mux_logic_bypass": (
        "c5_service_mux_logic_inverters", "5", "2"
    ),
    "c5_service_reset_proof_bypass": (
        "c5_service_reset_proof_inverters", "5", "2"
    ),
}


class H6R2LocalityOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read_json(relative):
            return json.loads((ROOT / relative).read_text(encoding="utf-8"))

        cls.policy = read_json(
            "hardware/layout/h6-r2-placement-contract.json"
        )["placement_policy"]
        cls.boards = read_json(
            "hardware/layout/generated/H6-R2-placement-audit.json"
        )["boards"]
        cls.native_pins = {
            (row["instance"], row["physical"]): row
            for row in read_json(
                "hardware/ecad/generated/H2-R2-native-net-ledger.json"
            )["rows"]
        }

    def test_bypass_owners_are_explicit_and_match_the_electrical_review(self):
        owners = self.policy["locality_owner_overrides"]
        rows = {
            row["instance"]: row
            for board in self.boards
            for row in board["locality"]["rows"]
        }
        for child, (owner, _, _) in EXPECTED_OWNERS.items():
            with self.subTest(child=child):
                self.assertEqual(owner, owners.get(child))
                self.assertEqual(owner, rows[child]["owner"])

    def test_reviewed_bypasses_share_the_true_ic_supply_and_ground_pins(self):
        for child, (owner, supply_pad, ground_pad) in EXPECTED_OWNERS.items():
            with self.subTest(child=child):
                cap_supply = self.native_pins[(child, "1")]
                cap_ground = self.native_pins[(child, "2")]
                ic_supply = self.native_pins[(owner, supply_pad)]
                ic_ground = self.native_pins[(owner, ground_pad)]
                self.assertEqual(SUPPLY, cap_supply["net"])
                self.assertEqual(SUPPLY, ic_supply["net"])
                self.assertEqual(GROUND, cap_ground["net"])
                self.assertEqual(GROUND, ic_ground["net"])
                self.assertEqual("power", ic_supply["role"])
                self.assertEqual(cap_supply["project"], ic_supply["project"])
                self.assertIn(ic_supply["contact"], ("VCC", "VPOS"))

    def test_every_reviewed_owner_has_a_real_supply_pad_distance_constraint(self):
        for child, (owner, _, _) in EXPECTED_OWNERS.items():
            with self.subTest(child=child):
                pairs = [
                    row for row in self.policy["critical_pad_pairs"]
                    if row["canonical_net"] == SUPPLY
                    and {row["first_instance"], row["second_instance"]}
                    == {owner, child}
                ]
                self.assertEqual(1, len(pairs))
                self.assertGreater(pairs[0]["maximum_distance_mm"], 0.0)
                self.assertLessEqual(
                    pairs[0]["maximum_distance_mm"], MAXIMUM_PAD_DISTANCE_MM
                )

    def test_generated_native_pad_audit_meets_the_supply_distance_ceiling(self):
        all_pairs = [
            row for board in self.boards
            for row in board["critical_pad_pairs"]["rows"]
        ]
        for child, (owner, supply_pad, _) in EXPECTED_OWNERS.items():
            with self.subTest(child=child):
                pairs = [
                    row for row in all_pairs
                    if row["canonical_net"] == SUPPLY
                    and {row["first_instance"], row["second_instance"]}
                    == {owner, child}
                ]
                self.assertEqual(1, len(pairs))
                pair = pairs[0]
                endpoints = {
                    pair["first_instance"]: pair["first_pad"],
                    pair["second_instance"]: pair["second_pad"],
                }
                self.assertEqual("1", endpoints[child])
                self.assertEqual(supply_pad, endpoints[owner])
                self.assertLessEqual(
                    pair["maximum_distance_mm"], MAXIMUM_PAD_DISTANCE_MM
                )
                self.assertLessEqual(
                    pair["pad_centre_distance_mm"],
                    pair["maximum_distance_mm"],
                )

    def test_air_lna_bypass_targets_the_supply_side_of_its_bias_choke(self):
        child = "air_lna_rail_bypass"
        owner = "air_lna_bias_choke"
        supply = "3V3_AIR_SWITCHED"
        self.assertEqual(owner, self.policy["locality_owner_overrides"].get(child))
        for instance in (child, owner):
            self.assertEqual(supply, self.native_pins[(instance, "1")]["net"])
            self.assertEqual("END_1", self.native_pins[(instance, "1")]["contact"])
        self.assertEqual(
            "AIR_LNA_OUT_BIASED", self.native_pins[(owner, "2")]["net"]
        )

        declared = self.policy["critical_pad_pairs"]
        measured = [
            row for board in self.boards
            for row in board["critical_pad_pairs"]["rows"]
        ]
        for source, rows in (("contract", declared), ("native audit", measured)):
            with self.subTest(source=source):
                matches = [
                    row for row in rows
                    if row["canonical_net"] == supply
                    and {row["first_instance"], row["second_instance"]}
                    == {owner, child}
                ]
                self.assertEqual(1, len(matches))
                pair = matches[0]
                self.assertGreater(pair["maximum_distance_mm"], 0.0)
                self.assertLessEqual(
                    pair["maximum_distance_mm"], MAXIMUM_PAD_DISTANCE_MM
                )
                if source == "native audit":
                    endpoints = {
                        pair["first_instance"]: (pair["first_reference"], pair["first_pad"]),
                        pair["second_instance"]: (pair["second_reference"], pair["second_pad"]),
                    }
                    self.assertEqual(("L23", "1"), endpoints[owner])
                    self.assertEqual(("C167", "1"), endpoints[child])
                    self.assertLessEqual(
                        pair["pad_centre_distance_mm"], pair["maximum_distance_mm"]
                    )


if __name__ == "__main__":
    unittest.main()
