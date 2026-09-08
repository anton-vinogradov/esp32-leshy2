"""The product preview is derived from current native views, never old H1 poses."""
import importlib.util
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_product_view.py"
SPEC = importlib.util.spec_from_file_location("product_view", SCRIPT)
VIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEW)


class ProductViewTests(unittest.TestCase):
    def evidence(self):
        views = {"status": "current_native_visualization_not_assembly_approval",
                 "inputs_sha256": dict.fromkeys(VIEW.EXPECTED_VIEW_INPUTS, "a"*64),
                 "outputs_sha256": dict.fromkeys(VIEW.EXPECTED_VIEW_OUTPUTS, "a"*64)}
        intent = {"schema_version": 1, "status": "pass", "failed_requirements": [],
                  "sources": dict.fromkeys(VIEW.EXPECTED_INTENT_SOURCES, "a"*64),
                  "checks": [{"requirement": f"independent requirement {n}", "pass": True}
                             for n in range(19)]}
        return views, intent

    def test_failed_intent_cannot_publish_a_corrected_mockup(self):
        views, intent = self.evidence()
        intent["status"] = "fail"
        with self.assertRaisesRegex(ValueError, "placement intent fails"):
            VIEW.validate_evidence(views, intent)

    def test_complete_evidence_rehashes_every_required_source_and_output(self):
        with patch.object(VIEW, "sha", return_value="a"*64) as digest:
            VIEW.validate_evidence(*self.evidence())
        self.assertEqual(13, digest.call_count)  # 3 component inputs +5 SVG +5 intent inputs
        checked = {str(call.args[0].relative_to(ROOT)) for call in digest.call_args_list}
        self.assertTrue(set(VIEW.BOARD_PATHS.values()) <= checked)

    def test_empty_truncated_or_extra_hash_inventory_fails_before_any_path_read(self):
        for section in ("inputs_sha256", "outputs_sha256", "sources"):
            for mutation in ("empty", "truncated", "extra"):
                views, intent = self.evidence()
                record = intent if section == "sources" else views
                if mutation == "empty":
                    record[section] = {}
                elif mutation == "truncated":
                    record[section].pop(next(iter(record[section])))
                else:
                    record[section]["../../outside-scope"] = "a"*64
                with self.subTest(section=section, mutation=mutation), patch.object(VIEW, "sha") as digest:
                    with self.assertRaisesRegex(ValueError, "inventory"):
                        VIEW.validate_evidence(views, intent)
                    digest.assert_not_called()

    def test_invalid_hash_format_and_stale_native_hash_are_rejected(self):
        views, intent = self.evidence()
        intent["sources"][VIEW.BOARD_PATHS["rf"]] = True
        with patch.object(VIEW, "sha") as digest:
            with self.assertRaisesRegex(ValueError, "invalid source digest"):
                VIEW.validate_evidence(views, intent)
            digest.assert_not_called()
        with patch.object(VIEW, "sha", return_value="b"*64):
            with self.assertRaisesRegex(ValueError, "stale native"):
                VIEW.validate_evidence(*self.evidence())

    def test_empty_truncated_duplicate_failed_or_nonboolean_checks_cannot_turn_green(self):
        for mutation in ("empty", "truncated", "duplicate", "failed", "int-true",
                         "false", "blank", "schema-bool"):
            views, intent = self.evidence()
            if mutation == "empty": intent["checks"] = []
            elif mutation == "truncated": intent["checks"].pop()
            elif mutation == "duplicate": intent["checks"][-1] = copy.deepcopy(intent["checks"][0])
            elif mutation == "failed": intent["failed_requirements"] = ["a real failure"]
            elif mutation == "int-true": intent["checks"][0]["pass"] = 1
            elif mutation == "false": intent["checks"][0]["pass"] = False
            elif mutation == "blank": intent["checks"][0]["requirement"] = " "
            elif mutation == "schema-bool": intent["schema_version"] = True
            with self.subTest(mutation=mutation), patch.object(VIEW, "sha") as digest:
                with self.assertRaises(ValueError):
                    VIEW.validate_evidence(views, intent)
                digest.assert_not_called()

    def test_duplicate_raw_json_keys_are_not_silently_overwritten(self):
        with self.assertRaisesRegex(ValueError, "duplicate manifest key"):
            json.loads('{"sources":{"same":"old","same":"new"}}', object_pairs_hook=VIEW.unique_object)

    def test_outer_faces_retain_native_identity_and_exact_common_viewport(self):
        views, _ = self.evidence()
        attrs = {"viewBox": "0 0 96 190", "data-board": "rf", "data-face": "outer",
                 "data-source-sha256": "a"*64, "data-renderer-sha256": "a"*64}
        VIEW.validate_outer_view(ET.Element(VIEW.NS+"svg", attrs), "rf", views)
        for key, value in (("viewBox", "0 0 192 190"), ("data-board", "ui"),
                           ("data-face", "inner"), ("data-source-sha256", "b"*64)):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "identity, scale or source"):
                VIEW.validate_outer_view(ET.Element(VIEW.NS+"svg", {**attrs, key: value}), "rf", views)

    def test_current_preview_is_reproducible_and_uses_both_native_outer_faces(self):
        if not VIEW.OUTPUT.exists():
            self.skipTest("generated after joint native placement integration")
        svg, manifest = VIEW.build()
        self.assertEqual(VIEW.OUTPUT.read_text(), svg)
        self.assertEqual(VIEW.MANIFEST.read_text(), manifest)
        root = ET.fromstring(svg)
        panels = [node for node in root if node.get("data-board")]
        self.assertEqual(["ui", "rf"], [node.get("data-board") for node in panels])
        self.assertEqual(["translate(0 15)", "translate(96 15)"], [node.get("transform") for node in panels])
        self.assertNotIn("h1-r2", manifest)
        overlays = [node for node in root.iter() if node.get("data-role") == "nominal-display-panel-envelope"]
        self.assertEqual(1, len(overlays))
        self.assertIn("Native positions", svg)

    def test_landing_uses_current_preview_and_keeps_h1_only_as_archive_link(self):
        for name in ("README.md", "README.ru.md"):
            page = (ROOT/name).read_text()
            self.assertIn("docs/images/h6-r2-product-exterior.svg", page)
            self.assertNotIn("![H1 concept", page)
            self.assertNotIn("![Концептуальный", page)
            self.assertIn("h1-r2-four-faces.svg", page)


if __name__ == "__main__":
    unittest.main()
