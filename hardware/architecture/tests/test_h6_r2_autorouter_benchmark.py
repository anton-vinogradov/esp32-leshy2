"""Controller guard tests without an engine, KiCad or network."""
from pathlib import Path
import json
import tempfile
import unittest

from hardware.layout.h6_r2_autorouter_benchmark import restore_dependencies, select_best, sha
from hardware.layout.h6_r2_benchmark_profiles import adaptive_fallback, sweep_profiles


class BenchmarkControllerTests(unittest.TestCase):
    def test_larger_case_retains_reviewed_keys_and_exact_scope_counts(self):
        cases = Path(__file__).resolve().parents[2] / "layout/benchmarks"
        old = json.loads((cases / "ui-controls-60.json").read_text())
        large = json.loads((cases / "ui-inputs-service-id-82.json").read_text())
        self.assertEqual(old["baseline_sha256"], large["baseline_sha256"])
        by_name = {n["kicad_net"]: n for n in large["nets"]}
        self.assertEqual(29, len(by_name))
        self.assertEqual(82, sum(n["remaining_connections"] for n in large["nets"]))
        self.assertEqual(111, sum(len(n["exact_ref_pads"]) for n in large["nets"]))
        for net in old["nets"]:
            self.assertEqual(net, by_name[net["kicad_net"]])
        self.assertFalse(large["scope_review"]["production_authorization"])

    def test_adaptive_search_keeps_quality_gate_and_deduplicates_seed(self):
        seed = {"id": "known", "grid_step": 0.05, "via_cost": 75, "ordering": "mps"}
        self.assertEqual(12, len(sweep_profiles()))
        # Connectivity alone (or engine success) must not suppress fallback.
        fallback = adaptive_fallback(seed, [{"geometry_pass": False, "resolved": 82}])
        self.assertEqual(11, len(fallback))
        self.assertEqual([], adaptive_fallback(seed, [{"geometry_pass": True}]))
        self.assertFalse(any(p["grid_step"] == 0.05 and p["via_cost"] == 75
                             and p["ordering"] == "mps" for p in fallback))

    def test_selection_never_rewards_fast_incomplete_candidate(self):
        def result(passed, vias, length, seconds):
            return {"geometry_pass": passed, "validation": {"new_vias": vias,
                    "new_trace_length_mm": length}, "end_to_end_seconds": seconds}
        rejected = result(False, 0, 0, 0.1)
        longer = result(True, 5, 120, 3)
        winner = result(True, 5, 100, 9)
        more_vias = result(True, 6, 80, 1)
        self.assertIs(winner, select_best([rejected, longer, winner, more_vias]))
        self.assertIsNone(select_best([rejected]))

    def test_restore_modified_and_deleted_dependencies_but_never_board(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, candidate = root / "baseline", root / "candidate"
            baseline.mkdir()
            candidate.mkdir()
            for name in ("board.kicad_pcb", "board.kicad_pro", "board.kicad_dru"):
                (baseline / name).write_text("original " + name)
            hashes = {p.name: sha(p) for p in baseline.iterdir()}
            (candidate / "board.kicad_pcb").write_text("candidate copper")
            (candidate / "board.kicad_pro").write_text("weakened rules")
            changed = restore_dependencies(baseline, candidate, hashes, "board.kicad_pcb")
            self.assertEqual({"board.kicad_pro", "board.kicad_dru"}, set(changed))
            self.assertEqual("candidate copper", (candidate / "board.kicad_pcb").read_text())
            self.assertEqual([], restore_dependencies(baseline, candidate, hashes, "board.kicad_pcb"))
            for name in changed:
                self.assertEqual(hashes[name], sha(candidate / name))


if __name__ == "__main__":
    unittest.main()
