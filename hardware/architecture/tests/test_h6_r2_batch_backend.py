"""Cold-copy and fail-closed backend tests; no KiCad, router or network needed."""
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import Mock, patch

from hardware.layout import h6_r2_batch_backend as backend


class BatchBackendTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.layout = self.root / "hardware/layout"
        self.code = self.layout / "h6_r2_batch_backend.py"
        self.profile = self.layout / "profile.json"
        self.case_path = self.layout / "benchmarks/synthetic.json"
        self.project = "LESHY2-UI-R2"
        self.board = Path(f"hardware/ecad/kicad/{self.project}/{self.project}.kicad_pcb")
        self.inputs = [self.board, self.board.with_suffix(".kicad_pro")]
        for project in backend.inventory.PROJECTS:
            self.put(self.root / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb", "original PCB")
        self.put(self.root / self.inputs[1], "original rules")
        self.put(self.code, "frozen backend source")
        self.put(self.root / "engine-python", "fixture interpreter")
        self.put(self.profile, {"engine": {"source_commit": "pinned", "entrypoint": "py_router/route.py",
                                          "macos_arm64_binary_sha256": "a" * 64},
                               "execution": {"arguments": backend.STRICT_ARGUMENTS, "environment": {},
                                             "fab_overrides_file_contents": "via_diameter = 0.4\n"}})
        self.put(self.case_path, {"id": "synthetic", "project": self.project,
                 "nets": [{"kicad_net": n, "remaining_connections": 1, "exact_ref_pads": ["J1.1", "J2.1"]}
                          for n in ("A", "B")], "scope": {"expected_connections": 2},
                 "baseline_sha256": {str(p): backend.sha(self.root / p) for p in self.inputs}})
        for target, value in (("ROOT", self.root), ("PROFILE", self.profile), ("__file__", str(self.code)),
                              ("_engine_pins", Mock()), ("verified_sources", Mock()),
                              ("input_hashes", lambda project, root: {str(p): backend.sha(Path(root) / p) for p in self.inputs})):
            guard = patch.object(backend, target, value)
            guard.start()
            self.addCleanup(guard.stop)
        guard = patch.object(backend.inventory, "expected_inventory", return_value=([], {}, []))
        guard.start()
        self.addCleanup(guard.stop)
        self.auth = backend.authority(self.case_path, engine_root=self.root / "engine",
                                      engine_python=self.root / "engine-python", engine_patch_sha256="b" * 64)
        self.registry = Mock(cancel_event=Event())
        self.registry.run.side_effect = self.process
        self.sequence = 0

    @staticmethod
    def put(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, dict) else value)

    def process(self, command, log, timeout, **kwargs):
        if "--prove" in command:
            context = backend.read(Path(command[-1]))
            self.put(Path(context["folder"]) / "baseline-proof.json", {
                "baseline_sha256": self.auth["baseline_inputs"][str(self.board)],
                "exact_endpoints_checked": True, "native_version": "10.0.5",
                "selected_remaining": [2, 2], "selected_original_copper_and_zones": {"A": 0, "B": 0}})
        elif "--native-probe" in command:
            context = backend.read(Path(command[-1]))
            report = Path(context["baseline_root"]) / "work/preflight-drc.json"
            self.put(report, {"kicad_version": "10.0.5", "violations": [], "schematic_parity": [],
                              "unconnected_items": [{}, {}]})
            self.put(report.with_name(report.name + ".provenance.json"), {"synthetic": True})
        return {"exit_code": 0, "returncode": 0, "pid": 123, "seconds": 0.01}

    def prepare(self, recipe=None):
        self.sequence += 1
        return backend.prepare(self.auth, recipe or backend.Recipe("cold"),
                               self.root / "work" / f"cold-{self.sequence}", self.registry)

    def test_recipe_rejects_unbounded_or_arbitrary_controls(self):
        for field, value in (("direction", "sideways"), ("ordering", "random"), ("grid_step", .001),
                             ("via_cost", True), ("max_ripup", 500), ("blocker_select", "shell"),
                             ("max_iterations", -1), ("dynamic_iterations_grace", True),
                             ("rip_selected", 1), ("clearance", .1), ("clearance", float("nan")),
                             ("board_edge_clearance", .2), ("board_edge_clearance", float("inf"))):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                backend.Recipe("bounded", **{field: value})
        with self.assertRaises(TypeError):
            backend.Recipe("bounded", extra_arguments=["--relax-drc-severities"])

    def test_cold_prepare_copies_sources_and_freezes_exact_recipe(self):
        recipe = backend.Recipe("ordered", ordering="original", net_order=["B", "A"], rip_selected=True,
                                max_ripup=5, blocker_select="mincut", max_iterations=1000000,
                                dynamic_iterations_grace=2)
        context = self.prepare(recipe)
        self.assertTrue(context["prepared"])
        self.assertEqual(asdict(recipe), context["recipe"])
        for name in self.inputs:
            original = (self.root / name).read_bytes()
            for key in ("baseline_root", "candidate_root"):
                copied = Path(context[key]) / name
                self.assertEqual(original, copied.read_bytes())
                self.assertNotEqual((self.root / name).stat().st_ino, copied.stat().st_ino)
        command = context["command"]
        self.assertEqual(["B", "A"], command[command.index("--nets") + 1:command.index("--layers")])
        self.assertIn("--no-fix-drc-settings", command)
        self.assertEqual(["--rip-existing-nets", "B", "A"], command[-3:])
        self.assertEqual("2", context["environment"]["KICAD_DYNAMIC_ITERATIONS_GRACE"])
        self.assertEqual("0", context["environment"]["KICAD_SMOOTH_ROUTE"])
        self.assertEqual("0", context["environment"]["KICAD_INRUN_FLOOR_SYNC"])
        backend.check_context(context)

    def test_net_order_requires_exact_permutation_before_native_process(self):
        for order in (["A", "A"], ["A"], ["A", "B", "C"], ["A", "*"]):
            self.registry.run.reset_mock()
            with self.subTest(order=order), self.assertRaisesRegex(ValueError, "exact case permutation"):
                self.prepare(backend.Recipe("bad-order", net_order=order))
            self.registry.run.assert_not_called()

    def test_existing_output_cannot_be_reused_as_a_cold_attempt(self):
        context = self.prepare()
        with self.assertRaisesRegex(ValueError, "not empty"):
            backend.prepare(self.auth, backend.Recipe("again"), context["folder"], self.registry)

    def test_tampered_copy_or_source_blocks_engine_before_spawn(self):
        for relative in ("candidate/" + str(self.board), "candidate/" + str(self.inputs[1]), "case.json", "backend.py"):
            context = self.prepare()
            self.put(Path(context["folder"]) / relative, "tampered")
            self.registry.run.reset_mock()
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                backend.engine(context, self.registry)
            self.registry.run.assert_not_called()
        context = self.prepare()
        self.put(self.code, "changed authoritative code")
        self.registry.run.reset_mock()
        with self.assertRaisesRegex(ValueError, "Authority"):
            backend.engine(context, self.registry)
        self.registry.run.assert_not_called()

    def test_failed_baseline_proof_is_not_prepared(self):
        self.registry.run.side_effect = lambda *a, **k: {"exit_code": -6}
        with self.assertRaisesRegex(ValueError, "baseline proof failed"):
            self.prepare()

    def test_engine_cannot_reseal_settings_mutated_during_execution(self):
        for on_disk in (False, True):
            self.registry.run.side_effect = self.process
            context = self.prepare()
            def mutate(*args, **kwargs):
                if on_disk:
                    self.put(Path(context["receipt_path"]), {"tampered": True})
                else:
                    context["recipe"]["via_cost"] = 125
                    context["command"][context["command"].index("--via-cost") + 1] = "125"
                return {"exit_code": 0}
            self.registry.run.side_effect = mutate
            with self.subTest(on_disk=on_disk), self.assertRaises(ValueError):
                backend.engine(context, self.registry)
            self.assertFalse((Path(context["folder"]) / "engine-context.json").exists())

    def test_only_fine_grid_can_use_extended_engine_budget(self):
        context = self.prepare()
        self.registry.run.reset_mock()
        with self.assertRaises(ValueError):
            backend.engine(context, self.registry, timeout=1800)
        self.registry.run.assert_not_called()
        context = self.prepare(backend.Recipe("fine", grid_step=.025))
        backend.engine(context, self.registry, timeout=1800)
        self.assertEqual(1800, self.registry.run.call_args.args[2])
        context = self.prepare(backend.Recipe("fine-too-long", grid_step=.025))
        self.registry.run.reset_mock()
        with self.assertRaises(ValueError):
            backend.engine(context, self.registry, timeout=1801)
        self.registry.run.assert_not_called()

    def test_bus_order_and_abandon_metric_are_explicit_bounded_options(self):
        for metric in ("stranded", "total-pads"):
            context = self.prepare(backend.Recipe("bus", ordering="bus", abandon_metric=metric))
            command = context["command"]
            self.assertEqual("bus", command[command.index("--ordering") + 1])
            self.assertEqual(metric, command[command.index("--ripup-abandon-metric") + 1])
        with self.assertRaises(ValueError):
            backend.Recipe("bad-metric", abandon_metric="anything")

    def test_worker_request_tamper_and_stale_native_receipt_block_validation(self):
        context = backend.engine(self.prepare(), self.registry)
        request = Path(context["folder"]) / "worker-request.json"
        self.put(request, {"case": "/another/case.json"})
        self.registry.run.reset_mock()
        with self.assertRaisesRegex(ValueError, "Worker request"):
            backend.validate(context, self.registry)
        self.registry.run.assert_not_called()
        context = backend.engine(self.prepare(), self.registry)
        self.put(Path(context["candidate_root"]) / "validation.json", {})
        self.registry.run.reset_mock()
        with self.assertRaisesRegex(ValueError, "stale/repeated"):
            backend.validate(context, self.registry)
        self.registry.run.assert_not_called()

    def test_failed_native_worker_never_runs_inventory_or_returns_pass(self):
        context = backend.engine(self.prepare(), self.registry)
        self.registry.run.reset_mock()
        self.registry.run.side_effect = lambda *a, **k: {"exit_code": -6}
        with self.assertRaisesRegex(ValueError, "native worker failed"):
            backend.validate(context, self.registry)
        self.assertEqual(1, self.registry.run.call_count)

    def test_preflight_uses_bounded_registry_and_baseline_copy_provenance(self):
        context = self.prepare()
        self.registry.run.reset_mock()
        with patch.object(backend, "validate_provenance") as provenance, \
                patch.object(backend, "_native_lock", wraps=backend._native_lock) as lock:
            result = backend.preflight(context, self.registry, timeout=17)
        self.assertTrue(result["pass"])
        self.assertEqual(2, result["native_unconnected"])
        self.assertEqual(1, self.registry.run.call_count)
        command, log, timeout = self.registry.run.call_args.args
        self.assertIn("--native-probe", command)
        self.assertEqual((context["receipt_path"], 17), (command[-1], timeout))
        baseline = Path(context["baseline_root"])
        provenance.assert_called_once_with(baseline / "work/preflight-drc.json", self.project, baseline)
        lock.assert_called_once()
        self.assertIs(self.registry.cancel_event, lock.call_args.args[0])
        with self.assertRaisesRegex(ValueError, "already exists"):
            backend.preflight(context, self.registry)

    def test_preflight_failure_timeout_and_cancellation_never_pass(self):
        context = self.prepare()
        self.registry.run.reset_mock()
        with self.assertRaisesRegex(ValueError, "bounded"):
            backend.preflight(context, self.registry, timeout=181)
        self.registry.cancel_event.set()
        with self.assertRaisesRegex(ValueError, "Cancelled"):
            backend.preflight(context, self.registry)
        self.registry.run.assert_not_called()
        self.registry.cancel_event.clear()
        for code in (-6, "timeout", False):
            self.registry.run.side_effect = lambda *a, **k: {"exit_code": code}
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "preflight failed"):
                backend.preflight(context, self.registry)
        self.assertFalse((Path(context["folder"]) / "preflight-result.json").exists())

    def test_geometry_gate_rejects_roi_regressions_and_malformed_counts(self):
        flags = ("geometry_pass", "candidate_pass", "selected_complete", "drc_checked",
                 "candidate_unchanged_during_checks", "preservation_recipe_pass", "dependencies_unchanged")
        grade = dict.fromkeys(flags, True)
        grade.update(selected_remaining=[2, 0], kicad_version="10.0.5", electrically_qualified=False,
                     drc_selected_unconnected=0, drc_violations=0, schematic_parity_errors=0,
                     failures={}, roi_escaped_objects=[], all_net_regressions={},
                     native_unconnected=[12, 10], resolved_connections=2, added_geometry_signature="a" * 64)
        self.assertTrue(backend.geometry_pass(grade, 2))
        for key, value in (("roi_escaped_objects", ["escape"]), ("all_net_regressions", {"other-net": [1, 2]}),
                           ("drc_violations", False), ("drc_violations", 1), ("drc_checked", False),
                           ("selected_remaining", [2, 1]), ("selected_remaining", [2, False]),
                           ("dependencies_unchanged", False), ("native_unconnected", [12, 12]),
                           ("resolved_connections", True), ("added_geometry_signature", "not-a-sha")):
            with self.subTest(key=key, value=value):
                self.assertFalse(backend.geometry_pass({**grade, key: value}, 2))


if __name__ == "__main__":
    unittest.main()
