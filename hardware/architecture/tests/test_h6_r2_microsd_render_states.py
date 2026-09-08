"""Exact DM3AT card-state references must not look like a protruding connector."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("microsd_state_renderer", ROOT / "hardware/layout/h6_r2_component_render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
MODEL = {"reference": "J5", "anchor_mm": [61.005, 140.075]}
# Independent current-native SVG fixture. These are only the three locked and
# five ejected/shared strokes; the unrelated body line must remain byte-identical.
PATHS = [
    "M66.4300 149.8000 L56.4300 149.8000",
    "M55.9300 149.3000 A0.5000 0.5000 0.0 0 0 56.4300 149.8000",
    "M66.4300 149.8000 A0.5000 0.5000 0.0 0 0 66.9300 149.3000",
    "M66.4300 153.8000 L56.4300 153.8000",
    "M55.9300 153.3000 A0.5000 0.5000 0.0 0 0 56.4300 153.8000",
    "M66.4300 153.8000 A0.5000 0.5000 0.0 0 0 66.9300 153.3000",
    "M55.9300 153.3000 L55.9300 148.4000",
    "M66.9300 148.4000 L66.9300 153.3000",
]
BODY = '<path d="M54.0800 132.2500 L67.9300 132.2500" />'

def fixture(paths=PATHS):
    return BODY + ''.join(f'<path d="{d}" />' for d in paths)


class MicroSDRenderStateTests(unittest.TestCase):
    def test_only_ejected_reference_strokes_are_dashed_and_body_is_unchanged(self):
        result = renderer.distinguish_microsd_card_states(fixture(), "inner", MODEL)
        self.assertIn(BODY, result)
        root = ET.fromstring('<svg>' + result + '</svg>')
        ejected = [p for p in root if p.get("data-card-state") == "ejected"]
        locked = [p for p in root if p.get("data-card-state") == "locked"]
        self.assertEqual(5, len(ejected))
        self.assertEqual(5, len(locked))  # three native + two exact short subsegments
        for path in ejected:
            self.assertIn("stroke-dasharray:0.7 0.45", path.get("style"))
        for path in locked:
            self.assertNotIn("dash", path.get("style", ""))
        self.assertEqual(set(PATHS[3:]), {p.get("d") for p in ejected})

    def test_missing_changed_or_duplicate_reference_stroke_fails_closed(self):
        for source in (fixture(PATHS[:-1]), fixture(PATHS + [PATHS[3]]),
                       fixture().replace("153.8000", "154.8000")):
            with self.assertRaisesRegex(RuntimeError, "changed or duplicated"):
                renderer.distinguish_microsd_card_states(source, "inner", MODEL)

    def test_outer_or_other_board_exports_are_not_broadly_restyled(self):
        source = fixture()
        self.assertEqual(source, renderer.distinguish_microsd_card_states(source, "outer", MODEL))
        self.assertEqual(source, renderer.distinguish_microsd_card_states(source, "inner", None))

    def model(self, *, footprint="microSD_HC_Hirose_DM3AT-SF-PEJM5", flipped=True, angle=180, count=1):
        fp = SimpleNamespace(GetReference=lambda: "J5", IsFlipped=lambda: flipped,
                             GetOrientationDegrees=lambda: angle,
                             GetPosition=lambda: SimpleNamespace(x=61.005, y=140.075),
                             GetFPID=lambda: SimpleNamespace(GetLibNickname=lambda: "Connector_Card",
                                                            GetLibItemName=lambda: footprint))
        board = SimpleNamespace(GetFootprints=lambda: [fp] * count)
        with patch.dict("sys.modules", {"pcbnew": SimpleNamespace(ToMM=lambda value: value)}):
            return renderer.microsd_reference_model(board)

    def test_rule_is_bound_to_exact_native_reference_package_side_and_pose(self):
        self.assertEqual(MODEL, self.model())
        for kwargs in ({"footprint": "other-card"}, {"flipped": False}, {"angle": 0}, {"count": 0}, {"count": 2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(RuntimeError):
                self.model(**kwargs)

    def test_callout_is_outside_pcb_readable_on_both_faces_and_not_silkscreen(self):
        for face in ("outer", "inner"):
            text = renderer.microsd_state_annotation(face, MODEL)
            root = ET.fromstring(text)
            self.assertEqual("true", root.get("data-not-silkscreen"))
            self.assertIn("card ejected / карта извлечена", ''.join(root.itertext()))
            self.assertIn("156.3000", text)
            self.assertEqual(face == "inner", "scale(-1 1)" in text)
        self.assertEqual("", renderer.microsd_state_annotation("inner", None))

    def test_reference_states_preserve_the_four_mm_nominal_travel(self):
        locked = renderer.microsd_state_paths(MODEL, "locked")[0]
        ejected = renderer.microsd_state_paths(MODEL, "ejected")[0]
        self.assertEqual(PATHS[0], locked)
        self.assertEqual(PATHS[3], ejected)
        self.assertAlmostEqual(4, float(ejected.split()[1]) - float(locked.split()[1]))


if __name__ == "__main__":
    unittest.main()
