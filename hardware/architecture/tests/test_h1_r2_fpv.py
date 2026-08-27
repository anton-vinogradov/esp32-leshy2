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

    def test_official_k331_media_closes_functional_integration_only(self):
        evidence = self.model["receiver"]["official_integration_evidence"]
        self.assertEqual(
            {"application_circuit", "channel_table", "pinout"},
            set(self.audit["official_integration_evidence"]),
        )
        for key in ("application_circuit", "pinout", "channel_table"):
            self.assertIn("akktek.com/media/catalog/product/", evidence[key])
        self.assertIn("maximum body dimensions", evidence["does_not_cover"])
        self.assertFalse(self.model["receiver"]["mechanical"]["accepted"])

    def test_k331_nominal_xy_is_not_overstated_as_a_controlled_body(self):
        mechanical = self.model["receiver"]["mechanical"]
        self.assertEqual([28.7, 23.1], mechanical["nominal_board_xy_mm"])
        self.assertEqual([30.0, 24.0, 4.0], mechanical["working_envelope_mm"])
        self.assertIn("reseller", mechanical["nominal_board_xy_source_class"])
        self.assertFalse(mechanical["accepted"])

    def test_awm666v_is_a_controlled_but_degraded_fallback(self):
        alternatives = {row["mpn"]: row for row in self.model["receiver_alternatives_reviewed"]}
        fallback = alternatives["AWM666V RX"]
        self.assertEqual([26.16, 16.38, 3.7], fallback["controlled_envelope_mm"])
        self.assertTrue(fallback["controlled_land_pattern"])
        self.assertTrue(fallback["fits_k331_working_envelope"])
        self.assertEqual(7, fallback["channel_count"])
        self.assertEqual(0, fallback["jlcpcb_surface"]["placeable_hits"])
        self.assertIn("CH7", fallback["datasheet_inconsistency"])

    def test_receiver_factory_and_physical_limits_fail_closed(self):
        receiver = self.model["receiver"]
        self.assertEqual({0}, {row["placeable_hits"] for row in receiver["jlcpcb_surface"]["searches"]})
        self.assertFalse(receiver["jlcpcb_surface"]["accepted_for_factory_placement"])
        self.assertFalse(receiver["mechanical"]["accepted"])
        self.assertFalse(self.model["result"]["production_acceptance"])
        self.assertEqual(8, self.audit["receiver_alternatives_reviewed"])
        alternatives = {row["mpn"]: row for row in self.model["receiver_alternatives_reviewed"]}
        self.assertGreater(alternatives["AWM682 RX"]["controlled_envelope_mm"][1], 23.0)
        self.assertGreater(alternatives["TUE-RFVRX-58-D"]["maximum_current_ma"], 350)
        sp166rx = alternatives["SP166RX"]
        self.assertEqual([42.418, 29.46], sp166rx["controlled_board_xy_mm"])
        self.assertGreater(sp166rx["controlled_board_xy_mm"][0], 30.0)
        self.assertGreater(sp166rx["controlled_board_xy_mm"][1], 24.0)
        self.assertEqual(0, sp166rx["jlcpcb_surface"]["placeable_hits"])
        self.assertIn("contradict", sp166rx["result"])
        mm238r = alternatives["MM238R-MCU"]
        self.assertEqual([28.0, 23.0, 3.0], mm238r["working_envelope_mm"])
        self.assertFalse(mm238r["controlled_mechanical_drawing"])
        self.assertIn("discontinued", mm238r["availability"])
        self.assertEqual(0, mm238r["jlcpcb_surface"]["placeable_hits"])
        rtc = alternatives["RichWave RTC6715 IC"]
        self.assertEqual("C7464354", rtc["jlcpcb_part"])
        self.assertEqual("RichWave", rtc["jlcpcb_surface"]["manufacturer"])
        self.assertEqual(0, rtc["jlcpcb_surface"]["stock"])
        self.assertEqual(442, rtc["jlcpcb_surface"]["minimum"])
        self.assertIn("without a public reference application", rtc["datasheet_status"])
        rx5808 = alternatives["generic RX5808"]
        self.assertEqual("C9900139392", rx5808["jlcpcb_part"])
        self.assertEqual(0, rx5808["jlcpcb_surface"]["stock"])
        self.assertEqual(0, self.audit["jlcpcb_placeable_hits"])

    def test_supplier_responses_preserve_the_remaining_gate(self):
        outreach = self.model["supplier_outreach"]
        self.assertEqual("2026-08-27", outreach["sent_on"])
        self.assertEqual({"akk", "jlcpcb"}, set(outreach) - {"sent_on"})
        self.assertEqual(["akk"], self.audit["supplier_responses_pending"])
        self.assertIn("response received", outreach["jlcpcb"]["status"])
        self.assertTrue(self.model["receiver"]["jlcpcb_surface"]["consigned_parts_route"]["selected"])
        self.assertFalse(self.model["result"]["production_acceptance"])

    def test_only_present_blockers_are_owned_by_h1(self):
        blockers = self.model["current_h1_blockers"]
        downstream = self.model["downstream_verification"]
        self.assertEqual(1, len(blockers))
        self.assertTrue(any("AKK-controlled" in row for row in blockers))
        self.assertEqual({"H5/H6/H7", "H3/H6/H8", "H5/H8"}, {row["stage"] for row in downstream})
        self.assertEqual(blockers, self.audit["current_h1_blockers"])
        self.assertEqual(downstream, self.audit["downstream_verification"])

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
