import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h5_r2_current_routes.py"
SPEC = importlib.util.spec_from_file_location("h5_r2_current_routes", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class H5R2CurrentRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.build()

    def test_current_inventory_has_no_unmapped_route(self):
        self.assertEqual([], self.result["errors"])
        self.assertEqual(
            "reviewed_with_one_order_time_global_sourcing_gate",
            self.result["status"],
        )
        self.assertEqual(249, self.result["summary"]["component_groups"])
        self.assertEqual(1216, self.result["summary"]["component_articles"])
        self.assertEqual(209, self.result["summary"]["legacy_routes_reused"])
        self.assertEqual(40, self.result["summary"]["new_or_replaced_routes"])

    def test_only_wbc16_is_a_current_sourcing_gate(self):
        gates = [
            row for row in self.result["routes"]
            if row["route_class"] == "jlcpcb_global_sourcing_required"
        ]
        self.assertEqual(["WBC16-1TLC"], [row["mpn"] for row in gates])
        self.assertTrue(self.result["boundary"]["h6_may_continue"])
        self.assertFalse(self.result["boundary"]["order_release_may_continue"])

    def test_docs_expose_real_cost_and_gate(self):
        ru = MODULE.render_doc(self.result, True)
        self.assertIn("249 закупаемых групп / 1216 изделий", ru)
        self.assertIn("WBC16-1TLC", ru)
        self.assertIn("$449.70", ru)


if __name__ == "__main__":
    unittest.main()
