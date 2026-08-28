import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/architecture/r2_authority.py"
SPEC = importlib.util.spec_from_file_location("r2_authority", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class R2AuthorityTest(unittest.TestCase):
    def test_current_h0_has_six_domains_two_rps_and_exact_m1(self):
        result = MODULE.build()
        self.assertEqual([], result["errors"])
        self.assertEqual(6, result["current_h0"]["domain_count"])
        self.assertEqual({"hub_rp", "rf_rp"}, set(result["current_h0"]["rp_domain_ids"]))
        self.assertEqual(80, result["current_h0"]["m1_contacts"])
        self.assertEqual(14, result["current_h0"]["m1_reserve_contacts"])

    def test_historical_h2_is_single_rp_old_m1_and_not_current(self):
        result = MODULE.build()
        historical = result["historical_r1_h2"]
        self.assertEqual("historical_only_not_r2", historical["authority"])
        self.assertEqual(5, historical["domain_count"])
        self.assertEqual(["rp"], historical["rp_instances"])
        self.assertEqual(51, historical["m1_unique_nets"])
        self.assertEqual(0, historical["m1_reserve_contacts"])
        self.assertFalse(result["r2_h2_authoritative"])
        self.assertFalse(result["r2_kicad_started"])

    def test_false_current_r2_claim_fails_closed(self):
        policy = copy.deepcopy(MODULE.load(MODULE.POLICY))
        policy["current_r2_h2_export"] = True
        result = MODULE.build(policy=policy)
        self.assertIn(
            "current-R2 H2 claim is forbidden while the generated export is single-RP/old-M1",
            result["errors"],
        )

    def test_r2_kicad_start_also_fails_closed(self):
        policy = copy.deepcopy(MODULE.load(MODULE.POLICY))
        policy["r2_kicad_started"] = True
        result = MODULE.build(policy=policy)
        self.assertIn(
            "R2 KiCad cannot start before the generated H2 export matches H0-R2",
            result["errors"],
        )

    def test_h1_and_h5_use_two_rps_per_device_and_ten_for_evt5(self):
        import json

        placement = json.loads(
            (ROOT / "hardware/product-design/h1-r2-placement.json").read_text(encoding="utf-8")
        )
        factory = next(row for row in placement["factory_evidence"] if row["mpn"] == "SC1512-A4")
        self.assertEqual(("C39843328", 2, 10), (
            factory["jlcpcb_part"], factory["quantity_per_device"], factory["evt5_quantity"]
        ))

        from hardware.verification import h5_pcba_platform

        overlay = h5_pcba_platform.build()["r2_quantity_overlay"]
        self.assertEqual(("J0", "C39843328", 2, 10), (
            overlay["route"], overlay["jlcpcb_part"],
            overlay["quantity_per_device"], overlay["evt5_quantity"]
        ))


if __name__ == "__main__":
    unittest.main()
