"""Bounded procurement/electrical admission for the approved USB family merge."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "hardware/verification/jlcpcb-usb-unification-2026-09-09.json"


class USBUnificationFactoryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads(EVIDENCE.read_text())

    def test_exact_family_and_standard_pcba_route(self):
        part = self.evidence["part"]
        self.assertEqual("USB4105-GF-A", part["mpn"])
        self.assertEqual("Global Connector Technology", part["manufacturer"])
        self.assertEqual("C3020560", part["jlcpcb_part_number"])
        self.assertEqual("SMT Assembly", part["assembly_type"])
        self.assertIn("Standard", part["pcba_type"])
        self.assertEqual("Extended", part["library_type"])
        self.assertEqual("High", part["assembly_difficulty"])

    def test_stock_is_not_misrepresented_as_direct_moq_one(self):
        part = self.evidence["part"]
        self.assertEqual("Pre-order", part["purchase_action_displayed"])
        self.assertEqual(1044, part["stock_displayed"])
        self.assertEqual(9, part["minimum_purchase_quantity"])
        self.assertEqual(4, part["proposed_fitted_quantity_per_product"])
        self.assertEqual(4, part["current_fitted_quantity_of_this_mpn"])
        self.assertEqual(3, part["fitted_quantity_before_unification"])
        self.assertIn("not_production_release", self.evidence["status"])
        self.assertEqual(5, part["minimum_purchase_surplus_before_factory_attrition"])
        self.assertEqual(1.0656, part["estimated_unit_price_usd"])
        self.assertAlmostEqual(9.59, round(9 * part["estimated_unit_price_usd"], 2))
        self.assertIn("factory attrition allowance", part["not_included_in_estimate"])
        self.assertIn("2026-09-08T21:51:23Z", self.evidence["checked_at_utc"])
        self.assertEqual("го", self.evidence["user_confirmation"]["answer"])
        self.assertIn("USB4105-GF-A", self.evidence["user_confirmation"]["exact_question"])

    def test_connector_rating_does_not_enlarge_product_power_profiles(self):
        source = json.loads((ROOT / "hardware/verification/h3-r2-source-margin-contract.json").read_text())
        rating = self.evidence["manufacturer_crosscheck"]
        self.assertEqual(5, rating["vbus_collective_current_a"])
        self.assertEqual(48, rating["voltage_rating_v"])
        self.assertEqual(16, rating["mating_contacts"])
        self.assertEqual(12, rating["shared_solder_positions"])
        self.assertEqual(4, rating["through_hole_shell_stakes"])
        self.assertEqual(0.95, rating["shell_stake_length_mm"])
        profiles = source["usb_profiles"]
        self.assertEqual({"USB_ABSENT", "USB_5V_FALLBACK", "USB_5V_3A", "USB_9V_3A", "USB_15V_2A"}, set(profiles))
        self.assertIsNone(profiles["USB_5V_FALLBACK"]["current_limit_a"])
        self.assertEqual(3, max(p["current_limit_a"] or 0 for p in profiles.values()))
        self.assertEqual(15, max(p["voltage_v"] for p in profiles.values()))
        self.assertLess(3, rating["vbus_collective_current_a"])
        self.assertLess(15, rating["voltage_rating_v"])
        self.assertEqual("usb_support", source["ownership_rules"]["SOURCE_OVERHEAD"]["gct_usb4105_gf_a"])
        # This test admits connector ratings, not negotiated power, contact
        # sharing, routed losses, plug-overmould fit or whole-device readiness.


if __name__ == "__main__":
    unittest.main()
