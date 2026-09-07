"""Physical projection regressions: known datums, not generated-file equality."""

import ast
import copy
import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "h1_r2_view_invariants", REPO / "hardware/product-design/h1_r2_layout.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def find(root, attribute, value):
    return next(node for node in root.iter() if node.get(attribute) == value)


def body(identifier, frame, x, width=4.0):
    return {
        "id": identifier, "frame": frame, "bbox": {
            "x": [x, x + width], "y": [50.0, 54.0], "z": [5.0, 6.0]
        }, "mpn": "projection probe", "role": "asymmetric datum probe",
        "kind": "fixed_body", "origin": "R2 placement",
    }


class H1R2ViewInvariantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_model = json.loads(MODULE.MODEL_PATH.read_text())
        cls.result = json.loads(MODULE.AUDIT_PATH.read_text())

    def setUp(self):
        self.model = copy.deepcopy(self.original_model)
        self.model["physical_features"] = []
        self.rows = [body("ui_probe", "ui-inner", 12), body("rf_probe", "rf-inner", 12)]
        self.topology = {"pcb_segments": [], "cables": [], "connectors": []}

    def render_face(self, frame):
        with mock.patch.object(MODULE, "complete_inner_rows", return_value=self.rows), \
                mock.patch.object(MODULE, "r2_antenna_topology", return_value=self.topology):
            return ET.fromstring(MODULE.render_inner_face_svg(
                self.model, {}, {}, self.result, frame
            ))

    def test_shared_world_rectangle_is_mirrored_only_for_ui_inner(self):
        # World box [12,16] becomes [64,68] on UI B, stays [12,16] on RF B.
        for frame, identifier, expected_x in (
            ("ui-inner", "ui_probe", 64), ("rf-inner", "rf_probe", 12)
        ):
            node = find(self.render_face(frame), "data-instance", identifier)
            self.assertAlmostEqual(expected_x, (float(node.get("x")) - 80) / 5.6)
            self.assertAlmostEqual(4, float(node.get("width")) / 5.6)
            self.assertAlmostEqual(50, (float(node.get("y")) - 165) / 5.6)

    def test_sparse_engineering_view_uses_the_same_physical_handedness(self):
        base = {"rows": [
            {"instance": row["id"], "source_frame": row["frame"], "world_bbox_mm": row["bbox"]}
            for row in self.rows
        ]}
        self.model["placements"] = [
            {"id": "new_rf_probe", "frame": "rf-inner", "world_xy_mm": [19, 40],
             "size_mm": [5, 4, 1], "kind": "fixed_body", "drawing_ref": "R",
             "mpn": "probe", "role": "R2 world datum"}
        ]
        root = ET.fromstring(MODULE.render_svg(self.model, base, self.result))
        for identifier, origin, expected in (
            ("ui_probe", 70, 64), ("rf_probe", 410, 12), ("new_rf_probe", 410, 19)
        ):
            node = find(root, "data-instance", identifier)
            self.assertAlmostEqual(expected, (float(node.get("x")) - origin) / 3.2)

    def test_combined_inner_view_does_not_reintroduce_rf_reflection(self):
        with mock.patch.object(MODULE, "complete_inner_rows", return_value=self.rows), \
                mock.patch.object(MODULE, "r2_antenna_topology", return_value=self.topology):
            root = ET.fromstring(MODULE.render_complete_inner_svg(self.model, {}, {}, self.result))
        for identifier, origin, expected in (("ui_probe", 65, 64), ("rf_probe", 440, 12)):
            node = find(root, "data-instance", identifier)
            self.assertAlmostEqual(expected, (float(node.get("x")) - origin) / 3.65)
        self.assertFalse(any(node.tag.endswith("path") and node.get("marker-end") for node in root.iter()))

    def test_world_keepout_is_not_treated_as_rear_exterior_geometry(self):
        self.model["physical_features"] = [{
            "id": "rf_world_keepout", "frame": "rf-inner", "kind": "keepout",
            "world_bbox_mm": {"x": [17, 23], "y": [30, 35]},
        }]
        node = find(self.render_face("rf-inner"), "data-physical-feature", "rf_world_keepout")
        self.assertAlmostEqual(17, (float(node.get("x")) - 80) / 5.6)
        self.assertAlmostEqual(6, float(node.get("width")) / 5.6)

    def test_exterior_local_holes_mirror_once_on_both_inner_faces(self):
        # Deliberately asymmetric positions catch a double reflection hidden by
        # the production [5,75] symmetric pattern.
        legacy = MODULE.legacy_generator()
        with mock.patch.object(legacy, "HOLES", ((7, 11), (72, 15), (6, 145), (74, 144))):
            for frame in ("ui-inner", "rf-inner"):
                root = self.render_face(frame)
                holes = [n for n in root.iter() if n.get("data-mechanical-feature") == "mounting-hole"]
                self.assertEqual(4, len(holes))
                self.assertEqual(["MH1", "MH2", "MH3", "MH4"], [n.get("data-hole") for n in holes])
                for node, x, y in zip(holes, (73, 8, 74, 6), (11, 15, 145, 144)):
                    self.assertAlmostEqual(x, (float(node.get("cx")) - 80) / 5.6)
                    self.assertAlmostEqual(y, (float(node.get("cy")) - 165) / 5.6)
                    self.assertAlmostEqual(2.7, 2 * float(node.get("r")) / 5.6, places=2)
                    self.assertEqual("#ffffff", node.get("fill"))
                self.assertEqual(4, sum(n.get("data-mechanical-feature") == "mounting-keepout" for n in root.iter()))

    def test_fpc_slot_uses_world_rectangle_and_exact_capsule_dimensions(self):
        route = {"mechanical_retention": {"fpc_route_side_section": {
            "pcb_slot_position_mm": [21.25, 23], "pcb_slot_width_mm": 27,
            "pcb_slot_height_mm": 1.2,
        }}}
        with mock.patch.object(MODULE, "load", return_value=route) as loader:
            root = self.render_face("ui-inner")
        loader.assert_called_once_with(MODULE.DISPLAY_MOUNT_PATH)
        slot = find(root, "data-mechanical-feature", "display-fpc-slot")
        self.assertAlmostEqual(31.75, (float(slot.get("x")) - 80) / 5.6)
        self.assertAlmostEqual(23, (float(slot.get("y")) - 165) / 5.6)
        self.assertAlmostEqual(27, float(slot.get("width")) / 5.6)
        self.assertAlmostEqual(1.2, float(slot.get("height")) / 5.6)
        self.assertAlmostEqual(.6, float(slot.get("rx")) / 5.6)

    def test_ui_slot_is_not_copied_to_rf_board(self):
        with mock.patch.object(MODULE, "load") as loader:
            root = self.render_face("rf-inner")
        loader.assert_not_called()
        self.assertFalse(any(n.get("data-mechanical-feature") == "display-fpc-slot" for n in root.iter()))

    def test_sma_exterior_identity_order_stays_mirrored_on_both_inner_views(self):
        for face, frame in (("front", "ui-inner"), ("rear", "rf-inner")):
            self.model["antenna_bank_optimization"][f"{face}_x_centres_mm"] = [7, 21, 39, 53, 72]
            root = self.render_face(frame)
            paths = self.model["antenna_bank_optimization"][f"{face}_paths"]
            for path, expected_x in zip(paths, (73, 59, 41, 27, 8)):
                label = next(n for n in root.iter() if n.tag.endswith("text") and n.text == path)
                self.assertAlmostEqual(expected_x, (float(label.get("x")) - 80) / 5.6)

    def test_rf_topology_converts_only_exterior_port_not_world_source(self):
        bank = self.model["antenna_bank_optimization"]
        bank["front_x_centres_mm"] = bank["rear_x_centres_mm"] = [7, 21, 39, 53, 72]
        ids = ["nrf0_r2", "nrf1_r2", "nrf2_r2", "s3", "c5", "voice", "voice_v", "cc_r2",
               "receiver_r2", "airband_selector", "airband_lna", "airband_mixer", "airband_lo",
               "s3_rf_coupler_r2", "c5_rf_coupler_r2"]
        ids += [f"{name}_rf_board_connector_r2" for name in ("nrf0", "nrf1", "nrf2", "s3", "c5")]
        rows = [body(identifier, "rf-inner", 30) for identifier in ids]
        topology = MODULE.r2_antenna_topology(self.model, rows)
        segments = {(n["path"], n["branch"]): n for n in topology["pcb_segments"]}
        self.assertEqual([(32, 52), (8, 0)], segments["VOICE-UHF", "main"]["points"])
        self.assertEqual([(32, 52), (27, 0)], segments["VOICE-VHF", "main"]["points"])
        self.assertEqual((73, 0), segments["RX-FM/SW", "direct-fm-sw"]["points"][0])
        self.assertEqual((7, 0), segments["N24-0", "main"]["points"][-1])

    def test_source_and_port_remain_connected_after_rf_projection(self):
        self.topology["pcb_segments"] = [{
            "frame": "rf-inner", "path": "probe", "branch": "main",
            "points": [(14, 52), (73, 0)], "medium": "controlled-50-ohm-pcb",
            "stroke": "#2563eb", "width": 1.7, "dash": None,
        }]
        root = self.render_face("rf-inner")
        segment = find(root, "data-path", "probe")
        points = [[float(v) for v in pair.split(",")] for pair in segment.get("points").split()]
        self.assertAlmostEqual(14, (points[0][0] - 80) / 5.6)
        self.assertAlmostEqual(73, (points[-1][0] - 80) / 5.6)
        node = find(root, "data-instance", "rf_probe")
        self.assertAlmostEqual(points[0][0], float(node.get("x")) + float(node.get("width")) / 2)

    def test_four_face_scale_and_clip_preserve_complete_interface_extents(self):
        external = '<svg><rect data-probe="ui" x="80" y="150" width="296" height="555"/><rect data-probe="rf" x="465" y="150" width="296" height="555"/></svg>'
        inner = '<svg><rect data-probe="inner" x="80" y="165" width="448" height="840"/></svg>'
        root = ET.fromstring(MODULE.render_four_faces_svg(self.model, external, inner, inner))
        for panel in (n for n in root if n.get("data-panel")):
            name = panel.get("data-panel")
            group = next(iter(panel))
            tx, ty, scale = map(float, re.fullmatch(r"translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)", group.get("transform")).groups())
            exterior = name.endswith("external")
            width, height, y0 = (296, 555, 150) if exterior else (448, 840, 165)
            self.assertAlmostEqual(320, width * scale, places=5)
            self.assertAlmostEqual(600, height * scale, places=5)
            board_top = ty + y0 * scale
            clip_id = panel.get("clip-path")[5:-1]
            clip = next(iter(find(root, "id", clip_id)))
            clip_top = float(clip.get("y"))
            clip_bottom = clip_top + float(clip.get("height"))
            if exterior:
                # 4 px/mm in every panel. Source barrel=-11.4 mm, antenna
                # arrow tip=-14.7 mm, bottom arrow tip=+8 mm from PCB edge.
                self.assertLessEqual(clip_top, board_top - 14.7 * 4 - 1)
                self.assertGreaterEqual(clip_bottom, board_top + 600 + 8 * 4 + 1)
                self.assertGreater(board_top - 14.7 * 4, 130 + 5)
            else:
                self.assertLessEqual(clip_top, board_top - 7 * 4)
                self.assertGreaterEqual(clip_bottom, board_top + 600)
                self.assertGreater(float(root.get("height")), board_top + 600 + 20)

    def test_unknown_frame_fails_instead_of_silently_mirroring(self):
        for function in (MODULE.inner_view_x, MODULE.exterior_x_to_world):
            with self.assertRaises(ValueError):
                function("rf-inner-typo", 12, 4, 80)


class H1R2InventoryReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = MODULE.load(MODULE.MODEL_PATH)
        cls.base = MODULE.load(MODULE.BASE_PATH)
        cls.sources = MODULE.load(MODULE.SOURCE_TABLE_PATH)
        cls.result = MODULE.audit(cls.model, cls.base)
        cls.rows = MODULE.complete_inner_rows(cls.model, cls.base, cls.sources, cls.result)

    def test_replaced_and_retired_seed_bodies_leave_all_current_populations(self):
        obsolete = {"evidence_cmp_b", "evidence_main_isolator", "evidence_main_isolator_bypass",
                    "slow_io", "safe_reset_sink_b"}
        self.assertEqual({"evidence_main_isolator", "evidence_main_isolator_bypass"},
                         set(self.result["retired_seed_instances"]))
        self.assertIn("evidence_cmp_b", self.result["replaced_seed_instances"])
        self.assertTrue(obsolete <= {row["instance"] for row in self.base["rows"]},
                        "historical source evidence must not be deleted")
        placed = [{"item": item, "bbox": MODULE.bbox(item, self.model)}
                  for item in self.model["placements"]]
        for rows in (self.rows, MODULE.effective_inner_entries(self.model, self.base, placed)):
            self.assertFalse(obsolete & {row["id"] for row in rows})
            self.assertEqual(1, sum(row["id"] == "nrf_evidence_cmp_r2" for row in rows))
        svg = MODULE.render_svg(self.model, self.base, self.result)
        for instance in obsolete:
            self.assertNotIn(f'data-instance="{instance}"', svg)

    def test_retired_collision_is_excluded_but_reappears_if_retirement_is_removed(self):
        base = copy.deepcopy(self.base)
        placement = next(p for p in self.model["placements"] if p["id"] == "slow_io_r2")
        retired = next(row for row in base["rows"] if row["instance"] == "evidence_main_isolator")
        retired["source_frame"] = "rf-inner"
        retired["world_bbox_mm"] = MODULE.bbox(placement, self.model)
        self.assertEqual([], MODULE.audit(self.model, base)["same_face_collisions"])
        model = copy.deepcopy(self.model)
        model["retired_seed_instances"].remove("evidence_main_isolator")
        self.assertIn(["slow_io_r2", "evidence_main_isolator"],
                      MODULE.audit(model, base)["same_face_collisions"])

    def test_retirement_cannot_hide_an_unknown_or_replaced_instance(self):
        for retired, expected in ((["typo-body"], "unknown retired"),
                                  (["slow_io"], "both retired and replaced"),
                                  (["evidence_main_isolator"] * 2, "duplicates")):
            model = copy.deepcopy(self.model)
            model["retired_seed_instances"] = retired
            self.assertTrue(any(expected in error for error in MODULE.audit(model, self.base)["errors"]))

    def test_two_asymmetric_native_bodies_match_their_rf_world_replacements(self):
        review = MODULE.load(REPO / "hardware/product-design/h1-r2-native-body-review.json")
        snapshot = review["source_snapshot"]
        self.assertRegex(snapshot["commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(snapshot["pcb_sha256"], r"^[0-9a-f]{64}$")
        self.assertFalse(review["concept_collision_review"]["native_pcb_geometry_verified_as_a_whole"])
        self.assertFalse(review["concept_collision_review"]["production_release_authorized"])
        tree = ast.parse((REPO / "hardware/layout/h6_r2_placement.py").read_text())
        fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                  and node.name == "_balanced_form_end")
        namespace = {}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), "balanced_form", "exec"), namespace)
        form_end = namespace["_balanced_form_end"]
        pcb = (REPO / snapshot["pcb"]).read_text()
        forms = [pcb[m.start():form_end(pcb, m.start())]
                 for m in re.finditer(r'\(footprint "', pcb)]
        expected = {"U106": ([55.345, 82.095], [22.155, 79.595], [5.0, 5.0]),
                    "Q6": ([7.5, 91.0], [71.875, 90.0], [1.25, 2.0])}
        for body in review["bodies"]:
            ref = body["reference"]
            with self.subTest(reference=ref):
                native = next(form for form in forms if f'(property "Reference" "{ref}"' in form)
                self.assertIn(f'(footprint "{body["footprint"]}"', native)
                self.assertEqual("B.Cu", re.search(r'\(layer "([^"]+)"\)', native)[1])
                at = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', native)
                anchor = list(map(float, at.group(1, 2)))
                self.assertEqual(expected[ref][0], anchor)
                self.assertEqual(0, float(at[3] or 0))
                points = []
                for match in re.finditer(r'\(fp_(rect|poly)\b', native):
                    shape = native[match.start():form_end(native, match.start())]
                    if '(layer "B.Fab")' not in shape:
                        continue
                    points.extend((float(x) + anchor[0], float(y) + anchor[1])
                                  for x, y in re.findall(r'\((?:start|end|xy) ([-\d.]+) ([-\d.]+)\)', shape))
                self.assertTrue(points)
                native_box = {axis: [min(p[n] for p in points), max(p[n] for p in points)]
                              for n, axis in enumerate(("x", "y"))}
                target = next(p for p in self.model["placements"] if p["id"] == body["id"])
                self.assertEqual("rf-inner", target["frame"])
                self.assertEqual(body["replaces"], target["replaces"])
                self.assertEqual(expected[ref][1], target["world_xy_mm"])
                self.assertEqual(expected[ref][2], target["size_mm"][:2])
                self.assertEqual(body["native_anchor_mm"], anchor)
                for axis in ("x", "y"):
                    for actual, recorded in zip(native_box[axis], body["native_body_bbox_mm"][axis]):
                        self.assertAlmostEqual(recorded, actual)
                self.assertAlmostEqual(target["world_xy_mm"][0], 80 - native_box["x"][1])
                self.assertAlmostEqual(target["world_xy_mm"][1], native_box["y"][0])
        self.assertEqual([], self.result["same_face_collisions"])

    def test_bilingual_document_retains_h1_history_without_native_release_claim(self):
        result = copy.deepcopy(self.result)
        topology = MODULE.r2_antenna_topology(self.model, self.rows)
        result["rf_microcoax"] = MODULE.r2_microcoax_audit(self.model, self.rows, topology)
        for ru in (False, True):
            doc = MODULE.render_doc(self.model, result, ru)
            suffix = ".ru" if ru else ""
            self.assertIn(f"h6-r2-component-views{suffix}.md", doc)
            self.assertIn(f"h6-r2-interface-review{suffix}.md", doc)
            self.assertIn("2026-08-30", doc)
            self.assertIn("не означают готовность к производству" if ru else "do not close H6 geometry checks", doc)
        self.assertFalse(self.result["native_pcb_correspondence_verified"])

    def test_display_role_labels_manufacturer_pin_one_at_world_xmax(self):
        legacy = MODULE.legacy_generator()
        connector = next(p for p in legacy.UI_INNER if p.instance == "display_connector")
        self.assertIn("connector pin 1 at world x-max", connector.role)
        self.assertIn("tail pin 1 mates connector pin 50 at world x-min", connector.role)


if __name__ == "__main__":
    unittest.main()
