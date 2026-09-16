"""Bounded parallel engines feeding one independent validation worker.

Callbacks return PhaseResult. Validation receives the successful engine's
``value``; only a successful validation marks a job accepted. Result dictionaries
retain input order, while validation starts in completion order. Each job must
construct its own cold inputs; this coordinator never reuses candidate copper.

Callbacks must bound their own work and honor a shared cancellation Event.
Subprocess adapters must use thread-safe process handling, not the benchmark's
signal-installing execute(). Supply cancel_running to stop/reap their registered
process groups on cancellation. Each adapter must also clean up its own child
processes on a phase error. Python cannot forcibly stop callback threads.
"""
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from threading import Event
from typing import Any


@dataclass(frozen=True)
class PhaseResult:
    ok: bool
    value: Any = None


def run_jobs(jobs, engine_phase, validation_phase, *, max_workers=6,
             cancel_event=None, cancel_running=None):
    """Run a finite iterable once; return input-ordered per-job result dicts.

    Statuses: accepted, engine_failed, validation_failed, cancelled. A callback
    exception fails just that job; a malformed/missing PhaseResult fails closed.
    Cancellation stops scheduling, calls cancel_running once, and drains active
    callbacks before returning. KeyboardInterrupt also cleans up, then propagates.
    ``accepted`` is the caller's validation result, not production qualification.
    """
    if type(max_workers) is not int or max_workers < 1:
        raise ValueError("max_workers must be a positive integer")
    if not callable(engine_phase) or not callable(validation_phase):
        raise TypeError("Both phases must be callable")
    if cancel_running is not None and not callable(cancel_running):
        raise TypeError("cancel_running must be callable")
    jobs = tuple(jobs)
    results = [{"index": i, "job": job, "status": "pending", "accepted": False,
                "engine": None, "validation": None, "error": None} for i, job in enumerate(jobs)]
    cancel = cancel_event if cancel_event is not None else Event()
    engines = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="routing-engine")
    validator = ThreadPoolExecutor(max_workers=1, thread_name_prefix="routing-validation")
    pending, ready, validating = {}, deque(), None
    next_job, cancellation_handled = 0, False

    def stop():
        nonlocal cancellation_handled
        if cancellation_handled:
            return
        cancellation_handled = True
        cancel.set()
        for row in results:
            if row["status"] in {"pending", "engine_running", "awaiting_validation", "validating"}:
                row.update(status="cancelled", accepted=False)
        for future in pending:
            future.cancel()
        if validating is not None:
            validating[0].cancel()
        if cancel_running is not None:
            cancel_running()

    def finish(future, index, phase):
        row = results[index]
        try:
            outcome = future.result()
            if not isinstance(outcome, PhaseResult) or type(outcome.ok) is not bool:
                raise TypeError("Callback must return PhaseResult with a boolean ok")
            row[phase] = outcome.value
            if not outcome.ok:
                row["status"] = phase + "_failed"
            elif phase == "engine":
                row["status"] = "awaiting_validation"
                ready.append(index)
            else:
                row.update(status="accepted", accepted=True)
        except Exception as exc:
            row.update(status=phase + "_failed", error=f"{type(exc).__name__}: {exc}")

    try:
        while next_job < len(jobs) or pending or ready or validating is not None:
            if cancel.is_set():
                stop()
                break
            # Refill engines first. Neither queued nor active validation owns
            # an engine slot, including a validator blocked on a native lock.
            while next_job < len(jobs) and len(pending) < max_workers and not cancel.is_set():
                index = next_job
                next_job += 1
                results[index]["status"] = "engine_running"
                pending[engines.submit(engine_phase, jobs[index])] = index
            if validating is None and ready and not cancel.is_set():
                index = ready.popleft()
                results[index]["status"] = "validating"
                validating = (validator.submit(validation_phase, jobs[index], results[index]["engine"]), index)
            futures = set(pending)
            if validating is not None:
                futures.add(validating[0])
            if not futures:
                continue
            completed, _ = wait(futures, timeout=0.05, return_when=FIRST_COMPLETED)
            # Do not credit results that arrive after cancellation was requested.
            if cancel.is_set():
                continue
            for future in sorted(completed & pending.keys(), key=pending.__getitem__):
                finish(future, pending.pop(future), "engine")
            if validating is not None and validating[0] in completed:
                finish(*validating, "validation")
                validating = None
    except BaseException:
        stop()
        raise
    finally:
        engines.shutdown(wait=True, cancel_futures=True)
        validator.shutdown(wait=True, cancel_futures=True)
    return results
