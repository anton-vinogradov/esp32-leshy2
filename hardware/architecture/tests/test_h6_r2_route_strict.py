"""Negative tests: corruption must not masquerade as a routed candidate."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

from hardware.layout.h6_r2_autorouter_benchmark import execute
from hardware.layout.h6_r2_benchmark_profiles import adaptive_fallback, freeze_net_order, portfolio_profiles
from hardware.layout.h6_r2_route_candidate import drc_selected_open, grade_candidate


class StrictTests(unittest.TestCase):
    def test_cli_connections_are_bound_to_native_uuids(self):
        finding = {"items": [{"uuid": "p1"}, {"uuid": "p2"}]}
        report = {"unconnected_items": [finding]}
        self.assertEqual(1, drc_selected_open(report, {"p1": "A", "p2": "A"}, {"A"}))
        self.assertEqual(0, drc_selected_open(report, {"p1": "B", "p2": "B"}, {"A"}))
        for broken in ({}, {"unconnected_items": None}, {"unconnected_items": [{}]}, report):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                drc_selected_open(broken, {}, {"A"})

    def test_portfolio_never_relaxes_geometry_and_freezes_feedback_order(self):
        profiles = portfolio_profiles()
        self.assertEqual(8, len(profiles))
        self.assertFalse(any("layers" in p or "track_width" in p or "clearance" in p for p in profiles))
        rows = [{"kicad_net": "A"}, {"kicad_net": "B"}]
        history = [{"validation": {"resolved_connections": 5, "per_net": {"A": [1, 0], "B": [2, 1]}}}]
        frozen = freeze_net_order(profiles[2], rows, history)
        self.assertEqual(["B", "A"], frozen["net_order"])
        self.assertEqual(frozen, freeze_net_order(frozen, rows, []))
        with self.assertRaises(ValueError):
            freeze_net_order({"net_order": ["A", "A"]}, rows, [])
        self.assertEqual(11, len(adaptive_fallback(freeze_net_order(profiles[0], rows, []), [])))

    def test_timeout_reaps_child(self):
        with tempfile.TemporaryDirectory() as directory:
            result = execute([sys.executable, "-c", "import time; time.sleep(10)"],
                             Path(directory) / "child.log", 0.03)
            self.assertEqual("timeout", result["exit_code"])

    def test_native_mutations_fail_closed_without_modifying_source(self):
        try:
            import pcbnew
        except ImportError:
            self.skipTest("KiCad Python required")
        with tempfile.TemporaryDirectory() as directory:
            baseline, candidate = Path(directory) / "old.kicad_pcb", Path(directory) / "new.kicad_pcb"
            board = pcbnew.BOARD()
            board.SetCopperLayerCount(6)
            for name, y, start in (("A", 10, 1), ("B", 20, 3)):
                net = pcbnew.NETINFO_ITEM(board, name)
                board.Add(net)
                for offset, x in enumerate((10, 20)):
                    fp = pcbnew.FOOTPRINT(board)
                    fp.SetReference(f"J{start + offset}")
                    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
                    board.Add(fp)
                    pad = pcbnew.PAD(fp)
                    pad.SetNumber("1")
                    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
                    pad.SetSize(pcbnew.VECTOR2I_MM(1, 1))
                    layers = pcbnew.LSET()
                    layers.AddLayer(pcbnew.F_Cu)
                    pad.SetLayerSet(layers)
                    pad.SetPosition(fp.GetPosition())
                    pad.SetNet(net)
                    fp.Add(pad)
            pcbnew.SaveBoard(str(baseline), board)
            text = baseline.read_text()
            old = ('(segment (start 10 20) (end 20 20) (width 0.15) (layer "F.Cu") '
                   '(net "B") (uuid "a81de09a-e855-492f-8d15-64cf441f2a7b"))')
            source = text[:text.rfind(")")] + old + ")\n"
            baseline.write_text(source)
            digest = hashlib.sha256(baseline.read_bytes()).hexdigest()
            route = ('(segment (start 10 10) (end 20 10) (width 0.15) (layer "F.Cu") '
                     '(net "A") (uuid "88e6b797-2e20-4bc5-91c6-f74af9e8e8b2"))')
            valid = source[:source.rfind(")")] + route + ")\n"
            rows = [{"kicad_net": "A", "exact_ref_pads": ["J1.1", "J2.1"], "remaining_connections": 1}]
            candidate.write_text(valid)
            self.assertTrue(grade_candidate(baseline, candidate, rows, digest)["candidate_pass"])
            mutations = {
                "reserved layer": valid.replace(route, route.replace('"F.Cu"', '"In1.Cu"')),
                "wrong width": valid.replace(route, route.replace("width 0.15", "width 0.10")),
                "wrong net": valid.replace(route, route.replace('net "A"', 'net "B"')),
                "old copper removed": valid.replace(old, ""),
                "old copper changed": valid.replace(old, old.replace("width 0.15", "width 0.2")),
                "disconnected endpoint": valid.replace(route, route.replace("end 20 10", "end 15 10")),
                "moved footprint": valid.replace("(at 10 10)", "(at 11 10)", 1),
                "unrequested zone": valid[:valid.rfind(")")] + '(gr_text "changed" (at 0 0) (layer "User.1"))' + ")",
            }
            for label, altered in mutations.items():
                with self.subTest(label=label):
                    self.assertNotEqual(valid, altered)
                    candidate.write_text(altered)
                    self.assertFalse(grade_candidate(baseline, candidate, rows, digest)["candidate_pass"])
                    self.assertEqual(source, baseline.read_text())
            candidate.write_text(valid)
            self.assertFalse(grade_candidate(baseline, candidate, rows, "0" * 64)["candidate_pass"])
