"""Controller guard tests without an engine, KiCad or network."""
from pathlib import Path
import tempfile
import unittest

from hardware.layout.h6_r2_autorouter_benchmark import restore_dependencies, select_best, sha


class BenchmarkControllerTests(unittest.TestCase):
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
