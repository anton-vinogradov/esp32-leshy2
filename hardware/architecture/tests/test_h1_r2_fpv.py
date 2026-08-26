import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/h1_r2_fpv.py"
SPEC = importlib.util.spec_from_file_location("h1_r2_fpv", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1R2FPVTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(MODULE.MODEL_PATH.read_text())
        cls.audit = MODULE.audit(cls.model)

    def test_functional_pin_and_power_fit_passes(self):
        self.assertEqual([], self.audit["errors"])
        self.assertTrue(self.audit["functional_and_pin_fit"])
        self.assertEqual(14, self.audit["pin_count"])
        self.assertEqual(150, self.audit["power_margin_ma"])

    def test_k331_uses_the_reserved_hub_controls(self):
        pins = {row["pin"]: row["owner"] for row in self.model["receiver"]["pinout"]}
        self.assertIn("GPIO36", pins[1])
        self.assertIn("GPIO37", pins[2])
        self.assertIn("GPIO38", pins[3])
        self.assertIn("GPIO34", pins[5])
        self.assertIn("GPIO33", pins[6])
        self.assertIn("GPIO35", self.model["receiver"]["decoder_lock_evidence"])

    def test_same_board_rf_path_has_no_ufl(self):
        path = " ".join(self.model["signal_path"])
        self.assertIn("direct 50-ohm PCB trace", path)
        self.assertIn("without U.FL or cable", path)

    def test_receiver_factory_and_physical_limits_fail_closed(self):
        receiver = self.model["receiver"]
        self.assertEqual({0}, {row["found"] for row in receiver["jlcpcb_surface"]["searches"]})
        self.assertFalse(receiver["jlcpcb_surface"]["accepted_for_factory_placement"])
        self.assertFalse(receiver["mechanical"]["accepted"])
        self.assertFalse(self.model["result"]["production_acceptance"])

    def test_exact_linear_mmcx_antenna_covers_k331(self):
        antenna = self.model["antenna"]
        self.assertEqual("TBS5G8MMCXA", antenna["mpn"])
        self.assertEqual("linear", antenna["polarization"])
        self.assertEqual("MMCX plug", antenna["termination"])
        self.assertEqual("FPV · RX 5.8G", antenna["printed_identity"])
        self.assertTrue(antenna["accepted"])
        alternate = antenna["supply_independent_alternate"]
        self.assertEqual("FXP831.09.0100C", alternate["mpn"])
        self.assertEqual([4900, 6000], alternate["frequency_mhz"])
        self.assertTrue(alternate["termination"].startswith("MMCX male"))
        self.assertEqual(0, alternate["jlcpcb_exact_search_found"])

    def test_generated_artifacts_are_current(self):
        for path, content in MODULE.outputs(self.model).items():
            self.assertTrue(path.exists(), path)
            self.assertEqual(content, path.read_text(), path)


if __name__ == "__main__":
    unittest.main()
