"""Copy-only CLI contract tests: no router, native KiCad, network or production writes."""
from contextlib import redirect_stdout
from copy import deepcopy
import fcntl
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools import route_board as cli


def checked_summary(case, target=2):
    grade = {key: True for key in ("geometry_pass", "candidate_pass", "preservation_recipe_pass",
                                   "dependencies_unchanged", "selected_complete", "drc_checked",
                                   "candidate_unchanged_during_checks")}
    grade.update(selected_remaining=[target, 0], native_unconnected=[10, 10-target],
                 resolved_connections=target, drc_violations=0, schematic_parity_errors=0,
                 failures={}, roi_escaped_objects=[], electrically_qualified=False,
                 drc_selected_unconnected=0, kicad_version="10.0.5",
                 added_geometry_signature="a" * 64)
    runs = []
    for index in range(4):
        profile = {"id": "seed" if index == 0 else f"seed-replay{index}"}
        if index:
            profile["replay_of"] = "seed"
        runs.append({"profile": profile, "repeat": 1, "geometry_pass": True,
                     "engine": {"exit_code": 0}, "validation_process": {"exit_code": 0},
                     "validation": deepcopy(grade)})
    return {"case": case["id"], "candidate_only": True, "production_promoted": False,
            "electrically_qualified": False, "fixture": None, "runs": runs,
            "best_initial_profile": {"id": "seed"}, "best_initial_geometry_signature": "a" * 64,
            "replay_pass": True}


class RouteBoardCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.layout = self.root / "hardware/layout"
        self.layout.mkdir(parents=True)
        self.controller = self.layout / "h6_r2_autorouter_benchmark.py"
        for name in (self.controller.name, "h6-r2-autorouter-profile.json",
                     "h6_r2_benchmark_profiles.py", "h6_r2_route_candidate.py"):
            (self.layout / name).write_text(name)
        self.patch = patch.multiple(cli, ROOT=self.root, LAYOUT=self.layout, CONTROLLER=self.controller)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.paths = [self.make_case("first", "LESHY2-UI-R2", "/EXACT_NET")]
        self.mutate_summary = lambda summary: None
        self.mutate_files = lambda output: None
        self.provenance_effect = None
        self.calls = []

    def make_case(self, name, project, net):
        board = Path("hardware/ecad/kicad") / project / (project + ".kicad_pcb")
        (self.root / board).parent.mkdir(parents=True, exist_ok=True)
        (self.root / board).write_text("unchanged source board")
        case = {"schema_version": 1, "id": name, "project": project,
                "scope": {"expected_connections": 2}, "baseline_sha256": {str(board): cli.sha(self.root / board)},
                "profiles": [{"id": "seed"}], "engine_timeout_seconds": 10, "validation_timeout_seconds": 10,
                "nets": [{"project": project, "kicad_net": net,
                          "exact_ref_pads": ["U1.1", "R1.2", "R2.1"], "remaining_connections": 2}]}
        path = self.layout / (name + ".json")
        path.write_text(json.dumps(case))
        return path

    def fake_controller(self, command, *, cwd, stdout, stderr):
        self.assertEqual(self.root, cwd)
        self.assertEqual(subprocess.STDOUT, stderr)
        self.calls.append(command)
        case_path = Path(command[command.index("--case") + 1])
        case = json.loads(case_path.read_text())
        output = Path(tempfile.mkdtemp(prefix="routing-benchmark-", dir=self.root / "work"))
        (output / "case.json").write_bytes(case_path.read_bytes())
        summary = checked_summary(case)
        summary.update(baseline_inputs=case["baseline_sha256"], case_sha256=cli.sha(case_path),
                       controller_sha256=cli.sha(self.controller),
                       profile_sha256=cli.sha(self.layout / "h6-r2-autorouter-profile.json"),
                       profile_policy_sha256=cli.sha(self.layout / "h6_r2_benchmark_profiles.py"),
                       grader_sha256=cli.sha(self.layout / "h6_r2_route_candidate.py"))
        self.mutate_summary(summary)
        for row in summary["runs"]:
            attempt = output / (row["profile"]["id"] + "-1")
            candidate = attempt / next(iter(case["baseline_sha256"]))
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text("new candidate geometry")
            row["candidate"] = str(candidate)
            row["validation"]["candidate_sha256"] = cli.sha(candidate)
            (attempt / "work").mkdir()
            native = attempt / "work/native-drc.json"
            native.write_text(json.dumps({"violations": [{}] * row["validation"]["drc_violations"],
                "schematic_parity": [{}] * row["validation"]["schematic_parity_errors"],
                "kicad_version": row["validation"]["kicad_version"]}))
            receipt = native.with_name(native.name + ".provenance.json")
            receipt.write_text("mocked native receipt")
            row["validation"].update(drc_report_sha256=cli.sha(native), drc_receipt_sha256=cli.sha(receipt))
            (attempt / "validation.json").write_text(json.dumps(row["validation"]))
        summary_path = output / "summary.json"
        summary_path.write_text(json.dumps(summary))
        stdout.write(json.dumps({"output": str(output), "case": case["id"]}) + "\n")
        stdout.write(json.dumps({"summary": str(summary_path), "summary_sha256": cli.sha(summary_path)}) + "\n")
        self.mutate_files(output)
        return subprocess.CompletedProcess(command, 0)

    def invoke(self, extra=()):
        stream = io.StringIO()
        argv = [arg for path in self.paths for arg in ("--case", str(path))] + list(extra)
        def controller(command, stream, power):
            return self.fake_controller(command, cwd=cli.ROOT, stdout=stream, stderr=subprocess.STDOUT)
        with patch.object(cli, "run_controller", side_effect=controller), \
                patch.object(cli.sys, "platform", "linux"), \
                patch.object(cli, "validate_provenance", side_effect=self.provenance_effect) as provenance, \
                redirect_stdout(stream):
            code = cli.main(argv)
        self.provenance_calls = provenance.call_count
        lines = stream.getvalue().splitlines()
        self.assertEqual(1, len(lines))
        return code, json.loads(lines[0])

    def test_two_boards_are_serial_and_counted_once_with_relative_evidence(self):
        self.paths.append(self.make_case("second", "LESHY2-RF-R2", "/EXACT_NET"))
        code, result = self.invoke(["--max-seconds", "30", "--engine", str(self.root / "engine"),
                                    "--engine-python", str(self.root / "python")])
        self.assertEqual(0, code)
        self.assertEqual((2, 4, 0), (result["accepted_cases"], result["resolved"], result["remaining_targeted"]))
        self.assertEqual(2, len(self.calls))
        self.assertEqual(8, self.provenance_calls)
        for command in self.calls:
            self.assertIn("--adaptive", command)
            self.assertIn("--quiet", command)
            self.assertEqual("3", command[command.index("--repeat-best") + 1])
            self.assertEqual("30", command[command.index("--max-seconds") + 1])
        for row in result["cases"]:
            self.assertFalse(Path(row["log"]).is_absolute())
            self.assertFalse(Path(row["summary"]).is_absolute())
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["electrically_qualified"])
        self.assertEqual(2, len(result["blockers"]))
        self.assertEqual("unsupported_not_needed", result["sleep_prevention"]["status"])

    def test_same_project_overlap_rejected_before_subprocess(self):
        self.paths.append(self.make_case("overlap", "LESHY2-UI-R2", "/EXACT_NET"))
        code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertIn("overlap", result["error"])
        self.assertEqual([], self.calls)

    def test_disjoint_same_project_and_explicit_search_modes(self):
        self.paths.append(self.make_case("disjoint", "LESHY2-UI-R2", "/OTHER_NET"))
        for mode in ("--sweep", "--portfolio"):
            with self.subTest(mode=mode):
                self.assertEqual(0, self.invoke([mode])[0])
                self.assertIn(mode, self.calls[-1])
                self.assertNotIn("--adaptive", self.calls[-1])

    def test_missing_or_invalid_replays_never_trust_summary_boolean(self):
        for change in (lambda s: s["runs"].pop(),
                       lambda s: s["runs"][-1]["validation"].update(drc_checked=False),
                       lambda s: s["runs"][-1]["validation"].update(added_geometry_signature="b" * 64),
                       lambda s: s["runs"][-1]["profile"].update(replay_of="another-profile"),
                       lambda s: s["runs"][-1]["validation"].update(selected_remaining=[2, 1]),
                       lambda s: s["runs"][-1]["validation"].update(drc_selected_unconnected=1),
                       lambda s: s["runs"][-1]["validation"].update(kicad_version="10.0.4"),
                       lambda s: s.update(budget_exhausted=True)):
            with self.subTest(change=change):
                self.mutate_summary = change
                code, result = self.invoke()
                self.assertEqual(1, code)
                self.assertEqual(0, result["resolved"])

    def test_native_failures_are_reported_and_rejected(self):
        self.mutate_summary = lambda s: s["runs"][-1]["validation"].update(drc_violations=2, schematic_parity_errors=1)
        code, result = self.invoke()
        self.assertEqual((1, 2, 1), (code, result["native_drc_failures"], result["parity_failures"]))
        self.assertEqual((0, 2), (result["resolved"], result["best_partial_resolved"]))

    def test_timeout_fails_and_does_not_launch_next_board(self):
        self.paths.append(self.make_case("second", "LESHY2-RF-R2", "/OTHER_NET"))
        self.mutate_summary = lambda s: s["runs"][0]["engine"].update(exit_code="timeout")
        code, result = self.invoke()
        self.assertEqual((1, 1, 4), (code, len(self.calls), result["remaining_targeted"]))

    def test_stale_tampered_missing_and_candidate_changed_evidence_fail_closed(self):
        changes = [lambda output: os.utime(output / "summary.json", (1, 1)),
                   lambda output: (output / "summary.json").write_text("{}"),
                   lambda output: (output / "summary.json").unlink(),
                   lambda output: (output / "case.json").write_text("{}"),
                   lambda output: next(output.glob("seed-1/**/*.kicad_pcb")).write_text("tampered"),
                   lambda output: (output / "seed-1/validation.json").write_text("{}"),
                   lambda output: (output / "seed-1/work/native-drc.json").write_text("{}"),
                   lambda output: (output / "seed-1/work/native-drc.json.provenance.json").write_text("{}")]
        for change in changes:
            with self.subTest(change=change):
                self.mutate_files = change
                code, result = self.invoke()
                self.assertEqual(1, code)
                self.assertIn("error", result["cases"][0])

    def test_hash_mismatch_and_invalid_endpoints_fail_before_execution(self):
        original = json.loads(self.paths[0].read_text())
        for change in (lambda c: c["baseline_sha256"].update({next(iter(c["baseline_sha256"])): "0" * 64}),
                       lambda c: c["nets"][0].update(exact_ref_pads=["missing-pad-number"]),
                       lambda c: c["nets"][0].update(kicad_net="/WILDCARD_*"),
                       lambda c: c["scope"].update(expected_connections=99)):
            with self.subTest(change=change):
                case = deepcopy(original)
                change(case)
                self.paths[0].write_text(json.dumps(case))
                self.assertEqual(1, self.invoke()[0])
                self.assertEqual([], self.calls)

    def test_duplicate_pad_numbers_remain_a_valid_multiset(self):
        case = json.loads(self.paths[0].read_text())
        case["nets"][0]["exact_ref_pads"] = ["U1.1", "U1.1", "R1.2"]
        self.paths[0].write_text(json.dumps(case))
        self.assertEqual(0, self.invoke()[0])

    def test_provenance_mismatch_or_failed_controller_rejected(self):
        self.mutate_summary = lambda s: s.update(controller_sha256="0" * 64)
        self.assertEqual(1, self.invoke()[0])
        self.fake_controller = lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1)
        code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertIn("Controller failed", result["cases"][0]["error"])

    def test_native_provenance_validator_rejection_is_not_ignored(self):
        # Preserve the minimal fixture, but reject it as the real validator
        # would if a candidate dependency or receipt command were altered.
        self.provenance_effect = ValueError("Native provenance rejected")
        code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertGreater(self.provenance_calls, 0)
        self.assertIn("Native provenance rejected", result["cases"][0]["error"])

    def test_second_wrapper_cannot_overlap_native_execution(self):
        (self.root / "work").mkdir()
        with (self.root / "work/route-board.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertIn("error", result)
        self.assertEqual([], self.calls)

    def test_missing_native_gate_and_boolean_exit_code_fail_closed(self):
        case = json.loads(self.paths[0].read_text())
        for key in ("candidate_unchanged_during_checks", "drc_checked", "drc_selected_unconnected",
                    "dependencies_unchanged", "preservation_recipe_pass", "failures"):
            with self.subTest(key=key):
                summary = checked_summary(case)
                del summary["runs"][-1]["validation"][key]
                self.assertFalse(cli.assess(summary, case, 2)["accepted"])
        summary = checked_summary(case)
        summary["runs"][-1]["engine"]["exit_code"] = False
        self.assertFalse(cli.assess(summary, case, 2)["accepted"])

    def test_cancelled_cli_returns_json_and_restores_sigterm_handler(self):
        before = signal.getsignal(signal.SIGTERM)
        def cancelled_controller(*args, **kwargs):
            signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
        self.fake_controller = cancelled_controller
        code, result = self.invoke()
        self.assertEqual(130, code)
        self.assertTrue(result["cancelled"])
        self.assertFalse(result["replay_passed"])
        self.assertIs(before, signal.getsignal(signal.SIGTERM))


class IdleSleepLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.power = Mock(pid=23456)
        self.power.poll.return_value = None
        self.power.wait.return_value = 0
        self.state = {}
        self.patch = patch.multiple(cli, ROOT=self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.platform = patch.object(cli.sys, "platform", "darwin")
        self.platform.start()
        self.addCleanup(self.platform.stop)
        self.spawn = patch.object(cli.subprocess, "Popen", return_value=self.power)
        self.popen = self.spawn.start()
        self.addCleanup(self.spawn.stop)
        self.probe = patch.object(cli.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, stdout="   pid 23456(caffeinate): [0x1] 00:00:00 PreventUserIdleSystemSleep named: assertion\n"))
        self.pmset = self.probe.start()
        self.addCleanup(self.probe.stop)

    def test_assertion_is_pid_scoped_verified_and_released_without_display_flag(self):
        with cli.keep_awake(self.state, self.root) as power:
            self.assertIs(power, self.power)
            self.assertTrue(self.state["active"])
            self.assertTrue(self.state["established"])
            self.power.terminate.assert_not_called()
        command = self.popen.call_args.args[0]
        self.assertEqual(["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())], command)
        self.assertTrue(self.popen.call_args.kwargs["start_new_session"])
        self.assertEqual(["/usr/bin/pmset", "-g", "assertions"], self.pmset.call_args.args[0])
        self.power.terminate.assert_called_once_with()
        self.power.wait.assert_called_once_with(timeout=3)
        self.assertEqual("released", self.state["status"])
        self.assertFalse(self.state["active"])
        self.assertTrue(self.state["display_sleep_allowed"])

    def test_error_and_keyboard_cancellation_release_assertion(self):
        for error in (ValueError("case failure"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__):
                self.power.reset_mock()
                with self.assertRaises(type(error)):
                    with cli.keep_awake(self.state, self.root):
                        raise error
                self.power.terminate.assert_called_once_with()
                self.assertFalse(self.state["active"])

    def test_missing_caffeinate_fails_visibly(self):
        self.popen.side_effect = FileNotFoundError("caffeinate unavailable")
        with self.assertRaisesRegex(FileNotFoundError, "caffeinate unavailable"):
            with cli.keep_awake(self.state, self.root):
                self.fail("Cannot run an unprotected macOS benchmark")
        self.assertEqual("failed", self.state["status"])
        self.assertFalse(self.state["established"])

    def test_unverified_or_foreign_assertion_is_rejected_and_cleaned(self):
        self.pmset.return_value.stdout = "pid 99999(caffeinate): PreventUserIdleSystemSleep\n"
        with patch.object(cli.time, "monotonic", side_effect=[0, 0, 4]), patch.object(cli.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "did not establish"):
                with cli.keep_awake(self.state, self.root):
                    self.fail("Another process's assertion does not satisfy this invocation")
        self.power.terminate.assert_called_once_with()
        self.assertEqual("failed", self.state["status"])

    def test_failed_pmset_probe_releases_caffeinate(self):
        self.pmset.side_effect = subprocess.TimeoutExpired("pmset", 2)
        with self.assertRaisesRegex(RuntimeError, "Cannot verify"):
            with cli.keep_awake(self.state, self.root):
                self.fail("Unverified assertion must fail closed")
        self.power.terminate.assert_called_once_with()

    def test_non_macos_reports_unsupported_without_processes(self):
        with patch.object(cli.sys, "platform", "linux"):
            with cli.keep_awake(self.state, self.root) as power:
                self.assertIsNone(power)
        self.assertEqual("unsupported_not_needed", self.state["status"])
        self.popen.assert_not_called()
        self.pmset.assert_not_called()

    def test_early_caffeinate_exit_is_rejected(self):
        self.power.poll.return_value = 1
        with self.assertRaisesRegex(RuntimeError, "did not establish"):
            with cli.keep_awake(self.state, self.root):
                self.fail("Exited caffeinate must never count as an assertion")
        self.assertFalse(self.state["established"])

    def test_controller_cancellation_waits_for_cleanup_and_force_kills_only_if_stuck(self):
        controller = Mock()
        controller.poll.return_value = None
        self.popen.return_value = controller
        for waits, force in (([KeyboardInterrupt(), 0], False),
                             ([KeyboardInterrupt(), subprocess.TimeoutExpired("controller", 10), 0], True)):
            with self.subTest(force=force):
                controller.reset_mock()
                controller.wait.side_effect = waits
                with self.assertRaises(KeyboardInterrupt):
                    cli.run_controller(["python", "controller.py"], io.StringIO(), self.power)
                controller.terminate.assert_called_once_with()
                self.assertEqual(force, controller.kill.called)
                self.assertIn((((), {"timeout": 10})), controller.wait.call_args_list)
        self.assertTrue(self.popen.call_args.kwargs["start_new_session"])

    def test_lost_assertion_stops_controller(self):
        controller = Mock()
        controller.poll.return_value = None
        controller.wait.return_value = 0
        self.popen.return_value = controller
        self.power.poll.return_value = 1
        with self.assertRaisesRegex(RuntimeError, "caffeinate exited while routing"):
            cli.run_controller(["python", "controller.py"], io.StringIO(), self.power)
        controller.terminate.assert_called_once_with()

    def test_controller_success_does_not_send_stop_signal(self):
        controller = Mock()
        controller.wait.return_value = 0
        self.popen.return_value = controller
        result = cli.run_controller(["python", "controller.py"], io.StringIO(), self.power)
        self.assertEqual(0, result.returncode)
        controller.terminate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
