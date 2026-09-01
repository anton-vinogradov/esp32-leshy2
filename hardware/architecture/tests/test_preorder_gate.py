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
        self.assertEqual("LESHY2-PREORDER-R2", self.contract["contract_id"])
        truth = self.contract["current_truth"]
        self.assertIn("H1-R2.38 is the user-accepted reviewed", truth["mechanical_projection"])
        self.assertIn("H2-R2.1.5 is reviewed", truth["current_ecad"])
        self.assertIn("H3-R2.0.1", truth["current_ecad"])
        self.assertIn("1183 fitted board positions", truth["current_ecad"])
        self.assertIn("816 canonical nets", truth["current_ecad"])
        self.assertIn("both pass ERC", truth["current_ecad"])
        self.assertIn("173 controller pins", truth["current_ecad"])
        self.assertIn("F2-R2.5 is in progress", truth["executable_firmware"])
        self.assertIn("F3-R2 and F-PO remain blocked", truth["instruction_emulation"])
        self.assertIn("H6 routed release candidate", truth["joined_release"])
        self.assertIn("immutable P8 order release", truth["joined_release"])
        self.assertEqual("not run", truth["physical_hil"])
        self.assertFalse(truth["order_authorized"])

        gates = {gate["id"]: gate for gate in self.contract["gates"]}
        self.assertEqual("reviewed", gates["P0_REQUIREMENTS_ARCHITECTURE"]["status"])
        self.assertEqual("reviewed", gates["P1_CURRENT_PHYSICAL_DESIGN"]["status"])
        self.assertEqual("reviewed", gates["P2_R2_PRODUCTION_SCHEMATIC"]["status"])
        self.assertEqual("reviewed", gates["P3_R2_VIRTUAL_ELECTRICAL"]["status"])
        self.assertEqual("in_progress", gates["P4_JOINED_PRE_LAYOUT_REVIEW"]["status"])
        for gate_id in (
            "P5_EXACT_PRODUCTION_SOURCING",
            "P6_ROUTED_PRODUCTION_PACKAGE",
            "P7_FIRST_SPIN_DIAGNOSTIC",
        ):
            self.assertEqual("blocked", gates[gate_id]["status"])
        self.assertEqual("not_authorized", gates["P8_IMMUTABLE_EXACT_ONE_RELEASE"]["status"])
        boundary = self.contract["procurement_boundary"]
        self.assertEqual(1, boundary["assembled_device_quantity"])
        self.assertIn("optional", boundary["factory_powered_function_test"])
        self.assertIn("owner", boundary["first_full_power_on"])

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

    def test_procurement_remains_unauthorized_during_h5_evidence_planning(self):
        index = (REPO_ROOT / "hardware/procurement/README.md").read_text(encoding="utf-8")
        plan = (
            REPO_ROOT / "hardware/procurement/pre-kicad-sample-plan.md"
        ).read_text(encoding="utf-8")
        plan_normalized = " ".join(plan.split())
        self.assertIn("H1 through H4", index)
        self.assertIn("H5.0.3 is current", index)
        self.assertIn("superseded", plan)
        self.assertIn("remain unauthorized", plan)
        self.assertIn("no separate engineering-sample or H5 coupon order", plan_normalized)
        self.assertIn("sole prototype order", plan_normalized)


if __name__ == "__main__":
    unittest.main()
