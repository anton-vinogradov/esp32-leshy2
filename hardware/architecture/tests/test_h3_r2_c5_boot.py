"""Exact C5 BOOT native chain; no runtime, mux or KILL qualification."""

import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    import pcbnew
except ImportError:
    pcbnew = None


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h3_r2_digital_interfaces.py"
# Independent physical-pin expectations, not copied from producer output/checks.
PINS = {
    "c5.GPIO28": ("U14", "15", "C5_BOOT_N"),
    "c5.GPIO27": ("U14", "18", "C5_GPIO27_FIXED_HIGH"),
    "c5_boot_pullup.END_1": ("R76", "1", "3V3_MAIN"),
    "c5_boot_pullup.END_2": ("R76", "2", "C5_BOOT_N"),
    "c5_dbg_boot_series.END_1": ("R79", "1", "C5_DBG_BOOT_CONNECTOR_N"),
    "c5_dbg_boot_series.END_2": ("R79", "2", "C5_BOOT_N"),
    "c5_gpio27_pullup.END_1": ("R90", "1", "3V3_MAIN"),
    "c5_gpio27_pullup.END_2": ("R90", "2", "C5_GPIO27_FIXED_HIGH"),
    "c5_boot_button.C1": ("SW18", "1", "C5_DBG_BOOT_CONNECTOR_N"),
    "c5_boot_button.C2": ("SW18", "3", "C5_DBG_BOOT_CONNECTOR_N"),
    "c5_boot_button.NO": ("SW18", "2", "POWER_GROUND"),
}


class C5BootNativeTopologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("c5_boot_digital", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.rows = cls.module.load(cls.module.NETS)["rows"]
        cls.instances = cls.module.load(cls.module.INSTANCES)["rows"]
        cls.devices = cls.module.load(cls.module.DEVICES)["devices"]

    def checks(self, rows=None, instances=None, devices=None):
        return self.module.c5_boot_topology_checks(
            self.rows if rows is None else rows,
            self.instances if instances is None else instances,
            self.devices if devices is None else devices)

    def test_actual_native_ledger_has_exact_complete_chain(self):
        for endpoint, (ref, physical, net) in PINS.items():
            with self.subTest(endpoint=endpoint):
                actual = [row for row in self.rows if row["endpoint"] == endpoint]
                self.assertEqual(1, len(actual))
                row = actual[0]
                self.assertEqual(("LESHY2-UI-R2", ref, physical, net, "connected"),
                                 tuple(row[key] for key in ("project", "reference", "physical", "net", "disposition")))
        result = self.checks()
        self.assertEqual(16, len(result))
        self.assertTrue(self.module.all_true(result), result)

    def test_any_missing_duplicate_or_disconnected_leg_fails_closed(self):
        for endpoint in PINS:
            for mutation in ("missing", "duplicate", "wrong_net", "nc"):
                with self.subTest(endpoint=endpoint, mutation=mutation):
                    rows = copy.deepcopy(self.rows)
                    row = next(row for row in rows if row["endpoint"] == endpoint)
                    if mutation == "missing":
                        rows.remove(row)
                    elif mutation == "duplicate":
                        rows.append(copy.deepcopy(row))
                    elif mutation == "wrong_net":
                        row["net"] = "3V3_AON"
                    else:
                        row["disposition"] = "no_connect"
                    self.assertIs(False, self.checks(rows=rows)["pin:" + endpoint])

    def test_pin_identity_cannot_be_replaced_by_same_named_label(self):
        for endpoint in PINS:
            for field, bad in (("project", "LESHY2-RF-R2"), ("reference", "U999"),
                               ("physical", "999"), ("instance", "other"),
                               ("contact", "OTHER"), ("device_id", "other")):
                with self.subTest(endpoint=endpoint, field=field):
                    rows = copy.deepcopy(self.rows)
                    next(row for row in rows if row["endpoint"] == endpoint)[field] = bad
                    self.assertIs(False, self.checks(rows=rows)["pin:" + endpoint])

    def test_component_identity_and_10k_1k_values_are_required(self):
        for instance in {endpoint.split(".")[0] for endpoint in PINS}:
            for mutation in ("missing", "duplicate", "excluded", "wrong_mpn", "wrong_kind"):
                with self.subTest(instance=instance, mutation=mutation):
                    instances = copy.deepcopy(self.instances)
                    devices = copy.deepcopy(self.devices)
                    row = next(row for row in instances if row["instance"] == instance)
                    if mutation == "missing":
                        instances.remove(row)
                    elif mutation == "duplicate":
                        instances.append(copy.deepcopy(row))
                    elif mutation == "excluded":
                        row["bom_excluded"] = True
                    elif mutation == "wrong_mpn":
                        row["mpn"] = devices[row["device_id"]]["mpn"] = "OTHER"
                    else:
                        devices[row["device_id"]]["kind"] = "100kohm_1pct_resistor"
                    self.assertIs(False, self.checks(instances=instances, devices=devices)["identity:" + instance])

    def test_device_contact_definition_must_agree_with_native_pin(self):
        devices = copy.deepcopy(self.devices)
        devices["esp32_c5_wroom_1u_n8r8"]["contacts"]["GPIO28"]["physical"] = "18"
        self.assertIs(False, self.checks(devices=devices)["pin:c5.GPIO28"])

    def test_gpio28_nc_prevents_acceptance_even_with_admitted_rails(self):
        rows = copy.deepcopy(self.rows)
        row = next(row for row in rows if row["endpoint"] == "c5.GPIO28")
        row.update(net=None, disposition="no_connect")
        original_load = self.module.load
        def fixture_load(path):
            return {"rows": rows} if path == self.module.NETS else original_load(path)
        with patch.object(self.module, "load", side_effect=fixture_load), \
                patch.object(self.module, "admits_current", return_value=True):
            result = self.module.build()
        self.assertEqual("fail", result["c5_boot_strap"]["topology_status"])
        self.assertEqual("review_required", result["status"])
        self.assertIs(False, result["current_analytical_scope_complete"])
        self.assertTrue(any("pin:c5.GPIO28" in error for error in result["provisional_numerical_errors"]))
        for language in ("en", "ru"):
            line = next(line for line in self.module.render(result, language).splitlines()
                        if line.startswith("| C5 BOOT |"))
            self.assertIn("| FAIL |", line)
            self.assertIn("pin:c5.GPIO28", line)
            self.assertNotIn("GPIO28/U14.15 → C5_BOOT_N", line)

    def test_render_rejects_inconsistent_or_empty_boot_checks_in_both_languages(self):
        original = self.module.build()
        for mutation in ("false_check", "empty_checks", "fail_status"):
            result = copy.deepcopy(original)
            boot = result["c5_boot_strap"]
            if mutation == "false_check":
                boot["checks"]["pin:c5.GPIO28"] = False
            elif mutation == "empty_checks":
                boot["checks"] = {}
            else:
                boot["topology_status"] = "fail"
            for language in ("en", "ru"):
                with self.subTest(mutation=mutation, language=language):
                    line = next(line for line in self.module.render(result, language).splitlines()
                                if line.startswith("| C5 BOOT |"))
                    self.assertIn("| FAIL |", line)
                    self.assertNotIn("GPIO28/U14.15 → C5_BOOT_N", line)

    def test_topology_pass_does_not_qualify_recovery_or_sampled_straps(self):
        result = self.module.build()
        boot = result["c5_boot_strap"]
        self.assertEqual("pass", boot["topology_status"])
        self.assertEqual({"GPIO27": 1, "GPIO28": 0}, boot["joint_download_boot_0_straps"])
        self.assertEqual(3, boot["hold_after_en_release_ms_min"])
        for field in ("sampled_levels_and_timing_qualified", "usb_mux_sel_oe_qualified",
                      "kill_recovery_policy_qualified", "end_to_end_download_qualified"):
            self.assertIs(False, boot[field])
        self.assertIs(False, result["authorization"]["fabrication"])
        self.assertIs(False, result["authorization"]["final_product_claim"])
        for language in ("en", "ru"):
            line = next(line for line in self.module.render(result, language).splitlines()
                        if line.startswith("| C5 BOOT |"))
            self.assertNotIn("| FAIL |", line)
            self.assertIn("GPIO28/U14.15 → C5_BOOT_N", line)

    @unittest.skipUnless(pcbnew, "Requires KiCad Python; read-only native pad check")
    def test_actual_ui_pads_match_the_physical_boot_chain(self):
        board = pcbnew.LoadBoard(str(ROOT / "hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb"))
        expected = {
            "U14": {"15": ["C5_BOOT_N"], "18": ["C5_GPIO27_FIXED_HIGH"]},
            "R76": {"1": ["3V3_MAIN"], "2": ["C5_BOOT_N"]},
            "R79": {"1": ["C5_DBG_BOOT_CONNECTOR_N"], "2": ["C5_BOOT_N"]},
            "R90": {"1": ["3V3_MAIN"], "2": ["C5_GPIO27_FIXED_HIGH"]},
            # Manufacturer common terminals 1/3 use two native lands numbered 1.
            "SW18": {"1": ["C5_DBG_BOOT_CONNECTOR_N"] * 2, "2": ["POWER_GROUND"]},
        }
        for ref, pins in expected.items():
            owners = [fp for fp in board.GetFootprints() if fp.GetReference() == ref]
            self.assertEqual(1, len(owners), ref)
            for physical, nets in pins.items():
                actual = sorted(str(pad.GetNetname()).rsplit("/", 1)[-1]
                                for pad in owners[0].Pads() if pad.GetNumber() == physical)
                self.assertEqual(sorted(nets), actual, (ref, physical))


if __name__ == "__main__":
    unittest.main()
