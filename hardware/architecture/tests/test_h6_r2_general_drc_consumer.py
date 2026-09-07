"""Live general-routing checks must not reuse PCB-only / parity-absent evidence."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Requires KiCad Python")
class GeneralDrcConsumerTests(unittest.TestCase):
    def test_live_import_requires_full_provenance_before_counts(self):
        import h6_r2_general_routing as general
        with patch.object(general, "validate_provenance", side_effect=ValueError("missing parity receipt")) as validator:
            with self.assertRaisesRegex(ValueError, "missing parity"):
                general.drc_evidence(Path("unused.json"), "LESHY2-RF-R2", "fake")
            validator.assert_called_once()

    def test_live_retained_board_hash_alone_is_not_evidence(self):
        import h6_r2_general_routing as general
        evidence = {"checked_board_sha256": "same", "violation_count": 0,
                    "schematic_parity_error_count": 0}
        existing = {"boards": [{"project": "LESHY2-RF-R2", "drc": evidence}]}
        _, errors = general.retained_drc_evidence(existing, "LESHY2-RF-R2", "same")
        self.assertTrue(any("provenance" in e for e in errors))

    def test_live_retained_validation_errors_are_not_suppressed(self):
        import h6_r2_general_routing as general
        evidence = {"checked_board_sha256": "same", "violation_count": 0,
                    "schematic_parity_error_count": 0, "report_sha256": "report", "provenance": {"receipt": "x"}}
        existing = {"boards": [{"project": "LESHY2-RF-R2", "drc": evidence}]}
        with patch.object(general, "validate_receipt", side_effect=ValueError("schematic changed")) as validator:
            _, errors = general.retained_drc_evidence(existing, "LESHY2-RF-R2", "same")
            self.assertEqual(["schematic changed"], errors)
            validator.assert_called_once_with(evidence["provenance"], "LESHY2-RF-R2", "report")


if __name__ == "__main__":
    unittest.main()
