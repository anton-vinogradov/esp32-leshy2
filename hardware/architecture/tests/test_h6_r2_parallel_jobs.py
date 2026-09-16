"""Scheduler tests with bounded synthetic callbacks; no subprocess/router/DRC."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, Lock
import unittest

from hardware.layout.h6_r2_parallel_jobs import PhaseResult, run_jobs


class ParallelJobTests(unittest.TestCase):
    def test_validation_wait_never_occupies_engine_slot(self):
        validation_started, engines_drained = Event(), Event()

        def engine(job):
            if job == 1:
                self.assertTrue(validation_started.wait(2))
            if job == 4:
                engines_drained.set()
            return PhaseResult(True, job * 10)

        def validate(job, value):
            self.assertEqual(job * 10, value)
            if job == 0:
                validation_started.set()
                self.assertTrue(engines_drained.wait(2))
            return PhaseResult(True, {"checked": job})

        results = run_jobs(range(5), engine, validate, max_workers=1)
        self.assertEqual(["accepted"] * 5, [row["status"] for row in results])
        self.assertEqual(list(range(5)), [row["job"] for row in results])

    def test_engines_obey_bound_and_validation_is_serial(self):
        gate, all_engines_done, first_validation = Event(), Event(), Event()
        first_wave = Barrier(3)
        lock = Lock()
        active, peak, completed, validation_calls = 0, 0, 0, []

        def engine(job):
            nonlocal active, peak, completed
            with lock:
                active += 1
                peak = max(peak, active)
            if job < 3:
                first_wave.wait(timeout=2)
            with lock:
                active -= 1
                completed += 1
                if completed == 12:
                    all_engines_done.set()
            return PhaseResult(True, job)

        def validate(job, value):
            with lock:
                validation_calls.append(job)
            first_validation.set()
            self.assertTrue(gate.wait(2))
            return PhaseResult(True, value)

        with ThreadPoolExecutor(max_workers=1) as caller:
            future = caller.submit(run_jobs, range(12), engine, validate, max_workers=3)
            try:
                self.assertTrue(first_validation.wait(2))
                self.assertTrue(all_engines_done.wait(2))
                with lock:
                    self.assertEqual(3, peak)
                    self.assertEqual(1, len(validation_calls))
            finally:
                gate.set()
            results = future.result(timeout=2)
        self.assertTrue(all(row["accepted"] for row in results))
        self.assertEqual(list(range(12)), [row["index"] for row in results])

    def test_later_engine_can_validate_before_first_engine_finishes(self):
        second_validated = Event()

        def engine(job):
            if job == "slow":
                self.assertTrue(second_validated.wait(2))
            return PhaseResult(True, job)

        def validate(job, value):
            if job == "fast":
                second_validated.set()
            return PhaseResult(True, value)

        rows = run_jobs(["slow", "fast"], engine, validate, max_workers=2)
        self.assertEqual(["slow", "fast"], [row["job"] for row in rows])
        self.assertTrue(all(row["accepted"] for row in rows))

    def test_failures_are_recorded_without_validation_or_queue_stall(self):
        validated = []

        def engine(job):
            if job == 0:
                return PhaseResult(False, {"exit_code": 2})
            if job == 1:
                raise OSError("engine unavailable")
            return PhaseResult(True, job)

        def validate(job, value):
            validated.append(job)
            if job == 2:
                return PhaseResult(False, {"drc": 1})
            if job == 3:
                raise ValueError("stale evidence")
            return PhaseResult(True, value)

        rows = run_jobs(range(5), engine, validate, max_workers=2)
        self.assertEqual(["engine_failed", "engine_failed", "validation_failed", "validation_failed", "accepted"],
                         [row["status"] for row in rows])
        self.assertEqual({2, 3, 4}, set(validated))
        self.assertEqual({"exit_code": 2}, rows[0]["engine"])
        self.assertIn("engine unavailable", rows[1]["error"])
        self.assertIn("stale evidence", rows[3]["error"])

    def test_missing_or_truthy_non_boolean_outcomes_fail_closed(self):
        for bad in (None, True, {"ok": True}, PhaseResult(1, "not bool")):
            with self.subTest(bad=bad):
                validated = []
                rows = run_jobs([0], lambda job: bad, lambda *args: validated.append(args))
                self.assertEqual("engine_failed", rows[0]["status"])
                self.assertEqual([], validated)
                rows = run_jobs([0], lambda job: PhaseResult(True), lambda *args: bad)
                self.assertEqual("validation_failed", rows[0]["status"])
                self.assertFalse(rows[0]["accepted"])

    def test_cancellation_cleans_running_callbacks_and_launches_no_more_jobs(self):
        cancel, started, released = Event(), Event(), Event()
        engine_calls, cleanup_calls, validations = [], [], []

        def engine(job):
            engine_calls.append(job)
            started.set()
            self.assertTrue(released.wait(2))
            return PhaseResult(True, job)

        def cleanup():
            cleanup_calls.append(True)
            released.set()  # Process adapters stop/reap their groups here.

        with ThreadPoolExecutor(max_workers=1) as caller:
            future = caller.submit(run_jobs, range(6), engine, lambda *args: validations.append(args),
                                   max_workers=1, cancel_event=cancel, cancel_running=cleanup)
            self.assertTrue(started.wait(2))
            cancel.set()
            rows = future.result(timeout=2)
        self.assertEqual([0], engine_calls)
        self.assertEqual([True], cleanup_calls)
        self.assertEqual([], validations)
        self.assertEqual(["cancelled"] * 6, [row["status"] for row in rows])

    def test_cancelled_validation_never_accepts_late_success(self):
        cancel, validating, release = Event(), Event(), Event()
        def validate(job, value):
            validating.set()
            self.assertTrue(release.wait(2))
            return PhaseResult(True)
        with ThreadPoolExecutor(max_workers=1) as caller:
            future = caller.submit(run_jobs, [1], lambda job: PhaseResult(True), validate,
                                   cancel_event=cancel, cancel_running=release.set)
            self.assertTrue(validating.wait(2))
            cancel.set()
            rows = future.result(timeout=2)
        self.assertEqual("cancelled", rows[0]["status"])
        self.assertFalse(rows[0]["accepted"])

    def test_keyboard_interrupt_cleans_active_callbacks_before_propagating(self):
        companion_started, release = Event(), Event()
        cancel, cleaned = Event(), []
        def engine(job):
            if job == 0:
                self.assertTrue(companion_started.wait(2))
                raise KeyboardInterrupt("cancel test")
            companion_started.set()
            self.assertTrue(release.wait(2))
            return PhaseResult(True)
        def cleanup():
            cleaned.append(True)
            release.set()
        with self.assertRaises(KeyboardInterrupt):
            run_jobs([0, 1], engine, lambda *args: PhaseResult(True), max_workers=2,
                     cancel_event=cancel, cancel_running=cleanup)
        self.assertTrue(cancel.is_set())
        self.assertEqual([True], cleaned)

    def test_pre_cancelled_jobs_and_empty_input_never_run(self):
        cancel = Event()
        cancel.set()
        def forbidden(*args):
            self.fail("Callback must not run")
        self.assertEqual([], run_jobs([], forbidden, forbidden))
        rows = run_jobs([0, 1], forbidden, forbidden, cancel_event=cancel)
        self.assertEqual(["cancelled", "cancelled"], [row["status"] for row in rows])

    def test_invalid_worker_count_rejected_before_callbacks(self):
        for count in (0, -1, True, 1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                run_jobs([1], lambda job: PhaseResult(True), lambda *args: PhaseResult(True), max_workers=count)


if __name__ == "__main__":
    unittest.main()
