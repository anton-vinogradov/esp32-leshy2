import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/g3_clamshell.py"
SPEC = importlib.util.spec_from_file_location("g3_clamshell_cap_register", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
import sys
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class H1CapEvidenceRegisterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.devices, _, cls.instances, *_ = MODULE.load()

    def test_exact_current_g2f_manifest_resolves_once_with_courtyards(self):
        audit = MODULE.cap_evidence_coordinate_register_audit(
            self.devices, self.instances
        )
        self.assertEqual("pass", audit["status"])
        self.assertEqual(43, audit["expected_instance_count"])
        self.assertEqual(43, audit["resolved_instance_count"])
        self.assertEqual([], audit["errors"])
        for row in audit["instances"]:
            width, height = row["source_envelope_mm"]
            courtyard = row["placement_courtyard_bbox_mm"]
            self.assertAlmostEqual(width + 0.7, courtyard["x"][1] - courtyard["x"][0])
            self.assertAlmostEqual(height + 0.7, courtyard["y"][1] - courtyard["y"][0])

    def test_device_substitution_fails_closed(self):
        broken = dict(self.instances)
        broken["u214_esd_a"] = self.instances["u214_esd_b"] + "-mutated"
        audit = MODULE.cap_evidence_coordinate_register_audit(self.devices, broken)
        self.assertEqual("fail", audit["status"])
        self.assertTrue(any("u214_esd_a expected current G2F device" in row for row in audit["errors"]))

    def test_missing_or_duplicate_coordinate_fails_closed(self):
        without_esd = tuple(
            (frame, tuple(item for item in items if item.instance != "u214_esd_a"))
            for frame, items in MODULE.PLACEMENT_PROJECTION_GROUPS
        )
        audit = MODULE.cap_evidence_coordinate_register_audit(
            self.devices, self.instances, without_esd
        )
        self.assertTrue(any("u214_esd_a has 0 physical projections" in row for row in audit["errors"]))

        duplicate_esd = tuple(MODULE.PLACEMENT_PROJECTION_GROUPS) + (
            ("rf-inner", (next(item for item in MODULE.RF_INNER if item.instance == "u214_esd_a"),)),
        )
        audit = MODULE.cap_evidence_coordinate_register_audit(
            self.devices, self.instances, duplicate_esd
        )
        self.assertTrue(any("u214_esd_a has 2 physical projections" in row for row in audit["errors"]))


if __name__ == "__main__":
    unittest.main()
