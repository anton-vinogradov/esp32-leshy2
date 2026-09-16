"""Real tiny Python process groups; no engine, KiCad, network or signal handlers in workers."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from hardware.layout.h6_r2_parallel_process import ProcessRegistry


CHILD = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('ready',flush=True); time.sleep(60)"
LEADER = """import json,os,signal,subprocess,sys,time
signal.signal(signal.SIGTERM, lambda *args: print('TERM',flush=True))
child = subprocess.Popen([sys.executable, '-u', '-c', sys.argv[1]], stdout=subprocess.PIPE, text=True)
assert child.stdout.readline().strip() == 'ready'
print(json.dumps({'leader':os.getpid(),'child':child.pid,'group':os.getpgrp()}),flush=True)
if sys.argv[2] != 'success': time.sleep(60)
"""


@unittest.skipUnless(os.name == "posix", "Process-group adapter targets POSIX")
class ParallelProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / "phase.log"
        self.registry = ProcessRegistry(grace_seconds=0.15)
        self.addCleanup(self.registry.cancel_all)

    def command(self, mode="wait"):
        return [sys.executable, "-u", "-c", LEADER, CHILD, mode]

    def wait_ready(self, log=None):
        log = log or self.log
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if log.exists():
                for line in log.read_text().splitlines():
                    if line.startswith("{"):
                        return json.loads(line)
            time.sleep(0.01)
        self.fail("Synthetic leader did not become ready")

    def assert_stopped(self, pid):
        # We reap our direct Popen child. On POSIX only the adopting OS parent
        # can reap an orphan grandchild; a zombie is already terminated.
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            stat = Path(f"/proc/{pid}/stat")
            if stat.exists():  # Linux containers may retain adopted zombies.
                try:
                    if stat.read_text().rsplit(") ", 1)[1].startswith("Z"):
                        return
                except FileNotFoundError:
                    return
            time.sleep(0.01)
        self.fail(f"Synthetic process {pid} is still running")

    def assert_cleaned(self, evidence):
        self.assert_stopped(evidence["leader"])
        self.assert_stopped(evidence["child"])
        self.assertEqual(0, self.registry.active_count)
        with self.assertRaises(ChildProcessError):
            os.waitpid(evidence["leader"], os.WNOHANG)

    def test_successful_leader_cannot_leave_ignoring_child_running(self):
        result = self.registry.run(self.command("success"), self.log, 3)
        evidence = self.wait_ready()
        self.assertEqual(0, result["exit_code"])
        self.assertEqual(evidence["leader"], evidence["group"])
        self.assertNotEqual(os.getpgrp(), evidence["group"])
        self.assert_cleaned(evidence)

    def test_timeout_terminates_group_then_kills_and_reaps(self):
        result = self.registry.run(self.command(), self.log, 0.4)
        evidence = self.wait_ready()
        self.assertEqual("timeout", result["exit_code"])
        self.assertEqual(-signal.SIGKILL, result["returncode"])
        self.assertLess(result["seconds"], 2)
        self.assertEqual(1, self.log.read_text().splitlines().count("TERM"))
        self.assert_cleaned(evidence)

    def test_registry_cancel_is_idempotent_and_does_not_install_thread_signals(self):
        with ThreadPoolExecutor(max_workers=1) as caller, patch.object(
                signal, "signal", side_effect=AssertionError("worker installed signal handler")), \
                patch("hardware.layout.h6_r2_parallel_process.os.killpg", wraps=os.killpg) as signals:
            future = caller.submit(self.registry.run, self.command(), self.log, 5)
            evidence = self.wait_ready()
            for _ in range(5):
                self.registry.cancel_all()
            result = future.result(timeout=2)
        sent = [call.args[1] for call in signals.call_args_list]
        self.assertEqual(1, sent.count(signal.SIGTERM))
        self.assertEqual(1, sent.count(signal.SIGKILL))
        self.assertEqual("cancelled", result["exit_code"])
        self.assertEqual(1, self.log.read_text().splitlines().count("TERM"))
        self.assert_cleaned(evidence)

    def test_event_cancellation_cleans_all_registered_groups(self):
        logs = [self.root / f"phase-{index}.log" for index in range(2)]
        with ThreadPoolExecutor(max_workers=2) as caller:
            futures = [caller.submit(self.registry.run, self.command(), log, 5) for log in logs]
            evidence = [self.wait_ready(log) for log in logs]
            self.assertEqual(2, self.registry.active_count)
            self.registry.cancel_event.set()
            results = [future.result(timeout=2) for future in futures]
        self.assertEqual(["cancelled", "cancelled"], [r["exit_code"] for r in results])
        for group in evidence:
            self.assert_cleaned(group)

    def test_exception_after_spawn_still_cleans_group_before_propagating(self):
        def faulty_wait(group, deadline):
            self.wait_ready()
            raise RuntimeError("injected wait failure")
        with patch.object(self.registry, "_wait", side_effect=faulty_wait):
            with self.assertRaisesRegex(RuntimeError, "injected wait failure"):
                self.registry.run(self.command(), self.log, 5)
        self.assert_cleaned(self.wait_ready())

    def test_keyboard_interrupt_also_cleans_group(self):
        def interrupted_wait(group, deadline):
            self.wait_ready()
            raise KeyboardInterrupt()
        with patch.object(self.registry, "_wait", side_effect=interrupted_wait):
            with self.assertRaises(KeyboardInterrupt):
                self.registry.run(self.command(), self.log, 5)
        self.assert_cleaned(self.wait_ready())

    def test_pre_cancelled_registry_never_spawns(self):
        self.registry.cancel_all()
        with patch("hardware.layout.h6_r2_parallel_process.subprocess.Popen") as spawn:
            result = self.registry.run(self.command(), self.log, 1)
        spawn.assert_not_called()
        self.assertEqual("cancelled", result["exit_code"])
        self.assertIsNone(result["pid"])

    def test_nonzero_exit_and_combined_log_preserve_result(self):
        command = [sys.executable, "-u", "-c", "import sys; print('stdout'); print('stderr',file=sys.stderr); sys.exit(7)"]
        result = self.registry.run(command, self.log, 2)
        self.assertEqual(7, result["exit_code"])
        self.assertEqual(7, result["returncode"])
        self.assertEqual({"stdout", "stderr"}, set(self.log.read_text().splitlines()))
        self.assertEqual(0, self.registry.active_count)

    def test_spawn_or_log_failure_leaves_registry_empty(self):
        with self.assertRaises(OSError):
            self.registry.run([str(self.root / "missing-program")], self.log, 1)
        with self.assertRaises(OSError):
            self.registry.run(self.command(), self.root / "missing/log", 1)
        self.assertEqual(0, self.registry.active_count)

    def test_bad_time_limits_and_shell_strings_rejected(self):
        for limit in (0, -1, True, float("inf"), float("nan")):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.registry.run(self.command(), self.log, limit)
        for grace in (-1, True, float("inf")):
            with self.subTest(grace=grace), self.assertRaises(ValueError):
                ProcessRegistry(grace_seconds=grace)
        with self.assertRaises(ValueError):
            self.registry.run("echo shell", self.log, 1)


if __name__ == "__main__":
    unittest.main()
