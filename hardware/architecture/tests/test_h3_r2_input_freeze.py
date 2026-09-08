import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_input_freeze.py"
SPEC = importlib.util.spec_from_file_location("h3_r2_input_freeze", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2InputFreezeTest(unittest.TestCase):
    def test_current_freeze_covers_every_sheet_and_domain(self):
        result = MODULE.build()
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["errors"])
        self.assertEqual(22, result["summary"]["unique_matrix_sheets"])
        self.assertEqual(7, result["summary"]["workstream_count"])
        self.assertEqual(12, result["summary"]["shared_parameter_dependencies"])
        self.assertEqual(
            ["c5", "hub_rp", "pack", "rf_rp", "s3", "safety"],
            result["summary"]["covered_domains"],
        )
        self.assertFalse(result["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(result["authorization"]["purchasing"])
        self.assertFalse(result["authorization"]["fabrication"])

    def test_duplicate_or_missing_sheet_fails_closed(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["workstreams"][1]["sheets"].append(contract["workstreams"][0]["sheets"][0])
        result = MODULE.build(contract)
        self.assertEqual("fail", result["status"])
        self.assertIn("a native sheet has more than one primary H3 workstream", result["errors"])

    def test_reviewed_counts_cannot_be_relabeled(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["expected"]["canonical_nets"] += 1
        result = MODULE.build(contract)
        self.assertIn("reviewed H2-R2 counts differ from the H3 input-freeze contract", result["errors"])

    def test_exact_ts_jack_nc6_removal_explains_one_pin_delta(self):
        contract = MODULE.load(MODULE.CONTRACT)
        review = contract["native_contact_count_change_review"]
        self.assertEqual(4305, contract["expected"]["physical_pins"])
        self.assertEqual([4306, 4305], review["physical_pins_before_after"])
        self.assertEqual([4302, 4301], review["logical_endpoints_before_after"])
        self.assertEqual([236, 235], review["explicit_nc_before_after"])
        self.assertEqual((0, 0), (review["removed_connected_endpoints"], review["added_endpoints"]))
        nets = MODULE.load(MODULE.NETS)
        self.assertEqual((4301, 4066, 235), tuple(nets["summary"][key] for key in (
            "endpoint_count", "connected_endpoint_count", "no_connect_endpoint_count")))
        jack = [row for row in nets["rows"] if row["instance"] == "headphone_jack"]
        # Primary SJ-4351X-SMT p.2: TS has only terminals1..5, all used.
        expected = {"1": "HEADSET_MIC_RAW", "2": "HEADPHONE_LEFT_TIP", "3": "HEADPHONE_RIGHT_RING1",
                    "4": "AUDIO_GROUND", "5": "HEADSET_SWITCH_STATE"}
        self.assertEqual(5, len(jack))
        self.assertEqual(expected, {row["physical"]: row["net"] for row in jack})
        self.assertTrue(all(row["disposition"] == "connected" and row["device_id"] == "same_sky_sj_43515ts_smt_tr" for row in jack))
        self.assertNotIn("headphone_jack.RING1_SWITCH", {row["endpoint"] for row in nets["rows"]})
        kicad = MODULE.load(MODULE.KICAD)["summary"]
        self.assertEqual((4305, 4070, 235), tuple(kicad[key] for key in (
            "physical_symbol_pin_count", "connected_physical_pin_count", "explicit_no_connect_physical_pin_count")))

    def test_connected_functions_preserved_after_nc6_removal_and_usb_unification(self):
        # Fixed reviewed849a350 baseline, not a digest regenerated from the
        # current input or a test requiring a mutable Git HEAD.
        fields = ("endpoint", "project", "sheet", "reference", "contact", "physical", "role", "net", "disposition")
        connected = [copy.deepcopy(row) for row in MODULE.load(MODULE.NETS)["rows"]
                     if row.get("disposition") == "connected"]
        rows = sorted(tuple(row.get(key) for key in fields) for row in connected)
        self.assertEqual(4066, len(rows))
        payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode()
        self.assertEqual("33a9708e0db86040572f2eb85758252f2c8e568299376582b13a4ae6a3ff3571",
                         hashlib.sha256(payload).hexdigest())
        # Only the product receptacle's shell-mechanics description changed.
        # Normalize that one proven metadata delta, never any net or contact,
        # to keep the original pre-NC6 electrical-function proof meaningful.
        shell = [row for row in connected if row["endpoint"] == "product_usb_connector.SHIELD"]
        self.assertEqual(1, len(shell))
        self.assertEqual("gct_usb4105_gf_a", shell[0]["device_id"])
        self.assertEqual("four through-hole shell stakes", shell[0]["physical"])
        shell[0]["physical"] = "four 0.9-mm through-hole shell board locks"
        normalized = sorted(tuple(row.get(key) for key in fields) for row in connected)
        digest = hashlib.sha256(json.dumps(normalized, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        self.assertEqual("a8bc48ee64e32a8354904d1619552a35a2f669adc5da5a5efa09e5721b8c9e0d", digest)
        self.assertEqual(digest, MODULE.load(MODULE.CONTRACT)["native_contact_count_change_review"]["connected_tuple_sha256"])

    def test_pre_removal_physical_count_is_rejected(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["expected"]["physical_pins"] = 4306
        self.assertIn("reviewed H2-R2 counts differ from the H3 input-freeze contract", MODULE.build(contract)["errors"])

    def test_unknown_shared_parameter_dependency_fails_closed(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["workstreams"][1]["shared_parameter_dependencies"].append("missing_device")
        result = MODULE.build(contract)
        self.assertTrue(any("shared parameter dependencies" in error for error in result["errors"]))

    def test_checked_in_outputs_are_current(self):
        result = MODULE.build()
        self.assertEqual(MODULE.render_json(result), MODULE.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_doc(result, False), MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_doc(result, True), MODULE.DOC_RU.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
