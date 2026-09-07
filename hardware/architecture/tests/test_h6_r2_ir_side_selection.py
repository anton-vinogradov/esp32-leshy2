"""The TR substitution must preserve carrier learning, not demodulate it."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


class IRSideSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.devices = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"]

    def test_same_physical_contacts_and_electrical_function(self):
        old, new = self.devices["vishay_tsmp95000tt"], self.devices["vishay_tsmp95000tr"]
        self.assertEqual(old["contacts"], new["contacts"])
        self.assertEqual({k:v for k,v in old["electrical_contract"].items() if k!="taping"},
                         {k:v for k,v in new["electrical_contract"].items() if k!="taping"})
        self.assertEqual([30,60], new["electrical_contract"]["carrier_range_khz"])
        self.assertIn("side-view", new["electrical_contract"]["taping"])

    def test_preorder_cost_is_not_a_one_piece_stock_claim(self):
        route = self.devices["vishay_tsmp95000tr"]["orderable_source"]
        self.assertEqual("C20593617", route["jlc_number"])
        self.assertEqual("SMT Assembly", route["assembly_type"])
        self.assertIn("Standard", route["pcba_type"])
        self.assertEqual(5, route["minimum_preorder_quantity"])
        self.assertAlmostEqual(route["minimum_component_subtotal_usd"], 5*route["unit_price_usd_at_minimum"])

    def test_current_overrides_are_side_view_and_historical_entry_survives(self):
        self.assertIn("vishay_tsmp95000tt", self.devices)
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text())
        for mpn in ("Vishay TSMP95000TR", "Vishay TSOP75238TR"):
            self.assertEqual("Leshy2:Vishay-Heimdall-SMD-TR", contract["footprint_overrides"][mpn])
        model = json.loads((ROOT / "hardware/product-design/h1-r2-cost-review.json").read_text())
        self.assertEqual("vishay_tsmp95000tr", model["r2_device_replacements"]["vishay_tsmp95000tt"]["device_id"])


if __name__ == "__main__":
    unittest.main()
