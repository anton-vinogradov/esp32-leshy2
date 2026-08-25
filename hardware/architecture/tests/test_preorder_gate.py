import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


class PreorderGateTests(unittest.TestCase):
    def setUp(self):
        self.contract_path = (
            REPO_ROOT / "hardware/verification/preorder-verification-contract.json"
        )
        self.contract = json.loads(self.contract_path.read_text(encoding="utf-8"))

    def test_gate_reports_actual_unfinished_state(self):
        self.assertEqual("LESHY2-PREORDER-1", self.contract["contract_id"])
        truth = self.contract["current_truth"]
        self.assertIn("H1 accepted", truth["mechanical_projection"])
        self.assertIn("H2 production schematics accepted", truth["current_ecad"])
        self.assertIn("F3 reviewed", truth["executable_firmware"])
        self.assertIn("52/52 artifacts reproduce byte-for-byte", truth["executable_firmware"])
        self.assertIn("ESP32-S3 exact debug/release images boot", truth["instruction_emulation"])
        self.assertEqual("not run", truth["physical_hil"])

        gates = {gate["id"]: gate for gate in self.contract["gates"]}
        self.assertEqual("reviewed", gates["P0_REQUIREMENTS_ARCHITECTURE"]["status"])
        self.assertEqual("reviewed", gates["P1_MECHANICAL_DESIGN"]["status"])
        self.assertEqual("reviewed", gates["P2_CURRENT_SCHEMATIC"]["status"])
        self.assertEqual("reviewed", gates["P3_VIRTUAL_ELECTRICAL"]["status"])
        self.assertEqual("reviewed", gates["P5_TARGET_BUILDS_EMULATION"]["status"])
        self.assertEqual("reviewed", gates["P4_EXECUTABLE_FIRMWARE_MODEL"]["status"])
        self.assertEqual("current_joined_review", gates["P6_PRE_LAYOUT_REVIEW"]["status"])
        self.assertEqual("not_authorized", gates["P7_ENGINEERING_SAMPLE_ORDER"]["status"])
        self.assertEqual("not_authorized", gates["P8_KICAD_LAYOUT_AND_PROTOTYPE_PCB"]["status"])

    def test_legacy_ecad_cannot_be_mistaken_for_current(self):
        current = REPO_ROOT / "hardware/tscircuit"
        self.assertEqual([], list(current.glob("*.tsx")))
        self.assertEqual([], list(current.glob("*.kicad_pcb")))
        marker = (current / "README.md").read_text(encoding="utf-8")
        self.assertIn("no current Leshy2 schematic or PCB layout", marker)
        self.assertIn("must not be built", " ".join(marker.split()))

        archive = REPO_ROOT / "drafts/legacy-2026-08-22/tscircuit-pre-g2f3i"
        self.assertTrue((archive / "integration.tsx").is_file())
        legacy = (archive / "integration.tsx").read_text(encoding="utf-8")
        for token in ('4.0" ST7796', "SW_STOP", "ANT_LoRa", "80mm top"):
            self.assertIn(token, legacy)

    def test_procurement_is_parked_behind_virtual_and_design_work(self):
        index = (REPO_ROOT / "hardware/procurement/README.md").read_text(encoding="utf-8")
        plan = (
            REPO_ROOT / "hardware/procurement/pre-kicad-sample-plan.md"
        ).read_text(encoding="utf-8")
        self.assertIn("not the next project step", index)
        self.assertIn("P1–P6", index)
        self.assertIn("not the next project step", plan)
        self.assertIn("Sample ordering remains unauthorized", plan)
        self.assertIn("Purchasing is the\nlast resort", plan)


if __name__ == "__main__":
    unittest.main()
