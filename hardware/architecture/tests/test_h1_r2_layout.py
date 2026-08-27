import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/h1_r2_layout.py"
SPEC = importlib.util.spec_from_file_location("h1_r2_layout", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1R2LayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(MODULE.MODEL_PATH.read_text())
        cls.base = json.loads(MODULE.BASE_PATH.read_text())
        cls.audit = MODULE.audit(cls.model, cls.base)

    def test_incremental_placement_passes(self):
        self.assertEqual([], self.audit["errors"])
        self.assertEqual([], self.audit["same_face_collisions"])
        self.assertGreaterEqual(
            self.audit["minimum_opposing_clearance_mm"],
            self.audit["required_opposing_clearance_mm"],
        )

    def test_every_fixed_body_has_exact_mpn(self):
        for item in self.model["placements"]:
            if item["kind"] == "fixed_body":
                self.assertTrue(item["mpn"], item["id"])

    def test_every_drawn_item_has_one_unique_compact_reference(self):
        refs = [item["drawing_ref"] for item in self.model["placements"]]
        self.assertEqual(len(refs), len(set(refs)))
        self.assertTrue(all(len(ref) <= 2 for ref in refs))

    def test_k331_physical_boundary_is_a_reserve_not_a_fake_component(self):
        bay = next(x for x in self.model["placements"] if x["id"] == "fpv_receiver_bay")
        self.assertEqual("reserve", bay["kind"])
        self.assertIsNone(bay["mpn"])
        self.assertEqual("AKK K331", bay["candidate_mpn"])
        self.assertIn("AKK-controlled maximum dimensions", self.model["current_h1_blockers"][0])

    def test_h1_blockers_are_separate_from_dependent_and_later_work(self):
        self.assertEqual(2, len(self.model["current_h1_blockers"]))
        self.assertEqual(1, len(self.model["dependent_h1_work"]))
        self.assertIn("regenerate", self.model["dependent_h1_work"][0])
        self.assertEqual({"H5/H8"}, {row["stage"] for row in self.model["downstream_verification"]})
        self.assertEqual(self.model["current_h1_blockers"], self.audit["current_h1_blockers"])
        self.assertEqual(self.model["dependent_h1_work"], self.audit["dependent_h1_work"])

    def test_factory_rows_include_current_identity(self):
        by_mpn = {row["mpn"]: row for row in self.model["factory_evidence"]}
        self.assertEqual("C3824301", by_mpn["TVP5150AM1PBS"]["jlcpcb_part"])
        self.assertEqual("C2894793", by_mpn["DL-MMCX-KWE-90"]["jlcpcb_part"])
        self.assertEqual("C39843328", by_mpn["SC1512-A4"]["jlcpcb_part"])
        self.assertIsNone(by_mpn["K331"]["jlcpcb_part"])
        self.assertFalse(by_mpn["K331"]["accepted"])
        self.assertTrue(all("accepted" in row for row in self.model["factory_evidence"]))
        self.assertTrue(by_mpn["TPS7A2018PDBVR"]["accepted"])
        self.assertIn("2,225 pieces", by_mpn["TPS7A2018PDBVR"]["availability"])

    def test_mmcx_uses_manufacturer_body_and_mounting_geometry(self):
        mmcx = next(x for x in self.model["placements"] if x["id"] == "fpv_mmcx")
        self.assertEqual([71.4, 99.5], mmcx["world_xy_mm"])
        self.assertEqual([6.6, 3.6, 4.0], mmcx["size_mm"])
        self.assertEqual(3.6, mmcx["mounting"]["body_inboard_mm"])
        self.assertEqual(3.0, mmcx["mounting"]["barrel_outboard_mm"])
        self.assertEqual([73.2, 101.3], mmcx["mounting"]["mounting_axis_world_xy_mm"])
        self.assertEqual(4, mmcx["mounting"]["ground_post_count"])
        self.assertEqual([2.0, 2.0], mmcx["mounting"]["ground_post_pitch_mm"])
        evidence = next(x for x in self.model["factory_evidence"] if x["mpn"] == mmcx["mpn"])
        self.assertTrue(evidence["accepted"])
        self.assertIn("dreamlnk.com", evidence["manufacturer_url"])
        self.assertIn("faiusr.com", evidence["drawing_url"])
        self.assertIn("Wave Soldering", evidence["assembly"])

    def test_mmcx_tail_and_service_keepouts_pass(self):
        service = self.audit["mmcx_service"]
        self.assertEqual(
            self.base["stack"]["rf_pcb_thickness_mm"],
            self.model["stack"]["rf_pcb_thickness_mm"],
        )
        self.assertEqual("pass", service["status"])
        self.assertEqual([], service["errors"])
        self.assertEqual([], service["opposing_body_hits"])
        self.assertEqual([], service["accessory_hits"])
        self.assertAlmostEqual(1.2, service["nominal_tail_projection_into_gap_mm"])
        self.assertAlmostEqual(0.5, service["sidewall_radial_clearance_mm"])
        self.assertEqual(12.0, service["external_service_keepout"]["diameter_mm"])

    def test_generated_artifacts_are_current(self):
        expected = {
            MODULE.AUDIT_PATH: json.dumps(self.audit, indent=2, ensure_ascii=False) + "\n",
            MODULE.SVG_PATH: MODULE.render_svg(self.model, self.base, self.audit),
            MODULE.MMCX_SVG_PATH: MODULE.render_mmcx_service_svg(self.model, self.audit),
            MODULE.EN_DOC_PATH: MODULE.render_doc(self.model, self.audit, False),
            MODULE.RU_DOC_PATH: MODULE.render_doc(self.model, self.audit, True),
        }
        for path, content in expected.items():
            self.assertTrue(path.exists(), path)
            self.assertEqual(content, path.read_text(), path)
        self.assertNotIn("[`None`]", expected[MODULE.EN_DOC_PATH])
        self.assertNotIn("[`None`]", expected[MODULE.RU_DOC_PATH])


if __name__ == "__main__":
    unittest.main()
