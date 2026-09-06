import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_placement.py"
SVG = ROOT / "docs/images/h6-r2-exact-placement.svg"
KICAD_PYTHON = Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/"
    "Versions/3.9/bin/python3"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class H6R2PlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_exact_placement_closes_every_schematic_instance(self):
        self.assertEqual("pass", self.audit["status"])
        self.assertEqual([], self.audit["errors"])
        self.assertEqual(
            {
                "board_count": 2,
                "board_outline_mm": [80.0, 150.0],
                "copper_layers_per_board": 6,
                "schematic_instance_count": 1208,
                "placed_instance_count": 1208,
                "hard_conflict_count": 0,
                "placement_failure_count": 0,
                "net_or_footprint_error_count": 0,
                "locality_pair_count": 310,
                "locality_violation_count": 0,
                "critical_pad_pair_count": 22,
                "critical_pad_pair_violation_count": 0,
                "accepted_same_face_overlap_count": 2,
                "routing_authorized": True,
                "routing_started": True,
            },
            self.audit["summary"],
        )
        boards = {row["project"]: row for row in self.audit["boards"]}
        self.assertEqual(428, boards["LESHY2-UI-R2"]["placed_instance_count"])
        self.assertEqual(780, boards["LESHY2-RF-R2"]["placed_instance_count"])

    def test_local_parts_stay_with_their_physical_owners(self):
        self.assertEqual(310, self.audit["summary"]["locality_pair_count"])
        self.assertEqual(0, self.audit["summary"]["locality_violation_count"])
        rows = {}
        for board in self.audit["boards"]:
            self.assertEqual("pass", board["locality"]["status"])
            self.assertEqual([], board["locality"]["violations"])
            rows.update({row["instance"]: row for row in board["locality"]["rows"]})
        for instance, limit in self.contract["placement_policy"]["locality_max_gap_mm"].items():
            self.assertIn(instance, rows)
            self.assertLessEqual(rows[instance]["courtyard_gap_mm"], limit)
        self.assertEqual("main_buck", rows["main_buck_bootstrap_cap"]["owner"])
        self.assertEqual("main_fb_top", rows["main_ff_cap"]["owner"])
        self.assertEqual("voice_inductor", rows["voice_output_cap0"]["owner"])

    def test_switching_nodes_and_selected_bypasses_use_actual_pad_distances(self):
        switching_nodes = {
            "AON_BUCK_SW",
            "CHARGER_BTST1",
            "CHARGER_BTST2",
            "CHARGER_PMID",
            "CHARGER_REGN",
            "CHARGER_SW1",
            "CHARGER_SW2",
            "EXT_BUCK_SW",
            "HUB_RP_VREG_LX_SW",
            "MAIN_BUCK_BST",
            "MAIN_BUCK_BST_LINK",
            "MAIN_BUCK_SW",
            "NVDC_SYS",
            "PACK_CHARGE_PUMP",
            "RF_RP_VREG_LX_SW",
            "VOICE_BUCK_SW",
        }
        rows = []
        for board in self.audit["boards"]:
            pad_audit = board["critical_pad_pairs"]
            self.assertEqual("pass", pad_audit["status"])
            self.assertEqual([], pad_audit["errors"])
            self.assertEqual([], pad_audit["violations"])
            rows.extend(pad_audit["rows"])
        self.assertEqual(22, len(rows))
        self.assertEqual(
            switching_nodes,
            switching_nodes & {row["canonical_net"] for row in rows},
        )
        for row in rows:
            self.assertLessEqual(
                row["pad_centre_distance_mm"], row["maximum_distance_mm"]
            )

    def test_pack_high_current_parts_target_their_exact_holder_terminals(self):
        rows = {}
        for board in self.audit["boards"]:
            rows.update({row["instance"]: row for row in board["locality"]["rows"]})
        expected = {
            "pack_fuse0": ([33.44, 126.0], 2.0),
            "pack_fuse1": ([52.54, 126.0], 2.0),
            "pack_shunt": ([33.44, 44.0], 4.0),
        }
        for instance, (anchor, limit) in expected.items():
            self.assertEqual(
                "owner_shared_pad_anchor_to_child_courtyard",
                rows[instance]["measurement"],
            )
            self.assertEqual(anchor, rows[instance]["owner_shared_pad_anchor_mm"])
            self.assertLessEqual(rows[instance]["courtyard_gap_mm"], limit)

    def test_power_islands_and_touch_buffer_use_reviewed_locality_anchors(self):
        expected = {
            "aon_buck": [50.7, 84.5],
            "aon_input_cap": [50.945, 87.045],
            "aon_output_cap": [45.795, 83.945],
            "charger_pmid_cap0": [71.945, 65.595],
            "charger_pmid_hf_cap": [70.245, 67.4],
            "charger_sys_hf_cap": [61.975, 67.4],
            "ext_buck": [30.35, 132.0],
            "ext_buck_hf_input_cap": [28.2, 130.2],
            "ext_buck_input_cap": [25.4, 130.945],
            "ext_buck_fb_bottom": [28.2, 132.075],
            "main_buck": [13.0, 126.0],
            "nvdc_charger": [66.0, 70.5],
            "voice_buck": [66.5, 111.5],
            "touch_irq_buffer": [38.5, 28.0],
        }
        for instance, centre in expected.items():
            self.assertEqual(
                centre,
                self.contract["placement_overrides"][instance]["centre_mm"],
            )
        self.assertEqual(
            180.0,
            self.contract["placement_overrides"]["aon_input_cap"]["rotation_deg"],
        )
        self.assertEqual(
            270.0,
            self.contract["placement_overrides"]["aon_output_cap"]["rotation_deg"],
        )
        self.assertEqual(
            0.0,
            self.contract["placement_overrides"]["ext_buck"]["rotation_deg"],
        )
        self.assertEqual(
            180.0,
            self.contract["placement_overrides"]["ext_buck_hf_input_cap"]["rotation_deg"],
        )
        self.assertEqual([], self.contract["placement_policy"]["released_instances"])
        self.assertEqual(
            {"LESHY2-UI-R2": [], "LESHY2-RF-R2": []},
            self.contract["placement_policy"]["released_reference_prefixes_by_project"],
        )

    def test_native_boards_and_six_layer_headers_match_the_placement_audit(self):
        for board in self.audit["boards"]:
            path = ROOT / board["output"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(64, len(board["unrouted_seed_sha256"]))
            self.assertEqual(64, len(board["placement_signature_sha256"]))
            text = path.read_text(encoding="utf-8")
            self.assertIn('(0 "F.Cu" signal)', text)
            self.assertIn('(4 "In1.Cu" signal)', text)
            self.assertIn('(6 "In2.Cu" signal)', text)
            self.assertIn('(8 "In3.Cu" signal)', text)
            self.assertIn('(10 "In4.Cu" signal)', text)
            self.assertIn('(2 "B.Cu" signal)', text)
            self.assertEqual(
                board["placed_instance_count"],
                text.count('property "Leshy2Instance"'),
                "every schematic footprint must retain its exact hierarchy identity",
            )

    def test_user_critical_datums_are_exact_and_symmetric(self):
        expected_x = [16.5, 28.25, 40.0, 51.75, 63.5]
        for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
            self.assertEqual(
                expected_x,
                [point[0] for point in self.contract["antenna_ports"][project].values()],
            )
            self.assertTrue(
                all(point[1] == 0.0 for point in self.contract["antenna_ports"][project].values())
            )
        display = self.contract["mechanical"]["display_bed"]
        self.assertEqual([11.73, 68.27], display["panel_bbox_mm"]["x"])
        self.assertEqual([19.0, 103.96], display["panel_bbox_mm"]["y"])
        self.assertEqual(5.0, display["minimum_relaxed_slack_mm"])
        self.assertEqual(
            [40.0, 35.4],
            self.contract["placement_overrides"]["display_connector"]["centre_mm"],
        )
        self.assertEqual(90.0, self.contract["placement_overrides"]["encoder"]["rotation_deg"])

    def test_battery_holder_is_shifted_clear_of_the_interboard_locator(self):
        self.assertEqual(
            [42.99, 85.0],
            self.contract["mechanical"]["rear_battery_holder"]["centre_mm"],
        )
        rf = next(row for row in self.audit["boards"] if row["project"] == "LESHY2-RF-R2")
        holder = next(row for row in rf["placements"] if row["reference"] == "BT1")
        self.assertEqual([42.99, 85.0], holder["footprint_anchor_mm"])

    def test_each_pack_ntc_is_directly_below_its_own_cell(self):
        rf = next(row for row in self.audit["boards"] if row["project"] == "LESHY2-RF-R2")
        placements = {row["instance"]: row for row in rf["placements"]}
        self.assertEqual([33.44, 85.0], placements["pack_ntc0"]["courtyard_centre_mm"])
        self.assertEqual([52.54, 85.0], placements["pack_ntc1"]["courtyard_centre_mm"])
        self.assertEqual("F.Cu", placements["pack_ntc0"]["side"])
        self.assertEqual("F.Cu", placements["pack_ntc1"]["side"])
        self.assertEqual(
            {("pack_ntc0", "pack_holder"), ("pack_ntc1", "pack_holder")},
            {
                (row["instance"], row["owner"])
                for row in rf["accepted_same_face_overlaps"]
            },
        )
        holder_footprint = (
            ROOT / "hardware/ecad/libraries/Leshy2.pretty/Keystone-1048P.kicad_mod"
        ).read_text(encoding="utf-8")
        self.assertIn('(start -43.000 -19.900) (end 43.000 19.900)', holder_footprint)
        self.assertNotIn('layer "F.CrtYd"', holder_footprint)
        self.assertIn("H6 placement audit enforces the complete F.Fab body", holder_footprint)
        board_text = (ROOT / rf["output"]).read_text(encoding="utf-8")
        holder_start = board_text.index('(footprint "Leshy2:Keystone-1048P"')
        holder_end = board_text.index("\n\t(footprint ", holder_start + 1)
        self.assertNotIn('layer "F.CrtYd"', board_text[holder_start:holder_end])
        self.assertIn('(gr_text "NTC0 PAD"', board_text)
        self.assertIn('(gr_text "NTC1 PAD"', board_text)

    def test_factory_stack_candidate_is_the_current_1p6_mm_six_layer_stack(self):
        stack = self.contract["board"]["factory_stack_candidate"]
        self.assertEqual("JLCPCB", stack["manufacturer"])
        self.assertEqual("JLC06161H-3313", stack["official_stackup_id"])
        self.assertEqual(1.6, stack["order_thickness_mm"])
        self.assertEqual(1.54, stack["calculator_finished_thickness_mm"])
        self.assertEqual(10, stack["calculator_finished_thickness_tolerance_percent"])
        self.assertEqual(0.035, stack["outer_copper_mm"])
        self.assertEqual(0.0152, stack["inner_copper_mm"])
        self.assertEqual("3313 x1, 0.0994 mm nominal", stack["outer_prepreg"])
        self.assertEqual("2116 x1, 0.1088 mm nominal", stack["inner_prepreg"])
        self.assertEqual(0.55, stack["core_each_mm"])
        self.assertEqual("https://jlcpcb.com/pcb-impedance-calculator/", stack["source"])
        self.assertEqual("2026-09-03", stack["verified_at"])

    def test_generation_is_byte_reproducible_when_kicad_python_is_available(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad bundled pcbnew Python is unavailable")
        result = subprocess.run(
            [str(KICAD_PYTHON), str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("1208/1208 positions; 0 hard conflicts; 0 unplaced", result.stdout)

    def test_placement_signature_ignores_tracks_but_detects_footprint_movement(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad bundled pcbnew Python is unavailable")
        board_path = ROOT / self.audit["boards"][0]["output"]
        code = f"""
import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, {str(SCRIPT.parent)!r})
import h6_r2_placement as placement
path = Path({str(board_path)!r})
board = pcbnew.LoadBoard(str(path))
baseline = placement.placement_signature_bytes(path.stem, board)
track = pcbnew.PCB_TRACK(board)
track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(2), pcbnew.FromMM(1)))
track.SetWidth(pcbnew.FromMM(0.2))
track.SetLayer(pcbnew.F_Cu)
board.Add(track)
assert placement.placement_signature_bytes(path.stem, board) == baseline
footprint = next(iter(board.GetFootprints()))
position = footprint.GetPosition()
footprint.SetPosition(pcbnew.VECTOR2I(position.x + pcbnew.FromMM(0.1), position.y))
assert placement.placement_signature_bytes(path.stem, board) != baseline
"""
        result = subprocess.run(
            [str(KICAD_PYTHON), "-c", code],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)

    def test_kicad_cli_parses_both_native_boards(self):
        cli = shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("kicad-cli is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            for board in self.audit["boards"]:
                source = ROOT / board["output"]
                output = Path(directory) / f"{board['project']}.csv"
                result = subprocess.run(
                    [
                        cli,
                        "pcb",
                        "export",
                        "pos",
                        "--side",
                        "both",
                        "--format",
                        "csv",
                        "--units",
                        "mm",
                        "-o",
                        str(output),
                        str(source),
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.assertEqual(0, result.returncode, result.stdout)
                self.assertTrue(output.is_file(), board["project"])

    def test_preview_is_current_and_states_that_it_remains_the_placement_authority(self):
        self.assertTrue(SVG.is_file())
        text = SVG.read_text(encoding="utf-8")
        self.assertIn("H6.0.1 exact-footprint placement", text)
        self.assertIn("placement authority for routed boards", text)
        self.assertIn("428 positions", text)
        self.assertIn("780 positions", text)


if __name__ == "__main__":
    unittest.main()
