"""Read-only regressions for complete, side-separated native component views.

These check drawing inventory and presentation, not physical assembly or 3D
correctness. Production PCB files are only read; rendering is owned separately.
"""

import copy
import hashlib
import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_component_render.py"
MANIFEST = ROOT / "hardware/layout/generated/H6-R2-component-views.json"
EXPECTED = {("ui", "outer"): (30, 4), ("ui", "inner"): (398, 0),
            ("rf", "outer"): (16, 4), ("rf", "inner"): (764, 0)}
SVG = "{http://www.w3.org/2000/svg}"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_footprint_forms(source):
    """Extract quoted KiCad footprint forms without treating string '(' as syntax."""
    for match in re.finditer(r'\(footprint\s+"', source):
        depth, quoted, escaped = 0, False, False
        for index in range(match.start(), len(source)):
            char = source[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    yield source[match.start():index + 1]
                    break
        else:
            raise ValueError("unterminated native footprint")


def own_face_elements(root):
    """Opposite-face context is clipped: its hidden refs cannot prove coverage."""
    if root.get("data-role") == "opposite-face-protrusions":
        return
    yield root
    for child in root:
        yield from own_face_elements(child)


class ComponentRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h6_component_render_under_test", SCRIPT)
        cls.renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.renderer)
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.views = {(row["board"], row["face"]): row for row in cls.manifest["views"]}
        cls.roots = {key: ET.parse(ROOT / row["svg"]).getroot() for key, row in cls.views.items()}

    def test_manifest_has_exact_four_views_and_inventory_counts(self):
        self.assertEqual(set(EXPECTED), set(self.views))
        self.assertEqual(4, len(self.manifest["views"]))
        for key, (components, mounts) in EXPECTED.items():
            with self.subTest(view=key):
                row = self.views[key]
                self.assertEqual(components, row["component_count"])
                self.assertEqual(mounts, row["mount_count"])
                self.assertEqual(components + mounts, len(row["references"]))
                self.assertEqual(len(row["references"]), len(set(row["references"])))
        self.assertEqual(1208, sum(row["component_count"] for row in self.views.values()))
        self.assertEqual(8, sum(row["mount_count"] for row in self.views.values()))

    def test_approved_single_sentence_is_rendered_on_its_own_outer_face_only(self):
        expected = {
            "ui": "USE ONLY IN ACCORDANCE WITH APPLICABLE LAW",
            "rf": "ИСПОЛЬЗОВАТЬ ТОЛЬКО В СООТВЕТСТВИИ С ЗАКОНОМ",
        }
        for (board, face), root in self.roots.items():
            descriptions = [node.text for node in own_face_elements(root)
                            if node.tag == SVG + "desc"]
            for owner, notice in expected.items():
                self.assertEqual(int(face == "outer" and board == owner),
                                 descriptions.count(notice), (board, face, owner))

    def test_bilingual_legend_counts_match_the_current_native_inventory(self):
        english = (ROOT / "docs/h6-r2-component-views.md").read_text()
        russian = (ROOT / "docs/h6-r2-component-views.ru.md").read_text()
        for (board, face), (components, mounts) in EXPECTED.items():
            if face == "outer":
                self.assertIn(f"Outer F — {components} items + {mounts} mounting footprints", english)
                self.assertIn(f"Наружная F — {components} позиций + {mounts} крепёжных footprint", russian)
            else:
                self.assertIn(f"Inner B — {components} items", english)
                self.assertIn(f"Внутренняя B — {components} позици", russian)

    def test_manifest_references_match_actual_native_side_not_only_totals(self):
        for board_name in ("ui", "rf"):
            path = self.renderer.BOARDS[board_name]
            native = {"outer": set(), "inner": set()}
            for form in native_footprint_forms(path.read_text()):
                reference = re.search(r'\(property "Reference" "([^"]+)"', form)
                layer = re.search(r'\(layer "([FB])\.Cu"\)', form)
                self.assertIsNotNone(reference)
                self.assertIsNotNone(layer)
                native["outer" if layer[1] == "F" else "inner"].add(reference[1])
            for face in native:
                with self.subTest(board=board_name, face=face):
                    self.assertEqual(native[face], set(self.views[board_name, face]["references"]))

    def test_hashes_cover_both_pcbs_renderer_and_all_five_images(self):
        input_paths = {str(path.relative_to(ROOT)) for path in self.renderer.BOARDS.values()} | {
            str(SCRIPT.relative_to(ROOT))}
        output_paths = {row["svg"] for row in self.views.values()} | {
            "docs/images/h6-r2-components-overview.svg"}
        self.assertEqual(input_paths, set(self.manifest["inputs_sha256"]))
        self.assertEqual(output_paths, set(self.manifest["outputs_sha256"]))
        for section in ("inputs_sha256", "outputs_sha256"):
            for name, expected in self.manifest[section].items():
                with self.subTest(section=section, path=name):
                    self.assertEqual(expected, sha256(ROOT / name))
        for (board, face), svg in self.roots.items():
            source = str(self.renderer.BOARDS[board].relative_to(ROOT))
            self.assertEqual(board, svg.get("data-board"))
            self.assertEqual(face, svg.get("data-face"))
            self.assertEqual(self.manifest["inputs_sha256"][source], svg.get("data-source-sha256"))
            self.assertEqual(sha256(SCRIPT), svg.get("data-renderer-sha256"))

    def test_read_only_freshness_check_leaves_both_production_pcbs_unchanged(self):
        before = {path: sha256(path) for path in self.renderer.BOARDS.values()}
        self.renderer.check()
        self.assertEqual(before, {path: sha256(path) for path in before})

    def test_freshness_check_rejects_changed_source_and_changed_image(self):
        for section in ("inputs_sha256", "outputs_sha256"):
            with self.subTest(section=section):
                altered = copy.deepcopy(self.manifest)
                path = next(iter(altered[section]))
                altered[section][path] = "0" * 64
                with patch.object(self.renderer.json, "loads", return_value=altered):
                    with self.assertRaisesRegex(RuntimeError, "stale component view"):
                        self.renderer.check()

    def test_all_component_refs_have_own_face_native_or_fallback_labels(self):
        for key, root in self.roots.items():
            nodes = list(own_face_elements(root))
            native = {node.text for node in nodes if node.tag == SVG + "desc"}
            fallbacks = [node for node in nodes if node.get("data-role") == "reference-label-fallback"]
            refs = [node.get("data-reference") for node in fallbacks]
            expected = {ref for ref in self.views[key]["references"] if not ref.startswith("MH")}
            with self.subTest(view=key):
                self.assertEqual(expected, (native | set(refs)) & expected)
                self.assertEqual(len(refs), len(set(refs)))
                self.assertFalse(set(refs) & native, "fallback must not duplicate a native Fab reference")
                self.assertEqual(set(self.views[key]["fallback_reference_labels"]), set(refs))
                for node in fallbacks:
                    self.assertEqual(node.get("data-reference"), node.find(SVG + "text").text)

    def test_fallback_function_is_idempotent_for_native_refs_and_keeps_b_text_readable(self):
        for face in ("outer", "inner"):
            with self.subTest(face=face):
                native = '<g class="stroked-text"><desc>U1</desc></g>'
                result, added = self.renderer.with_reference_fallbacks(
                    native, face, ["U1", "U2", "MH1"], {"U2": [12, 34, 4, 6]})
                self.assertEqual(["U2"], added)
                root = ET.fromstring("<svg>" + result + "</svg>")
                group = next(node for node in root if node.get("data-reference") == "U2")
                expected = "translate(12.000000 34.000000)"
                if face == "inner":
                    expected += " scale(-1 1)"
                self.assertEqual(expected, group.get("transform"))
                self.assertEqual("U2", group.find("text").text)

    def test_actual_back_views_have_one_board_flip_and_readable_fallbacks(self):
        self.assertEqual("outer=native; inner=x_view=80-x_native, y unchanged; no extra RF transform",
                         self.manifest["view_convention"])
        for (board, face), root in self.roots.items():
            nodes = list(own_face_elements(root))
            board_flips = [node for node in nodes
                           if node.get("transform") == "translate(80 0) scale(-1 1)"]
            with self.subTest(board=board, face=face):
                self.assertEqual(int(face == "inner"), len(board_flips))
                for node in nodes:
                    if node.get("data-role") != "reference-label-fallback":
                        continue
                    self.assertEqual(face == "inner", "scale(-1 1)" in node.get("transform", ""))
                if face == "inner":
                    self.assertIn("После переворота", " ".join(root.itertext()))

    def test_four_viewports_and_overview_use_one_scale(self):
        self.assertTrue(self.manifest["same_scale"])
        self.assertEqual([80, 150], self.manifest["board_size_mm"])
        for key, root in self.roots.items():
            with self.subTest(view=key):
                self.assertEqual("0 0 96 190", root.get("viewBox"))
                self.assertEqual(("1920", "3800"), (root.get("width"), root.get("height")))
                self.assertTrue(any(node.get("transform") == "translate(8 25)" for node in root.iter()))
                self.assertTrue(any(node.get("d") == "M79 183 h10 M79 182 v2 M89 182 v2"
                                    for node in root.iter()))
        overview = ET.parse(ROOT / "docs/images/h6-r2-components-overview.svg").getroot()
        self.assertEqual("0 0 192 406", overview.get("viewBox"))
        self.assertEqual(("3840", "8120"), (overview.get("width"), overview.get("height")))
        slots = {node.get("transform") for node in overview if node.tag == SVG + "g"}
        self.assertEqual({"translate(0 18)", "translate(96 18)",
                          "translate(0 208)", "translate(96 208)"}, slots)

    def test_nfc_reservation_keeps_actual_datum_and_is_not_claimed_as_routed_copper(self):
        for key, root in self.roots.items():
            groups = [node for node in root.iter() if node.get("data-role") == "unrouted-nfc-reserve"]
            with self.subTest(view=key):
                self.assertEqual(int(key == ("rf", "outer")), len(groups))
                if groups:
                    rect = groups[0].find(SVG + "rect")
                    self.assertEqual([4.0, 17.8, 72.0, 22.4],
                                     [float(rect.get(key)) for key in ("x", "y", "width", "height")])
                    self.assertEqual("none", rect.get("fill"))
                    self.assertTrue(rect.get("stroke-dasharray"))
                    self.assertIn("L32 · NFC reserve / резерв", " ".join(groups[0].itertext()))

    def test_opposite_face_context_cannot_show_through_board_interior(self):
        for (board, face), root in self.roots.items():
            group = next(node for node in root.iter()
                         if node.get("data-role") == "opposite-face-protrusions")
            clip_id = f"outside-{board}-{face}"
            with self.subTest(board=board, face=face):
                self.assertEqual(f"url(#{clip_id})", group.get("clip-path"))
                clip = next(node for node in root.iter() if node.get("id") == clip_id)
                path = clip.find(SVG + "path")
                self.assertEqual("evenodd", path.get("clip-rule"))
                self.assertEqual("M-8 -14H88V158H-8Z M0 0V150H80V0Z", path.get("d"))

    def test_drills_are_shown_on_both_faces_and_layer_scope_has_no_routing(self):
        for board in ("ui", "rf"):
            groups = [next(node for node in self.roots[board, face].iter()
                           if node.get("data-role") == "through-board-drills")
                      for face in ("outer", "inner")]
            self.assertGreater(len(list(groups[0])), 4)
            self.assertEqual([dict(node.attrib) for node in groups[0]],
                             [dict(node.attrib) for node in groups[1]])
        self.assertEqual({"outer": "F.Fab,F.Silkscreen,Edge.Cuts",
                          "inner": "B.Fab,B.Silkscreen,Edge.Cuts"}, self.manifest["layers"])
        self.assertEqual("current_native_visualization_not_assembly_approval", self.manifest["status"])
        self.assertIn("not a 3D qualification", " ".join(self.manifest["limitations"]))


if __name__ == "__main__":
    unittest.main()
