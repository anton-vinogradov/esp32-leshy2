"""Independent scope/geometry and negative screening regressions for SMA access."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_sma_solder_access as audit

try:
    import pcbnew
except ImportError:
    pcbnew = None


def fixture(project="LESHY2-UI-R2"):
    contract = json.loads((ROOT / audit.CONTRACT).read_text())
    connectors = []
    for instance, (ref, name) in audit.EXPECTED[project].items():
        anchor = contract["antenna_ports"][project][instance]
        pads = [{**audit.expected_pad(str(n), anchor), "native_id": f"{ref}.{n}",
                 "net": "signal/" + ref if n == 1 else "/POWER_GROUND"} for n in range(1, 6)]
        connectors.append({"instance": instance, "reference": ref, "mpn": "GCT " + name,
                           "footprint": "Leshy2:" + name, "side": "F", "anchor_mm": anchor,
                           "rotation_deg": 180.0, "pads": pads})
    return {"project": project, "native_board_sha256": "a" * 64, "connectors": connectors,
            "obstacles": [], "inventory_counts": {}}, contract


def land():
    return {"native_id": "SMA.4", "number": "4", "side": "B",
            "bbox_mm": {"x": [0.0, 1.6], "y": [0.0, 3.3]}}


def obstacle(kind="courtyard_bbox", bbox=None, side="B", reference="D5"):
    return {"id": kind + side + reference, "native_id": reference + ".1", "kind": kind,
            "reference": reference, "pad": "1", "side": side,
            "bbox_mm": bbox or {"x": [0.3, 1.0], "y": [3.45, 4.0]}}


def proof(gap=0.15, contact=False):
    return {"method": "native_effective_copper_shape", "contact_or_overlap": contact,
            "lower_mm": gap, "upper_mm": gap}


class SmaScopeTests(unittest.TestCase):
    def test_independent_scope_and_exact_five_pad_pattern(self):
        self.assertEqual(["LESHY2-UI-R2", "LESHY2-RF-R2"], list(audit.EXPECTED))
        self.assertEqual(10, sum(map(len, audit.EXPECTED.values())))
        self.assertEqual(2, sum(name == "RFPC-SMA32-FN-175-A"
                               for row in audit.EXPECTED.values() for _, name in row.values()))
        # Independent primary landing geometry, not only fixture echo.
        expected = {
            "1": ("F", [1.87, 3.3], [25.3, 1.65]),
            "2": ("F", [1.6, 3.3], [27.85, 1.65]),
            "3": ("F", [1.6, 3.3], [22.75, 1.65]),
            "4": ("B", [1.6, 3.3], [27.85, 1.65]),
            "5": ("B", [1.6, 3.3], [22.75, 1.65]),
        }
        for number, (side, size, at) in expected.items():
            row = audit.expected_pad(number, [25.3, 0])
            self.assertEqual((side, size, at), (row["side"], row["size_mm"], row["at_mm"]))
            self.assertEqual(sorted([side + ".Cu", side + ".Mask", side + ".Paste"]), row["layers"])

    def test_full_two_board_scope_is_50_pads_30_front_20_back(self):
        results = [audit.audit_snapshot(*fixture(p), lambda *args: proof()) for p in audit.EXPECTED]
        self.assertEqual((50, 30, 20), tuple(sum(b["summary"][key] for b in results)
                         for key in ("pad_count", "front_pad_count", "back_pad_count")))

    def test_empty_missing_extra_or_duplicate_sma_fails(self):
        for mutation in (lambda c: c.clear(), lambda c: c.pop(),
                         lambda c: c.append(copy.deepcopy(c[0])),
                         lambda c: c[0].update(instance="unknown_sma")):
            snapshot, contract = fixture()
            mutation(snapshot["connectors"])
            result = audit.audit_snapshot(snapshot, contract, lambda *args: proof())
            self.assertEqual("fail", result["status"])

    def test_contract_and_snapshot_cannot_both_omit_required_instance(self):
        snapshot, contract = fixture()
        missing = snapshot["connectors"].pop()["instance"]
        del contract["antenna_ports"][snapshot["project"]][missing]
        self.assertTrue(audit.scope_errors(snapshot["project"], snapshot["connectors"], contract))

    def test_missing_duplicate_or_unknown_pad_fails(self):
        for mutation in (lambda p: p.pop(), lambda p: p.append(copy.deepcopy(p[0])),
                         lambda p: p[-1].update(number="6")):
            snapshot, contract = fixture()
            mutation(snapshot["connectors"][0]["pads"])
            self.assertTrue(audit.scope_errors(snapshot["project"], snapshot["connectors"], contract))

    def test_wrong_mpn_fpid_face_pose_and_each_pad_geometry_fail(self):
        for key, value in (("mpn", "generic SMA"), ("footprint", "Other:" + audit.STANDARD),
                           ("side", "B"), ("rotation_deg", 0.0), ("anchor_mm", [10.6, 1])):
            snapshot, contract = fixture()
            snapshot["connectors"][0][key] = value
            self.assertTrue(audit.scope_errors(snapshot["project"], snapshot["connectors"], contract), key)
        for key, value in (("shape", "circle"), ("attribute", "through_hole"),
                           ("size_mm", [1.5, 3.3]), ("offset_mm", [0.1, 0]),
                           ("layers", ["B.Cu"]), ("side", "F"), ("drill_mm", [0.5, 0.5]),
                           ("at_mm", [1, 2]), ("rotation_deg", 90),
                           ("bbox_mm", {"x": [0, 1], "y": [0, 3.3]})):
            snapshot, contract = fixture()
            snapshot["connectors"][0]["pads"][3][key] = value
            self.assertTrue(audit.scope_errors(snapshot["project"], snapshot["connectors"], contract), key)

    def test_empty_ground_signal_short_and_ground_disagreement_fail(self):
        for index, net in ((0, ""), (0, "/POWER_GROUND"), (3, ""), (4, "/wrong-ground")):
            snapshot, contract = fixture()
            snapshot["connectors"][0]["pads"][index]["net"] = net
            self.assertTrue(audit.scope_errors(snapshot["project"], snapshot["connectors"], contract))


class SmaScreeningTests(unittest.TestCase):
    def test_point_15_gap_is_review_not_physical_overlap(self):
        row = audit.classify_land(land(), "SMA", [obstacle()], lambda *args: proof())
        self.assertAlmostEqual(0.15, row["nearest"]["courtyard_bbox"]["bbox_gap_mm"])
        self.assertTrue(row["screening_candidates"])
        self.assertEqual([], row["foreign_courtyard_bbox_overlap"])
        self.assertEqual([], row["foreign_pad_contact_or_overlap"])

    def test_fab_and_courtyard_overlap_never_become_copper_collision(self):
        bb = {"x": [.2, .7], "y": [2, 3]}
        row = audit.classify_land(land(), "SMA", [obstacle("fab_bbox", bb), obstacle("courtyard_bbox", bb)],
                                 lambda *args: self.fail("non-copper must not call native copper test"))
        self.assertEqual(1, len(row["foreign_fab_bbox_overlap"]))
        self.assertEqual(1, len(row["foreign_courtyard_bbox_overlap"]))
        self.assertEqual([], row["foreign_pad_contact_or_overlap"])

    def test_native_clear_shape_bbox_overlap_not_hard_collision(self):
        row = audit.classify_land(land(), "SMA", [obstacle("foreign_pad", {"x": [1.5, 2], "y": [3.2, 3.8]})],
                                  lambda *args: proof(0.05))
        self.assertEqual([], row["foreign_pad_contact_or_overlap"])
        self.assertEqual(1, len(row["screening_candidates"]))

    def test_actual_foreign_pad_contact_is_separate_hard_finding(self):
        row = audit.classify_land(land(), "SMA", [obstacle("foreign_pad")], lambda *args: proof(0, True))
        self.assertEqual(1, len(row["foreign_pad_contact_or_overlap"]))

    def test_same_reference_and_opposite_face_do_not_become_obstacles(self):
        row = audit.classify_land(land(), "SMA", [obstacle(reference="SMA"), obstacle(side="F")],
                                  lambda *args: self.fail("not a foreign same-face pad"))
        self.assertEqual([], row["screening_candidates"])

    def test_one_mm_screen_is_axis_expansion_not_invented_tool_radius(self):
        self.assertEqual({"x": [-1, 2.6], "y": [-1, 4.3]}, audit.expanded(land()["bbox_mm"]))
        row = audit.classify_land(land(), "SMA", [obstacle(bbox={"x": [2.5, 3], "y": [4.2, 5]})], lambda *args: proof())
        self.assertGreater(row["nearest"]["courtyard_bbox"]["bbox_gap_mm"], 1.0)
        self.assertEqual(1, len(row["screening_candidates"]))

    def test_unsupported_or_forged_clearance_fails_closed(self):
        for bad in ({}, proof(-1), proof(float("nan")), {**proof(), "method": "bbox_only"},
                    {**proof(), "contact_or_overlap": "false"}, {**proof(), "upper_mm": 1}, proof(1, True)):
            with self.subTest(proof=bad), self.assertRaises(ValueError):
                audit.classify_land(land(), "SMA", [obstacle("foreign_pad")], lambda *args: bad)

    def test_distal_nearest_is_retained_but_not_in_screen(self):
        row = audit.classify_land(land(), "SMA", [obstacle(bbox={"x": [0, 1], "y": [8, 9]})], lambda *args: proof())
        self.assertEqual([], row["screening_candidates"])
        self.assertAlmostEqual(4.7, row["nearest"]["courtyard_bbox"]["bbox_gap_mm"])

    def test_nearest_copper_uses_native_gap_not_bbox_rank(self):
        first = obstacle("foreign_pad", {"x": [1.5, 2], "y": [3.2, 3.8]}, reference="A")
        second = obstacle("foreign_pad", {"x": [0, 1], "y": [3.5, 4]}, reference="B")
        row = audit.classify_land(land(), "SMA", [first, second],
                                  lambda _, other, side: proof(.9 if other == "A.1" else .2))
        self.assertEqual("B", row["nearest"]["foreign_pad"]["reference"])

    def test_review_required_status_not_false_pass(self):
        snapshot, contract = fixture()
        pad = snapshot["connectors"][0]["pads"][3]
        bb = copy.deepcopy(pad["bbox_mm"])
        bb["y"] = [3.45, 4.0]
        snapshot["obstacles"] = [obstacle(bbox=bb)]
        result = audit.audit_snapshot(snapshot, contract, lambda *args: proof())
        self.assertEqual("review_required", result["status"])
        self.assertEqual(0, result["summary"]["native_foreign_pad_contact_count"])
        snapshot["obstacles"] = [obstacle("foreign_pad", bb)]
        result = audit.audit_snapshot(snapshot, contract, lambda *args: proof(0, True))
        self.assertEqual("fail", result["status"])

    def test_duplicate_obstacle_id_invalidates_snapshot(self):
        snapshot, contract = fixture()
        snapshot["obstacles"] = [obstacle(), obstacle()]
        self.assertEqual("fail", audit.audit_snapshot(snapshot, contract, lambda *args: proof())["status"])


class SmaArtifactTests(unittest.TestCase):
    def test_bilingual_tables_follow_the_current_native_result(self):
        result = json.loads((ROOT / audit.OUTPUT).read_text())
        flagged = sum(bool(pad["screening_candidates"]) for board in result["boards"]
                      for connector in board["connectors"] for pad in connector["pads"])
        for language, path in audit.DOCS.items():
            section = audit.document_section(result, language)
            text = (ROOT / path).read_text()
            self.assertEqual(text, audit.refreshed_document(text, section))
            self.assertEqual(flagged, sum(line.startswith(("| UI ·", "| RF ·")) for line in section.splitlines()))
            self.assertIn("solder_process_qualified: false", section)
            self.assertIn("не до физического корпуса" if language == "ru" else "not physical bodies", section)
            self.assertIn("чужих медных площадок" if language == "ru" else "foreign copper pads", section)
            changed = copy.deepcopy(result)
            changed["summary"]["pads_with_screening_candidates"] += 1
            self.assertNotEqual(section, audit.document_section(changed, language))

    def test_report_marker_errors_do_not_overwrite_unrelated_prose(self):
        section = audit.BEGIN + "\nnew\n" + audit.END
        source = "before\n" + audit.BEGIN + "old" + audit.END + "\nafter"
        self.assertEqual("before\n" + section + "\nafter", audit.refreshed_document(source, section))
        for malformed in ("no markers", audit.BEGIN, audit.END + audit.BEGIN,
                          source + audit.BEGIN, source + audit.END):
            with self.assertRaisesRegex(ValueError, "marker pair"):
                audit.refreshed_document(malformed, section)

    @unittest.skipUnless(pcbnew is not None, "KiCad Python required for native reproducibility regression")
    def test_native_recalculation_equals_artifact_and_preserves_board_bytes(self):
        boards = [ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
                  for project in ("LESHY2-UI-R2", "LESHY2-RF-R2")]
        before = {str(path): audit.sha256(path) for path in boards}
        result = audit.build()
        self.assertEqual(json.loads((ROOT / audit.OUTPUT).read_text()), result)
        self.assertEqual(before, {str(path): audit.sha256(path) for path in boards})

    def test_current_example_has_full_scope_and_never_claims_solder_qualification(self):
        path = ROOT / audit.OUTPUT
        self.assertTrue(path.is_file(), "current native audit must not silently disappear")
        result = json.loads(path.read_text())
        self.assertEqual({"boards": 2, "connectors": 10, "pads": 50, "F": 30, "B": 20}, result["fixed_scope"])
        self.assertEqual((10, 50, 30, 20), tuple(result["summary"][k] for k in
                         ("connector_count", "pad_count", "front_pad_count", "back_pad_count")))
        self.assertEqual("review_required", result["status"])
        self.assertEqual(0, result["summary"]["native_foreign_pad_contact_count"])
        self.assertTrue(all(v is False for v in result["authorization"].values()))
        self.assertEqual(1.0, result["screening"]["per_land_axis_expansion_mm"])
        expected = {str(p.relative_to(ROOT)) for p in audit.source_paths()}
        self.assertEqual(expected, set(result["source_sha256"]))
        for path, digest in result["source_sha256"].items():
            self.assertEqual(audit.sha256(ROOT / path), digest, path)

    @unittest.skipUnless(pcbnew is not None, "KiCad Python required for native shape regression")
    def test_native_rounded_shapes_distinguish_bbox_from_copper(self):
        fp = pcbnew.FOOTPRINT(None)
        a, b = pcbnew.PAD(fp), pcbnew.PAD(fp)
        for pad in (a, b):
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetSize(pcbnew.VECTOR2I(1000000, 1000000))
        a.SetPosition(pcbnew.VECTOR2I(0, 0))
        b.SetPosition(pcbnew.VECTOR2I(900000, 900000))
        measured = audit.native_shape_gap(a.GetEffectiveShape(pcbnew.F_Cu), b.GetEffectiveShape(pcbnew.F_Cu), pcbnew)
        self.assertFalse(measured["contact_or_overlap"])
        self.assertGreater(measured["lower_mm"], .27)
        b.SetPosition(pcbnew.VECTOR2I(900000, 0))
        self.assertTrue(audit.native_shape_gap(a.GetEffectiveShape(pcbnew.F_Cu), b.GetEffectiveShape(pcbnew.F_Cu), pcbnew)["contact_or_overlap"])


if __name__ == "__main__":
    unittest.main()
