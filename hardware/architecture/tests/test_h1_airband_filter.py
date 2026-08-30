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

    def test_nominal_candidate_passes_but_is_not_production_frozen(self):
        self.assertLessEqual(self.audit["nominal_passband_maximum_loss_db"], 4.5)
        self.assertTrue(all(row["nominal_pass"] for row in self.audit["stop_results"]))
        self.assertEqual("nominal_pass_stress_fail", self.audit["status"])
        self.assertFalse(self.audit["candidate_is_production_frozen"])
        self.assertTrue(self.audit["failures"])

    def test_factory_witnesses_are_exact_but_not_misrepresented_as_the_bom(self):
        rows = self.model["factory_feasibility_witnesses"]
        self.assertTrue(all(row["mpn"] and row["jlcpcb_part"].startswith("C") for row in rows))
        self.assertIn("not a production freeze", self.model["decision"]["rejected"])
        self.assertIn("retuned in H3", self.model["decision"]["rejected"])
        self.assertIn("24 x 11 mm", self.model["decision"]["accepted"])
        self.assertIn("H6", self.model["decision"]["next_gate"])
        self.assertIn("before the H7 order", self.model["decision"]["next_gate"])

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
