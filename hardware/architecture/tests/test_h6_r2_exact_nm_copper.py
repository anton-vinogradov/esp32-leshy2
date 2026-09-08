"""One exact detector path, no global rounding or copper-signature tolerance."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

try:
    import pcbnew as native
except ImportError:
    native = None

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("exact_nm_manual_copper", ROOT / "hardware/layout/h6_r2_manual_copper.py")
copper = importlib.util.module_from_spec(SPEC)
placement_stub = types.ModuleType("h6_r2_placement")
placement_stub.build = Mock(side_effect=AssertionError("no placement generation in this test"))
with patch.dict(sys.modules, {"pcbnew": types.ModuleType("pcbnew"), "h6_r2_placement": placement_stub}):
    SPEC.loader.exec_module(copper)

PROJECT = "LESHY2-UI-R2"
NET = "/UI_10_S3_DISPLAY_TOUCH/S3_FORWARD_RF_SAMPLE"
POINTS = [[30780000, 4950000], [32362500, 4950000]]


def route():
    return {"id": "UI-S3-DETECTOR-SAMPLE", "project": PROJECT,
            "canonical_net": "S3_FORWARD_RF_SAMPLE", "kicad_net": NET,
            "routing_class": "RF_CONTROLLED", "layer": "B.Cu", "width_mm": 0.134874,
            "path_nm": copy.deepcopy(POINTS), "expected_resolved_connections": 1,
            "reason": "Exact reviewed detector endpoints, not blanket rounding."}


class ExactNanometreValidationTests(unittest.TestCase):
    def test_reviewed_current_record_uses_only_exact_integer_path(self):
        rows=json.loads((ROOT / "hardware/layout/h6-r2-manual-copper.json").read_text())["routes"]
        exact=[r for r in rows if "path_nm" in r]
        self.assertEqual(len(exact),1)
        self.assertEqual(exact[0]["id"],"UI-S3-DETECTOR-SAMPLE")
        self.assertEqual(exact[0]["path_nm"],POINTS)
        self.assertNotIn("path_mm",exact[0])
        copper.preflight_exact_nm_paths(rows)

    def test_good_path_including_multiple_points(self):
        r=route();copper.preflight_exact_nm_paths([r],PROJECT)
        r["path_nm"].insert(1,[31500000,4950000])
        copper.preflight_exact_nm_paths([r],PROJECT)

    def test_exact_identity_cannot_be_reused_on_other_net_project_layer_or_width(self):
        replacements={"id":"OTHER", "project":"LESHY2-RF-R2", "canonical_net":"OTHER",
                      "kicad_net":"/OTHER/S3_FORWARD_RF_SAMPLE", "routing_class":"GENERAL_CONTROL",
                      "layer":"F.Cu", "width_mm":0.15}
        for key,value in replacements.items():
            with self.subTest(key=key):
                r=route();r[key]=value
                with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])
        with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([route()],"LESHY2-RF-R2")

    def test_missing_integer_path_does_not_fall_back_to_millimetres(self):
        r=route();del r["path_nm"];r["path_mm"]=[[30.78,4.95],[32.3625,4.95]]
        with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])

    def test_competing_geometry_and_vias_are_rejected_even_if_empty(self):
        for key in ("path_mm","segments","vias"):
            with self.subTest(key=key):
                r=route();r[key]=[]
                with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])

    def test_nanometres_are_true_int32_not_bool_float_string_or_overflow(self):
        for value in (True,False,30780000.0,"30780000",None,float("nan"),2**31,-2**31-1):
            with self.subTest(value=value):
                r=route();r["path_nm"][0][0]=value
                with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])

    def test_point_and_path_shapes_fail_closed(self):
        for value in (None,[],[POINTS[0]],"bad",[POINTS[0],[]],[POINTS[0],[1,2,3]],
                      [POINTS[0],(1,2)],[POINTS[0],POINTS[0]]):
            with self.subTest(value=value):
                r=route();r["path_nm"]=value
                with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])

    def test_expected_connection_count_is_exact_integer_one(self):
        for value in (True,1.0,0,2,None):
            r=route();r["expected_resolved_connections"]=value
            with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])

    def test_review_reason_required_before_mutation(self):
        for value in (None,""," "):
            r=route();r["reason"]=value
            with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r])

    def test_duplicate_id_or_net_rejected(self):
        r=route()
        with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r,copy.deepcopy(r)])
        other={"id":"OTHER", "project":PROJECT,"kicad_net":NET}
        with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r,other])
        other={"id":r["id"],"project":"LESHY2-RF-R2","kicad_net":"OTHER"}
        with self.assertRaises(ValueError):copper.preflight_exact_nm_paths([r,other])

    def test_bad_late_record_rejected_before_any_native_mutation(self):
        board=Mock();bad=route();bad["path_nm"][1][0]=True
        ordinary={"id":"ordinary", "project":PROJECT,"routing_class":"RF_CONTROLLED"}
        with self.assertRaises(ValueError):copper.add_routes(board,[ordinary,bad],{},PROJECT,{})
        self.assertEqual(board.mock_calls,[])

    def test_foreign_project_record_rejected_before_placement_generation(self):
        r=route();r["project"]="UNKNOWN"
        with patch.object(copper,"load",side_effect=[{"routes":[r]},{"rows":[]},
                {"classes":{"RF_CONTROLLED":{"reviewed_outer_layer_transitions":{}}}}]):
            with self.assertRaises(ValueError):copper.build()
        placement_stub.build.assert_not_called()


@unittest.skipUnless(native is not None,"KiCad pcbnew runtime required")
class ExactNanometreNativeReplayTests(unittest.TestCase):
    def test_exact_native_endpoint_not_the_legacy_float_truncation(self):
        self.assertEqual(native.VECTOR2I_MM(32.3625,4.95).x,32362499)
        vector=native.VECTOR2I(*POINTS[1])
        self.assertEqual((vector.x,vector.y),(32362500,4950000))

    def test_full_replay_both_boards_preserves_exact_signature_without_native_writes(self):
        contract=json.loads((ROOT / "hardware/layout/h6-r2-manual-copper.json").read_text())
        routing=json.loads((ROOT / "hardware/layout/h6-r2-routing-policy.json").read_text())
        policy=json.loads((ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json").read_text())
        rows={(r["project"],r["kicad_net"]):r for r in policy["rows"]}
        transitions=routing["classes"]["RF_CONTROLLED"]["reviewed_outer_layer_transitions"]
        with patch.object(sys,"path",[str(ROOT / "hardware/layout"),*sys.path]):
            import h6_r2_stage_placement_update as native_stage
        for project in ("LESHY2-UI-R2","LESHY2-RF-R2"):
            with self.subTest(project=project),patch.object(copper,"pcbnew",native):
                path=ROOT/f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
                before=hashlib.sha256(path.read_bytes()).hexdigest()
                existing=native.LoadBoard(str(path));expected=copper.copper_signature(existing)
                text=path.read_text()
                # Load a separate copper-free seed instead of mutating native
                # connectivity caches while retaining detached SWIG objects.
                for form in native_stage.copper_forms(text):text=text.replace(form,"",1)
                with tempfile.TemporaryDirectory(prefix="h6-exact-nm-replay-") as directory:
                    seed=Path(directory)/path.name;seed.write_text(text)
                    board=native.LoadBoard(str(seed))
                selected=[r for r in contract["routes"] if r["project"]==project]
                audit=copper.add_routes(board,selected,rows,project,transitions,routing)
                self.assertEqual(copper.copper_signature(board),expected)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
                if project==PROJECT:
                    proof=next(r for r in audit if r["id"]=="UI-S3-DETECTOR-SAMPLE")
                    self.assertEqual(proof["coordinate_representation"],"integer_nanometres")
                    self.assertEqual(proof["path_nm"],POINTS)
                    self.assertEqual(proof["length_mm"],1.5825)
                    self.assertEqual(proof["resolved_connections"],1)
                    item=next(t for t in board.GetTracks() if t.GetNetname()==NET)
                    self.assertEqual([item.GetStart().x,item.GetStart().y],POINTS[0])
                    self.assertEqual([item.GetEnd().x,item.GetEnd().y],POINTS[1])


if __name__=="__main__":unittest.main()
