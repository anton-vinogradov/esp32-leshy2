import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/architecture/pack_safety_i2c_boundary.py"
SPEC = importlib.util.spec_from_file_location("pack_safety_i2c_boundary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PackSafetyI2CBoundaryTest(unittest.TestCase):
    def test_exact_boundary_closes_both_asymmetric_power_states(self):
        result = MODULE.build()
        self.assertEqual([], result["errors"])
        contract = result["contract"]
        self.assertEqual("H2-R2.0.3", result["marker"])
        self.assertEqual(("TCA9803DGKR", "C2687966"),
                         (contract["buffer"]["mpn"], contract["buffer"]["jlcpcb_part_number"]))
        truth = {(row["main"], row["aon"]): row["result"]
                 for row in contract["power_truth_table"]}
        self.assertIn("no Hub/main back-power", truth[(0, 1)])
        self.assertIn("no reverse power", truth[(1, 0)])

    def test_b_side_has_current_sources_and_no_external_pullups(self):
        contract = MODULE.load(MODULE.CONTRACT)
        self.assertEqual(0, contract["rail_local_termination"]["aon_b_side"]["external_pullup_quantity"])
        self.assertEqual(3.3, contract["buffer"]["electrical_contract"]["b_side_current_source_ma_typical"])
        self.assertEqual(400, contract["buffer"]["electrical_contract"]["b_side_capacitance_pf_max"])

        broken = copy.deepcopy(contract)
        broken["rail_local_termination"]["aon_b_side"]["external_pullup_quantity"] = 2
        self.assertIn("B-side must not contain external pull-ups",
                      MODULE.build(contract=broken)["errors"])

    def test_factory_route_and_exact_one_cost_are_complete(self):
        contract = MODULE.load(MODULE.CONTRACT)
        factory = contract["buffer"]["factory_surface"]
        self.assertEqual((1864, 1818, 1, 0.3525),
                         (factory["stock"], factory["available_order_quantity"],
                          factory["moq"], factory["unit_price_usd_quantity_1"]))
        self.assertEqual(0.3953, contract["exact_one_component_cost_usd"])

        broken = copy.deepcopy(contract)
        broken["buffer"]["factory_surface"]["stock"] = 0
        self.assertIn("TCA9803 factory route lacks positive stock",
                      MODULE.build(contract=broken)["errors"])

    def test_checked_in_generated_artifact_is_current(self):
        result = MODULE.build()
        self.assertEqual(MODULE.render(result), MODULE.OUTPUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
