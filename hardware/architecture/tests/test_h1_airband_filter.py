import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/h1_airband_filter.py"
SPEC = importlib.util.spec_from_file_location("h1_airband_filter", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1AirbandFilterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = MODULE.load()
        cls.audit = MODULE.audit(cls.model)

    def test_bounded_candidate_passes_but_is_not_production_frozen(self):
        self.assertEqual("pass", self.audit["status"])
        self.assertTrue(self.audit["lumped_topology_is_reviewed"])
        self.assertEqual(1024, self.audit["corner_count"])
        self.assertGreater(self.audit["nominal_and_corner_model"]["minimum_margin_db"], 0.0)
        self.assertFalse(self.audit["candidate_is_production_frozen"])

    def test_factory_population_is_exact_and_not_misrepresented_as_frozen(self):
        rows = self.model["candidate"]["physical_population"]
        self.assertTrue(all(row["mpn"] and row["jlcpcb_part"].startswith("C") for row in rows))
        self.assertEqual(18, sum(row["quantity"] for row in rows))
        self.assertIn("not a routed-PCB production freeze", self.model["residual_boundary"]["not_claimed"])
        self.assertIn("H6", self.model["residual_boundary"]["h6_gate"])
        self.assertIn("H8", self.model["residual_boundary"]["h8_gate"])

    def test_generated_artifacts_are_current(self):
        expected = {
            MODULE.AUDIT_PATH: json.dumps(self.audit, indent=2, ensure_ascii=False) + "\n",
            MODULE.SVG_PATH: MODULE.render_svg(self.model, self.audit),
            MODULE.EN_DOC_PATH: MODULE.render_doc(self.model, self.audit, False),
            MODULE.RU_DOC_PATH: MODULE.render_doc(self.model, self.audit, True),
        }
        for path, content in expected.items():
            self.assertTrue(path.exists(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
