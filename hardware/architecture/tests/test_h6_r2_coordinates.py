"""Asymmetric fixtures distinguish RF world/native frames and double flips."""

from pathlib import Path
import subprocess
import unittest

from hardware.layout.h6_r2_coordinates import world_bbox_to_native


ROOT = Path(__file__).resolve().parents[3]
KICAD_PYTHON = Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3")


class NativeCoordinateTests(unittest.TestCase):
    def test_asymmetric_body_has_one_reflection_on_rf_only(self):
        original = {"x": [7.0, 13.0], "y": [21.0, 25.0], "z": [12.0, 16.0]}
        for frame in ("front-outer", "ui-inner", "ui-outer-face"):
            self.assertEqual(original, world_bbox_to_native(frame, original, 80))
        for frame in ("rear-outer", "rf-inner", "rear-inner", "rf-outer-face", "rf-outer-right-edge"):
            self.assertEqual({"x": [67.0, 73.0], "y": [21.0, 25.0], "z": [12.0, 16.0]},
                             world_bbox_to_native(frame, original, 80))
        projected = world_bbox_to_native("ui-inner", original, 80)
        projected["x"][0] = 100
        self.assertEqual([7.0, 13.0], original["x"])

    def test_board_width_is_not_hardcoded(self):
        self.assertEqual([87, 93], world_bbox_to_native("rf-inner", {"x": [7, 13], "y": [0, 2]}, 100)["x"])

    def test_unknown_frame_is_not_silently_treated_as_ui(self):
        with self.assertRaises(ValueError):
            world_bbox_to_native("display-assembly", {"x": [7, 13], "y": [0, 2]}, 80)

    def test_native_overrides_and_freeze_bypass_world_seed_projection(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad Python unavailable")
        code = r'''
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "hardware/layout"))
import h6_r2_placement as p
contract = p.load(p.CONTRACT_PATH)
coordinate = {"rows": [{"instance":"rf_fixture", "source_frame":"rf-inner", "world_bbox_mm":{"x":[7,13],"y":[21,25]}}]}
placement = {"placements":[{"id":"rf_replacement_r2", "kind":"fixed_body", "frame":"rf-inner", "world_xy_mm":[9,31], "size_mm":[5,4,1], "replaces":["rf_fixture"]}]}
small = {"board":{"width_mm":80},"instance_aliases":{"rf_alias":"rf_replacement_r2"}}
targets = p.build_target_index(small, placement, coordinate)
assert targets["rf_fixture"]["bbox"] == {"x":[66,71],"y":[31,35]}
assert targets["rf_alias"] == targets["rf_fixture"]
targets = p.build_target_index({"board":{"width_mm":80},"instance_aliases":{}}, {"placements":[]}, coordinate)
assert targets["rf_fixture"]["bbox"] == {"x":[67,73],"y":[21,25]}
# The already-correct M1 native pose is an override, NOT another world seed.
target = p.target_for_instance("LESHY2-RF-R2", "m1_rf_receptacle", "J12", contract, targets, {})
assert target["anchor"] == [37.5,122.25] and target["rotation"] == 180
# Likewise preserve a native freeze even when an unrelated H1 seed exists.
freeze = {("LESHY2-RF-R2","rf_fixture"): {"side":"B.Cu", "courtyard_centre_mm":[18,35], "footprint_anchor_nm":[18000000,35000000], "rotation_deg":90,"method":"test","courtyard_bbox_mm":{"x":[16,20],"y":[32,38]}}}
target = p.target_for_instance("LESHY2-RF-R2", "rf_fixture", "U999", contract, targets, freeze)
assert target["centre"] == [18,35] and target["exact_anchor_nm"] == [18000000,35000000]
assert target["frozen"]
print("world seeds normalized once; native overrides and frozen M1/anchors preserved")
'''
        result = subprocess.run([str(KICAD_PYTHON), "-c", code], cwd=ROOT, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("normalized once", result.stdout)


if __name__ == "__main__":
    unittest.main()
