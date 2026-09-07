import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_footprint_parity as audit


class FootprintParityTests(unittest.TestCase):
    def test_comparison_preserves_identical_numbered_pad_multiplicity(self):
        row = {"number": "SH", "at_mm": [1,2], "size_mm": [1,1]}
        result = audit.compare_pad_rows([row,row], [row])
        self.assertEqual([row], result["native_only"])
        self.assertEqual([], result["library_only"])

    def test_each_changed_geometry_field_is_detected(self):
        row = {"number":"1", "at_mm":[1,2], "size_mm":[1,1],
               "drill_mm":[0,0], "layers":[0], "shape":1, "attribute":0,
               "rotation_deg":0, "drill_shape":0, "roundrect_ratio":0}
        for field in row:
            changed = copy.deepcopy(row)
            changed[field] = "changed"
            with self.subTest(field=field):
                result = audit.compare_pad_rows([changed], [row])
                self.assertEqual([changed], result["native_only"])
                self.assertEqual([row], result["library_only"])

    def test_pad_order_is_not_a_geometry_difference(self):
        a, b = {"number":"1"}, {"number":"2"}
        self.assertEqual({"native_only":[],"library_only":[]},
                         audit.compare_pad_rows([a,b],[b,a]))

    def test_published_report_is_hash_bound_to_actual_native_boards(self):
        data = json.loads(audit.OUTPUT.read_text())
        self.assertEqual([], data["errors"])
        self.assertEqual(1216, data["summary"]["native_footprints"])
        self.assertEqual(1216, data["summary"]["checked_footprints"])
        for board in data["boards"]:
            self.assertEqual(board["board_sha256"], hashlib.sha256((ROOT/board["board"]).read_bytes()).hexdigest())
            self.assertEqual(board["native_footprint_count"], len(set(board["checked_references"])))

    def test_no_success_claim_when_stored_pad_deviations_exist(self):
        data = json.loads(audit.OUTPUT.read_text())
        count = sum(len(b["deviations"]) for b in data["boards"])
        self.assertEqual(count, data["summary"]["footprints_with_pad_geometry_drift"])
        self.assertEqual("open_native_library_drift" if count or data["errors"] else "pass", data["status"])
        self.assertFalse(data["fabrication_ready"])


if __name__ == "__main__":
    unittest.main()
