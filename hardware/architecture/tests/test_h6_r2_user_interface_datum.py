"""Visible indicators must not fall into automatic inner-face electronics packing."""

import __future__
import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_placement.py"
EXPECTED = {
    "s3_tx_led": (8.4, 104.9), "c5_tx_led": (24.2, 104.9),
    "nrf0_tx_led": (40.0, 104.9), "nrf1_tx_led": (55.8, 104.9),
    "nrf2_tx_led": (71.6, 104.9), "cc_tx_led": (8.4, 111.4),
    "voice_tx_led": (24.2, 111.4), "ir_tx_led": (40.0, 111.4),
    "ext_tx_led": (55.8, 111.4), "fault_led": (71.6, 111.4),
}


def gap(a, b):
    dx = max(a["x"][0] - b["x"][1], b["x"][0] - a["x"][1], 0)
    dy = max(a["y"][0] - b["y"][1], b["y"][0] - a["y"][1], 0)
    return (dx * dx + dy * dy) ** 0.5


class UserInterfaceDatumTests(unittest.TestCase):
    def setUp(self):
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result and key in EXPECTED:
                    raise ValueError(f"duplicate user-indicator placement-contract key: {key}")
                result[key] = value
            return result
        self.contract = json.loads(
            (ROOT / "hardware/layout/h6-r2-placement-contract.json").read_text(),
            object_pairs_hook=unique_object,
        )
        self.tree = ast.parse(SCRIPT.read_text())
        selected = [node for node in self.tree.body if isinstance(node, ast.FunctionDef)
                    and node.name in {"service_button_target", "target_for_instance", "target_side"}]
        self.fn = {}
        # Preserve the source module's postponed annotations when extracting its AST.
        exec(compile(ast.Module(body=selected, type_ignores=[]), str(SCRIPT), "exec",
                     flags=__future__.annotations.compiler_flag, dont_inherit=True), self.fn)

    def test_exact_ten_user_indicators_are_explicit_outer_face_datums(self):
        ledger = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json").read_text())
        leds = {row["instance"]: row for row in ledger["rows"]
                if row["device_id"] in {"liteon_ltst_c190krkt", "liteon_ltst_c190kfkt"}}
        self.assertEqual(set(EXPECTED), set(leds))
        for instance, centre in EXPECTED.items():
            with self.subTest(instance=instance):
                self.assertEqual("LESHY2-UI-R2", leds[instance]["project"])
                override = self.contract["placement_overrides"][instance]
                self.assertEqual("front-outer", override["frame"])
                self.assertEqual(list(centre), override["centre_mm"])
                self.assertEqual(0, override["rotation_deg"])
                self.assertEqual("reviewed outward user-indicator datum", override["method"])

    def test_centre_conversion_preserves_accepted_h1_outward_body_positions(self):
        accepted = json.loads((ROOT / "hardware/product-design/generated/H1-external-face-acceptance.json").read_text())["front"]
        rows = accepted["tx_indicators"] + accepted["status_indicators"]
        self.assertEqual(set(EXPECTED), {row["instance"] for row in rows})
        for row in rows:
            # H1 draws body rectangles from top-left; native LED_0603 anchor
            # and courtyard are centred. No R2 LED transform occurs in the renderer.
            x, y = row["position_mm"]
            actual = self.contract["placement_overrides"][row["instance"]]["centre_mm"]
            self.assertAlmostEqual(x + 0.8, actual[0])
            self.assertAlmostEqual(y + 0.4, actual[1])

    def test_wrong_inner_frozen_pose_cannot_override_visible_face(self):
        for instance, centre in EXPECTED.items():
            frozen = {("LESHY2-UI-R2", instance): {
                "side": "B.Cu", "rotation_deg": 90, "courtyard_centre_mm": [30, 80],
                "method": "automatic hidden electronics", "courtyard_bbox_mm": {"x": [29, 31], "y": [79, 81]},
            }}
            target = self.fn["target_for_instance"](
                "LESHY2-UI-R2", instance, "D_TEST", self.contract, {}, frozen
            )
            self.assertEqual("F.Cu", self.fn["target_side"](target))
            self.assertEqual(list(centre), target["centre"])
            self.assertEqual(0, target["rotation"])
            self.assertNotIn("frozen", target)

    def test_reviewed_method_really_prevents_automatic_repacking(self):
        # Evaluate the real entry-setup hard-lock expression. This catches
        # removing its placement_method clause without importing native KiCad.
        expression = next(
            node.value for node in ast.walk(self.tree)
            if isinstance(node, ast.Assign) and len(node.targets) == 1
            and ast.unparse(node.targets[0]) == "entry['hard']"
        )
        for instance in EXPECTED:
            target = self.fn["target_for_instance"]("LESHY2-UI-R2", instance, "D_TEST", self.contract, {}, {})
            namespace = {"target": target, "entry": {"row": {"instance": instance}}, "hard_locked": set()}
            self.assertTrue(eval(compile(ast.Expression(expression), str(SCRIPT), "eval"), namespace))
            target["placement_method"] = None
            self.assertFalse(eval(compile(ast.Expression(expression), str(SCRIPT), "eval"), namespace))

    def test_full_led_courtyards_clear_panel_controls_and_opposite_face_holes(self):
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())
        board = next(row for row in audit["boards"] if row["project"] == "LESHY2-UI-R2")
        obstacles = [("display", self.contract["mechanical"]["display_bed"]["panel_bbox_mm"])]
        for row in board["placements"]:
            if row["instance"] in EXPECTED:
                continue
            if row["side"] == "F.Cu":
                obstacles.append((row["instance"], row["courtyard_bbox_mm"]))
            else:
                obstacles.extend((row["instance"] + ":opposite", box)
                                 for box in row["opposite_face_keepout_bboxes_mm"])
        for instance, (x, y) in EXPECTED.items():
            # Exact LED_0603_1608Metric native courtyard including line stroke.
            courtyard = {"x": [x - 1.525, x + 1.525], "y": [y - 0.775, y + 0.775]}
            for owner, box in obstacles:
                with self.subTest(instance=instance, obstacle=owner):
                    self.assertGreaterEqual(gap(courtyard, box), 0.1)


if __name__ == "__main__":
    unittest.main()
