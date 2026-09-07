import importlib.util
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "user_silk", ROOT / "hardware/layout/h6_r2_user_silkscreen.py")
SILK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SILK)


class UserSilkscreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / "hardware/layout/h6-r2-placement-contract.json").read_text())
        cls.boards = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())["boards"]

    def test_antenna_labels_follow_identity_not_list_or_dictionary_order(self):
        board = next(b for b in self.boards if b["project"] == "LESHY2-RF-R2")
        contract = copy.deepcopy(self.contract)
        ports = contract["antenna_ports"][board["project"]]
        contract["antenna_ports"][board["project"]] = dict(reversed(list(ports.items())))
        found = {r["instance"]: r for r in SILK.labels(board["project"], list(reversed(board["placements"])), contract)
                 if r["role"] == "antenna"}
        self.assertEqual(("UHF TX", [51.75, 15.2]),
                         (found["voice_external_sma"]["text"], found["voice_external_sma"]["at_mm"]))
        self.assertEqual(("VHF TX", [63.5, 15.2]),
                         (found["voice_v_external_sma"]["text"], found["voice_v_external_sma"]["at_mm"]))
        rows = copy.deepcopy(board["placements"])
        next(r for r in rows if r["instance"] == "voice_external_sma")["footprint_anchor_mm"][0] = 52.0
        label = next(r for r in SILK.labels(board["project"], rows, contract) if r["instance"] == "voice_external_sma")
        self.assertEqual([52.0, 15.2], label["at_mm"])

    def test_all_ten_path_names_agree_with_the_h1_identity_not_position(self):
        placement = json.loads((ROOT / "hardware/product-design/h1-r2-placement.json").read_text())
        h1 = {r["path"]: r["text"] for face in ("front", "rear") for r in placement["antenna_silkscreen"][face]}
        self.assertEqual(10, len(SILK.ANTENNA_INTERFACES))
        self.assertEqual(h1, {path: text for path, text, _ in SILK.ANTENNA_INTERFACES.values()})

    def test_signal_identity_requires_the_actual_pad_not_just_label(self):
        board = next(b for b in self.boards if b["project"] == "LESHY2-RF-R2")
        rows = copy.deepcopy(board["placements"])
        for row in rows:
            if row["instance"] in SILK.ANTENNA_INTERFACES:
                row["signal_pad_nets"] = [SILK.ANTENNA_INTERFACES[row["instance"]][2]]
        self.assertEqual([], SILK.antenna_signal_findings(board["project"], rows, self.contract))
        uhf = next(r for r in rows if r["instance"] == "voice_external_sma")
        for wrong in ([], ["VOICE_V_EXTERNAL_RF_50R"], ["POWER_GROUND"], ["VOICE_U_EXTERNAL_RF_50R"] * 2):
            uhf["signal_pad_nets"] = wrong
            found = SILK.antenna_signal_findings(board["project"], rows, self.contract)
            self.assertEqual(1, len(found))
            self.assertEqual("antenna_signal_identity_mismatch", found[0]["kind"])


    def test_every_service_button_has_two_outer_face_labels(self):
        for board in self.boards:
            labels = SILK.labels(board["project"], board["placements"], self.contract)
            for instance, spec in self.contract["service_buttons"]["by_project"][board["project"]].items():
                found = [row for row in labels if row["instance"] == instance]
                self.assertEqual(2, len(found))
                self.assertEqual({"F.Silkscreen"}, {row["layer"] for row in found})
                self.assertEqual({6.0 if spec["edge"] == "left" else 74.0}, {row["at_mm"][0] for row in found})
                self.assertAlmostEqual(2.1, found[1]["at_mm"][1] - found[0]["at_mm"][1])

    def test_all_four_usb_paths_have_their_real_role_and_uniform_rows(self):
        found = {}
        for board in self.boards:
            rows = {row["instance"]: row for row in board["placements"]}
            for label in SILK.labels(board["project"], board["placements"], self.contract):
                if label["instance"] in SILK.USB_OWNERS:
                    found.setdefault(label["instance"], []).append(label)
                    self.assertEqual(rows[label["instance"]]["courtyard_centre_mm"][0], label["at_mm"][0])
        self.assertEqual(set(SILK.USB_OWNERS), set(found))
        for instance, rows in found.items():
            self.assertEqual(list(SILK.USB_OWNERS[instance]), [row["text"] for row in rows])
            self.assertEqual([138.0, 140.0], [row["at_mm"][1] for row in rows])
        self.assertEqual(1, sum(row["text"] == "POWER + USB" for rows in found.values() for row in rows))

    def test_all_ten_indicators_are_labelled_at_actual_positions(self):
        # Independent accepted interface name: IEEE 802.15.4, not "5.4".
        self.assertEqual("Wi-Fi/15.4", SILK.INDICATORS["c5_tx_led"])
        board = next(row for row in self.boards if row["project"] == "LESHY2-UI-R2")
        labels = SILK.labels(board["project"], board["placements"], self.contract)
        rows = {row["instance"]: row for row in board["placements"]}
        for instance, text in SILK.INDICATORS.items():
            found = [row for row in labels if row["instance"] == instance]
            self.assertEqual(1, len(found))
            self.assertEqual(text, found[0]["text"])
            x, y = rows[instance]["courtyard_centre_mm"]
            self.assertEqual(x, found[0]["at_mm"][0])
            self.assertAlmostEqual(y + 2.3, found[0]["at_mm"][1])

    def test_missing_interface_fails_closed_instead_of_silently_omitting_label(self):
        board = self.boards[0]
        rows = [row for row in board["placements"] if row["instance"] != "s3_reset_button"]
        with self.assertRaises(KeyError):
            SILK.labels(board["project"], rows, self.contract)

    def test_labels_keep_native_production_text_minima(self):
        for board in self.boards:
            for row in SILK.labels(board["project"], board["placements"], self.contract):
                self.assertGreaterEqual(row["size_mm"], 1.0)
                self.assertGreaterEqual(row["thickness_mm"], 0.15)


if __name__ == "__main__":
    unittest.main()
