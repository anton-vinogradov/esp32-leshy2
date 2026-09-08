"""Check the immutable 9 September inventory audit, not replacement approval."""

import ast
import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
BASE = "33908f003f2e622119de197056ed8ef70ddeeb2d"


class ComponentDiversityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / "hardware/verification"
        cls.active = json.loads((folder / "h6-r2-component-diversity-nonpassive-2026-09-09.json").read_text())
        cls.passive = json.loads((folder / "h6-r2-component-diversity-passive-2026-09-09.json").read_text())

    def test_inventory_union_covers_the_complete_recorded_baseline(self):
        self.assertEqual(BASE, self.active["base_commit"])
        self.assertEqual(BASE, self.passive["snapshot"]["head"])
        identifiers = set()
        devices = set()
        for group in self.active["screened_inventory"]:
            self.assertEqual(group["count"], len(group["instances"]))
            devices.add(group["device_id"])
            identifiers.update((p["project"], p["reference"]) for p in group["instances"])
        for key, group in self.passive["inventory"].items():
            self.assertEqual(group["count"], len(group["occurrences"]))
            self.assertEqual(group["count"], sum(group["boards"].values()))
            devices.add(key)
            identifiers.update((p["project"], p["reference"]) for p in group["occurrences"])
        self.assertEqual(1208, len(identifiers))
        self.assertEqual(245, len(devices))
        self.assertEqual(428, sum(project == "LESHY2-UI-R2" for project, _ in identifiers))
        self.assertEqual(780, sum(project == "LESHY2-RF-R2" for project, _ in identifiers))

    def test_candidates_are_not_silent_replacements(self):
        self.assertFalse(self.active["authority"]["replacement_approved"])
        self.assertFalse(self.active["authority"]["production_changes"])
        self.assertFalse(self.active["authority"]["factory_stock_checked"])
        self.assertTrue(all(value is False for value in self.passive["authority"].values()))
        self.assertEqual(6, len(self.passive["ranked_candidates"]))
        self.assertEqual(4, self.passive["summary"]["same_dc_class_resistor_pairs"])
        self.assertEqual(9, self.passive["summary"]["resistor_minority_instances"])
        groups = {group["id"]: group for group in self.active["groups"]}
        switch = groups["AUDIO_SINGLE_SPDT"]
        self.assertEqual("candidate_for_separate_unification_review_not_approved", switch["status"])
        self.assertEqual([1, 3], [part["count"] for part in switch["components"]])

    def test_shared_snapshot_source_hashes_agree(self):
        primary = {row["path"]: row["sha256"] for row in self.active["sources"]}
        for path, digest in self.passive["snapshot"]["sources"].items():
            self.assertEqual(digest, primary[path])
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertTrue((ROOT / path).is_file())
        # Sources may legitimately change after this immutable audit. Its
        # recorded SHA values must not be relabelled as current qualification.

    def test_public_report_is_bilingual_and_linked(self):
        for suffix in ("", ".ru"):
            name = f"h6-r2-component-unification{suffix}.md"
            page = (ROOT / "docs" / name).read_text()
            self.assertIn("USB4105-GF-A", page)
            self.assertIn("SN74LVC1G3157", page)
            self.assertIn("0402WGF1002TCE", page)
            self.assertIn(name, (ROOT / f"README{suffix}.md").read_text())

    def test_current_usb_reference_coordinates_match_intent_and_both_pages(self):
        expected = {
            ("UI", "J11"): 14.87, ("UI", "J9"): 26.1,
            ("RF", "J1"): 16.47, ("RF", "J4"): 37.47,
        }
        # Inspect the literal native-intent mapping without importing pcbnew or
        # treating prose as placement authority. In particular J9/J11 cannot be
        # exchanged merely because both component counts still equal two.
        source = ROOT / "hardware/layout/h6_r2_placement_intent.py"
        tree = ast.parse(source.read_text())
        loops = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.For) and isinstance(node.target, ast.Tuple)
            and [getattr(item, "id", None) for item in node.target.elts]
            == ["board", "ref", "x"]
        ]
        self.assertEqual(1, len(loops))
        self.assertIsInstance(loops[0].iter, ast.Tuple)
        literal = []
        for row in loops[0].iter.elts:
            self.assertIsInstance(row, ast.Tuple)
            self.assertEqual(3, len(row.elts))
            board, reference, x = row.elts
            self.assertIsInstance(board, ast.Name)
            literal.append(((board.id.upper(), ast.literal_eval(reference)), ast.literal_eval(x)))
        self.assertEqual(4, len(literal))
        self.assertEqual(expected, dict(literal))
        for suffix in ("", ".ru"):
            page = (ROOT / "docs" / f"h6-r2-component-unification{suffix}.md").read_text()
            pairs = re.findall(r"\b(UI|RF) (J\d+) = (\d+(?:\.\d+)?)", page)
            self.assertEqual(4, len(pairs))
            self.assertEqual(expected, {(board, ref): float(x) for board, ref, x in pairs})


if __name__ == "__main__":
    unittest.main()
